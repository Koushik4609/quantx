import pytest
import pytest_asyncio
import uuid
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.models.schema import User, Portfolio, Order, Position, Transaction, AIChatHistory
from app.api.ai import get_db

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db
# Also override trading dependency because AI uses it internally? No, AI service passes session explicitly.

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
        await conn.run_sync(AIChatHistory.__table__.create)
    async with TestingSessionLocal() as session:
        user = User(email="ai_trader@quantx.ai", password_hash="secret")
        session.add(user)
        await session.flush()
        portfolio = Portfolio(user_id=user.id, name="Paper Trading", cash_balance=10000.0)
        session.add(portfolio)
        await session.flush()
        
        # Give some dummy position for testing
        position = Position(portfolio_id=portfolio.id, symbol="AAPL", quantity=10.0, average_price=150.0)
        session.add(position)
        
        await session.commit()
        await session.refresh(user)
        await session.refresh(portfolio)
        pytest.user_id = str(user.id)
        pytest.portfolio_id = str(portfolio.id)
    yield

@pytest_asyncio.fixture(scope="module")
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_1_ai_chat_with_ticker(async_client):
    req = {
        "user_id": pytest.user_id,
        "portfolio_id": pytest.portfolio_id,
        "message": "Should I sell my AAPL shares?"
    }
    response = await async_client.post("/ai/chat", json=req)
    assert response.status_code == 200
    data = response.json()
    
    # Should run in stub mode and extract AAPL
    assert "AAPL" in data["tool_calls_made"][0]
    
    # Assert offline stub mode response
    assert "SYSTEM CONFIGURATION ERROR" in data["response"]
    
    # Assert portfolio context was injected
    assert "10.0 shares of AAPL" in data["response"]
    assert "Cash Balance: $10000.00" in data["response"]

@pytest.mark.asyncio
async def test_2_ai_chat_without_ticker(async_client):
    req = {
        "user_id": pytest.user_id,
        "portfolio_id": pytest.portfolio_id,
        "message": "What is my total balance?"
    }
    response = await async_client.post("/ai/chat", json=req)
    assert response.status_code == 200
    data = response.json()
    
    # Should NOT have market data tool call
    for call in data["tool_calls_made"]:
        assert "Fetched Market Data" not in call
    
    # Should still have portfolio context
    assert "Cash Balance: $10000.00" in data["response"]

@pytest.mark.asyncio
async def test_3_ai_chat_history(async_client):
    response = await async_client.get(f"/ai/history/{pytest.user_id}")
    assert response.status_code == 200
    histories = response.json()
    
    # 2 calls = 4 messages (2 user, 2 assistant)
    assert len(histories) == 4
    assert histories[0]["message_role"] == "user"
    assert histories[0]["content"] == "Should I sell my AAPL shares?"
    assert histories[1]["message_role"] == "assistant"
    assert "SYSTEM CONFIGURATION ERROR" in histories[1]["content"]
