import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.core.db import init_db, get_db as real_get_db
from app.api import auth as auth_router
from app.api import market as market_router
from app.api import trading as trading_router
from app.api import ai as ai_router
from app.api import news as news_router
from app.api import learning as learning_router
from app.api import analytics as analytics_router
from app.api import strategy as strategy_router
from app.api import portfolio_ai as portfolio_ai_router
from app.api import alerts as alerts_router
from app.api import broker as broker_router
from app.api import company as company_router
from app.core.auth import get_current_user
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="QuantX AI API", lifespan=lifespan)

# Setup Dependency Overrides for the DB
app.dependency_overrides[auth_router.get_db] = real_get_db
app.dependency_overrides[trading_router.get_db] = real_get_db
app.dependency_overrides[ai_router.get_db] = real_get_db
app.dependency_overrides[news_router.get_db] = real_get_db
app.dependency_overrides[learning_router.get_db] = real_get_db
app.dependency_overrides[strategy_router.get_db] = real_get_db
app.dependency_overrides[portfolio_ai_router.get_db] = real_get_db
app.dependency_overrides[alerts_router.get_db] = real_get_db
app.dependency_overrides[broker_router.get_db] = real_get_db

FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY", "fake-api-key")
if not FIREBASE_API_KEY or FIREBASE_API_KEY == "fake-api-key":
    async def mock_get_current_user():
        return {"uid": "00000000-0000-0000-0000-000000000000", "email": "trader@quantx.ai"}
    app.dependency_overrides[get_current_user] = mock_get_current_user

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(market_router.router)
app.include_router(trading_router.router)
app.include_router(ai_router.router)
app.include_router(news_router.router)
app.include_router(learning_router.router)
app.include_router(analytics_router.router)
app.include_router(strategy_router.router)
app.include_router(portfolio_ai_router.router)
app.include_router(alerts_router.router)
app.include_router(broker_router.router)
app.include_router(company_router.router)

@app.get("/")
def root():
    return {"message": "QuantX AI API"}

@app.get("/protected")
def protected_route(user: dict = Depends(get_current_user)):
    """
    A protected route that requires a valid Firebase JWT token.
    """
    return {
        "message": "You have access to this protected route!",
        "user_id": user.get("uid"),
        "email": user.get("email")
    }
