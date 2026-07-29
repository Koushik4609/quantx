import pytest
import pytest_asyncio
import uuid
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.models.schema import User, Portfolio, Order, Position, Transaction
from app.api.trading import get_db

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(scope="module")
async def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(User.__table__.create)
        await conn.run_sync(Portfolio.__table__.create)
        await conn.run_sync(Order.__table__.create)
        await conn.run_sync(Position.__table__.create)
        await conn.run_sync(Transaction.__table__.create)
    async with TestingSessionLocal() as session:
        user = User(email="trader@quantx.ai", password_hash="secret")
        session.add(user)
        await session.flush()
        portfolio = Portfolio(user_id=user.id, name="Paper Trading", cash_balance=10000.0)
        session.add(portfolio)
        await session.commit()
        await session.refresh(portfolio)
        pytest.portfolio_id = str(portfolio.id)
    yield

@pytest_asyncio.fixture(scope="module")
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_1_buy_aapl_150(async_client):
    req = {
        "portfolio_id": pytest.portfolio_id,
        "symbol": "AAPL",
        "quantity": 10.0,
        "price": 150.0
    }
    response = await async_client.post("/trading/buy", json=req)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

@pytest.mark.asyncio
async def test_2_buy_aapl_170(async_client):
    req = {
        "portfolio_id": pytest.portfolio_id,
        "symbol": "AAPL",
        "quantity": 10.0,
        "price": 170.0
    }
    response = await async_client.post("/trading/buy", json=req)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_3_verify_portfolio_unrealized(async_client):
    req = {
        "portfolio_id": pytest.portfolio_id,
        "current_prices": {"AAPL": 180.0}
    }
    response = await async_client.post("/trading/portfolio", json=req)
    assert response.status_code == 200
    data = response.json()
    
    assert data["cash_balance"] == 10000.0 - 1500.0 - 1700.0 # 6800.0
    
    positions = data["positions"]
    assert len(positions) == 1
    p = positions[0]
    
    assert p["quantity"] == 20.0
    assert p["average_cost"] == 160.0 # (1500+1700)/20
    assert p["unrealized_pnl"] == 400.0 # 20 * (180 - 160)
    
    assert data["total_equity"] == 6800.0 + (20.0 * 180.0) # 10400.0

@pytest.mark.asyncio
async def test_4_sell_aapl_180(async_client):
    req = {
        "portfolio_id": pytest.portfolio_id,
        "symbol": "AAPL",
        "quantity": 10.0,
        "price": 180.0
    }
    response = await async_client.post("/trading/sell", json=req)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_5_verify_portfolio_realized(async_client):
    req = {
        "portfolio_id": pytest.portfolio_id,
        "current_prices": {"AAPL": 180.0}
    }
    response = await async_client.post("/trading/portfolio", json=req)
    assert response.status_code == 200
    data = response.json()
    
    assert data["cash_balance"] == 6800.0 + 1800.0 # 8600.0
    
    positions = data["positions"]
    assert len(positions) == 1
    p = positions[0]
    
    assert p["quantity"] == 10.0
    assert p["average_cost"] == 160.0 # Unchanged
    
    assert data["total_realized_pnl"] == 200.0

@pytest.mark.asyncio
async def test_6_transaction_history(async_client):
    response = await async_client.get(f"/trading/transactions/{pytest.portfolio_id}")
    assert response.status_code == 200
    txs = response.json()
    
    assert len(txs) == 3
    
    types = [t["transaction_type"] for t in txs]
    assert types.count("SELL") == 1
    assert types.count("BUY") == 2
    
    amounts = [t["amount"] for t in txs]
    assert 1800.0 in amounts
    assert -1700.0 in amounts
    assert -1500.0 in amounts
