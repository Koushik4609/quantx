import pytest
import pytest_asyncio
import uuid
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.models.schema import User, Course, Lesson, Quiz
from app.api.learning import get_db
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
    
    # Seed data
    async with TestingSessionLocal() as session:
        c = Course(title="Test Course", description="Test", level="Beginner")
        session.add(c)
        await session.flush()
        
        l = Lesson(course_id=c.id, title="Test Lesson", content="Content", order=1)
        session.add(l)
        await session.flush()
        
        q = Quiz(lesson_id=l.id, question="Q1", options=["A", "B"], correct_option_index=0)
        session.add(q)
        
        await session.commit()
    
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def test_user_id():
    user_id = uuid.uuid4()
    async with TestingSessionLocal() as session:
        user = User(
            id=user_id,
            email=f"learning_test_{user_id}@example.com",
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
async def test_get_courses(client: AsyncClient):
    response = await client.get("/learning/courses")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert courses[0]["title"] == "Test Course"
    assert len(courses[0]["lessons"]) > 0
    assert len(courses[0]["lessons"][0]["quizzes"]) > 0

@pytest.mark.asyncio
async def test_user_progress(client: AsyncClient, test_user_id: str):
    # Get courses to get a lesson_id
    courses_resp = await client.get("/learning/courses")
    lesson_id = courses_resp.json()[0]["lessons"][0]["id"]
    
    # Update progress
    response = await client.post("/learning/progress", json={
        "user_id": test_user_id,
        "lesson_id": lesson_id,
        "score": 100
    })
    assert response.status_code == 200
    
    # Get progress
    response = await client.get(f"/learning/progress/{test_user_id}")
    assert response.status_code == 200
    progress = response.json()
    assert len(progress) == 1
    assert progress[0]["lesson_id"] == lesson_id
    assert progress[0]["completed"] is True
    assert progress[0]["score"] == 100
