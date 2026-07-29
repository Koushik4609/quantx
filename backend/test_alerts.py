import pytest
import pytest_asyncio
import uuid
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.models.schema import User, Alert
from app.api.alerts import get_db
from app.models.base import Base

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

from app.core.auth import get_current_user

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
            email=f"alerts_test_{user_id}@example.com",
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
async def test_alerts_crud(client: AsyncClient, test_user_id: str):
    # override for this test
    async def override_auth():
        return User(id=uuid.UUID(test_user_id), email="test@example.com")
    app.dependency_overrides[get_current_user] = override_auth

    # Create Alert
    response = await client.post(f"/alerts/?user_id={test_user_id}", json={
        "symbol": "AAPL",
        "alert_type": "PRICE",
        "condition": "ABOVE",
        "value": 150.0
    })
    assert response.status_code == 200
    alert_id = response.json()["id"]
    
    # Get Alerts
    response = await client.get(f"/alerts/?user_id={test_user_id}")
    assert response.status_code == 200
    alerts = response.json()
    assert len(alerts) == 1
    assert alerts[0]["symbol"] == "AAPL"
    
    # Delete Alert
    response = await client.delete(f"/alerts/{alert_id}?user_id={test_user_id}")
    assert response.status_code == 200
    
    response = await client.get(f"/alerts/?user_id={test_user_id}")
    assert len(response.json()) == 0
