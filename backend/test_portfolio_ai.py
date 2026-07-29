import pytest
import pytest_asyncio
import uuid
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.models.schema import User, Position
from app.api.portfolio_ai import get_db
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
            email=f"portai_test_{user_id}@example.com",
            password_hash="hash"
        )
        session.add(user)
        await session.commit()
        
        # Create Portfolio
        from app.models.schema import Portfolio
        port = Portfolio(user_id=user_id, name="Test", total_value=100000.0, cash_balance=100000.0)
        session.add(port)
        await session.commit()
        await session.refresh(port)
        
        # Add some mock positions
        p1 = Position(portfolio_id=port.id, symbol="AAPL", quantity=10, average_price=150.0)
        p2 = Position(portfolio_id=port.id, symbol="MSFT", quantity=5, average_price=300.0)
        session.add_all([p1, p2])
        await session.commit()
    return str(user_id)

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_portfolio_intelligence(client: AsyncClient, test_user_id: str):
    response = await client.get(f"/portfolio/intelligence/?user_id={test_user_id}")
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert "diversification_score" in data
    assert "risk_score" in data
    assert "volatility" in data
    assert "sector_allocation" in data
    assert "ai_analysis" in data
