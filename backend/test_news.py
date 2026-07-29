import pytest
import pytest_asyncio
import uuid
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.models.schema import User, BookmarkedArticle
from app.api.news import get_db
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
            email="news_test@example.com",
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
async def test_1_get_market_news(client: AsyncClient):
    response = await client.get("/news/market")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "title" in data[0]
        assert "url" in data[0]

@pytest.mark.asyncio
async def test_2_get_company_news(client: AsyncClient):
    response = await client.get("/news/company/AAPL")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_3_bookmarks_crud(client: AsyncClient, test_user_id: str):
    # Add Bookmark
    response = await client.post("/news/bookmarks", json={
        "user_id": test_user_id,
        "article_url": "https://example.com/news",
        "article_title": "Test Article",
        "source": "Testing",
        "published_at": "2026-01-01T00:00:00Z"
    })
    assert response.status_code == 200
    bookmark = response.json()
    assert bookmark["article_title"] == "Test Article"
    bookmark_id = bookmark["id"]
    
    # Get Bookmarks
    response = await client.get(f"/news/bookmarks/{test_user_id}")
    assert response.status_code == 200
    bookmarks = response.json()
    assert len(bookmarks) > 0
    assert any(b["id"] == bookmark_id for b in bookmarks)
    
    # Delete Bookmark
    response = await client.delete(f"/news/bookmarks/{bookmark_id}")
    assert response.status_code == 200
    
    # Verify Deletion
    response = await client.get(f"/news/bookmarks/{test_user_id}")
    bookmarks = response.json()
    assert not any(b["id"] == bookmark_id for b in bookmarks)
