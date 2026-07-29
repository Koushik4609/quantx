import pytest
import pytest_asyncio
import uuid
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.models.schema import User, Strategy, BacktestResult
from app.api.strategy import get_db
from app.models.base import Base

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def test_user_id():
    user_id = uuid.uuid4()
    async with TestingSessionLocal() as session:
        user = User(
            id=user_id,
            email=f"strategy_test_{user_id}@example.com",
            password_hash="hash"
        )
        session.add(user)
        await session.commit()
    return str(user_id)

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_strategy_crud_and_backtest(client: AsyncClient, test_user_id: str):
    # 1. Create
    create_resp = await client.post("/strategy/", json={
        "user_id": test_user_id,
        "name": "RSI Bounce",
        "symbol": "AAPL",
        "timeframe": "1d",
        "conditions": {
            "entry": [{"indicator": "RSI", "operator": "<", "value": 30.0, "timeperiod": 14}],
            "exit": [{"indicator": "RSI", "operator": ">", "value": 70.0, "timeperiod": 14}]
        }
    })
    assert create_resp.status_code == 200
    strategy = create_resp.json()
    assert strategy["name"] == "RSI Bounce"
    strategy_id = strategy["id"]
    
    # 2. Read
    get_resp = await client.get(f"/strategy/?user_id={test_user_id}")
    assert get_resp.status_code == 200
    strats = get_resp.json()
    assert len(strats) == 1
    
    # 3. Backtest
    # This calls yfinance and ta, so it may take a second
    bt_resp = await client.post(f"/strategy/{strategy_id}/backtest")
    assert bt_resp.status_code == 200
    bt_result = bt_resp.json()
    assert "total_return" in bt_result
    assert "win_rate" in bt_result
    
    # 4. Get Backtests
    bts_resp = await client.get(f"/strategy/{strategy_id}/backtests")
    assert bts_resp.status_code == 200
    assert len(bts_resp.json()) == 1
    
    # 5. Delete
    del_resp = await client.delete(f"/strategy/{strategy_id}")
    assert del_resp.status_code == 200
    
    # 6. Verify Deletion
    get_resp2 = await client.get(f"/strategy/?user_id={test_user_id}")
    assert len(get_resp2.json()) == 0
