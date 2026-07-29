import pytest
import pytest_asyncio
import uuid
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.models.schema import User, BrokerIntegration
from app.api.broker import get_db
from app.models.base import Base
from app.core.auth import get_current_user

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

# We will patch this fixture later per-test
async def override_get_current_user():
    return User(id=uuid.uuid4(), email="test@example.com")

app.dependency_overrides[get_current_user] = override_get_current_user
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
            email=f"broker_test_{user_id}@example.com",
            password_hash="hash"
        )
        session.add(user)
        
        # Add mock integration
        bi = BrokerIntegration(
            user_id=user_id,
            broker_name="UPSTOX",
            access_token="mock_token"
        )
        session.add(bi)
        await session.commit()
    return str(user_id)

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_broker_status(client: AsyncClient, test_user_id: str):
    async def override_auth():
        return User(id=uuid.UUID(test_user_id), email="test@example.com")
    app.dependency_overrides[get_current_user] = override_auth
    
    response = await client.get("/broker/status")
    assert response.status_code == 200
    assert response.json() == {"connected": True}

@pytest.mark.asyncio
async def test_broker_login_url(client: AsyncClient):
    response = await client.get("/broker/upstox/login-url")
    assert response.status_code == 200
    assert "api.upstox.com" in response.json()["url"]
