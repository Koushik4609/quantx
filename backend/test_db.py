from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import app
import os
from dotenv import load_dotenv

load_dotenv()
engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

# Note: Need to import all routers that use get_db to override them
from app.api.auth import get_db as get_db_auth
from app.api.trading import get_db as get_db_trading
from app.api.strategy import get_db as get_db_strategy
from app.api.news import get_db as get_db_news
from app.api.learning import get_db as get_db_learning
from app.api.portfolio_ai import get_db as get_db_portfolio_ai
from app.api.ai import get_db as get_db_ai

app.dependency_overrides[get_db_auth] = override_get_db
app.dependency_overrides[get_db_trading] = override_get_db
app.dependency_overrides[get_db_strategy] = override_get_db
app.dependency_overrides[get_db_news] = override_get_db
app.dependency_overrides[get_db_learning] = override_get_db
app.dependency_overrides[get_db_portfolio_ai] = override_get_db
app.dependency_overrides[get_db_ai] = override_get_db

