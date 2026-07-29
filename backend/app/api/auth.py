import os
import httpx
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.auth import UserCredentials, TokenResponse
from app.core.auth import get_current_user
from app.models.schema import User, Portfolio
import uuid

# Mock DB dependency to be overridden in tests/main
async def get_db() -> AsyncSession:
    raise NotImplementedError("Database dependency not overridden")

router = APIRouter(prefix="/auth", tags=["auth"])

FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY", "fake-api-key")
EMULATOR_HOST = os.environ.get("FIREBASE_AUTH_EMULATOR_HOST")

if EMULATOR_HOST:
    SIGNUP_URL = f"http://{EMULATOR_HOST}/identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
    LOGIN_URL = f"http://{EMULATOR_HOST}/identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
else:
    SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
    LOGIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"

@router.post("/signup", response_model=TokenResponse)
async def signup(credentials: UserCredentials):
    if not FIREBASE_API_KEY or FIREBASE_API_KEY == "fake-api-key":
        # Dev mode mock
        return {"idToken": "dev-mock-token", "refreshToken": "dev-mock-refresh", "expiresIn": "3600", "localId": "00000000-0000-0000-0000-000000000000", "email": credentials.email}

    payload = {
        "email": credentials.email,
        "password": credentials.password,
        "returnSecureToken": True
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(SIGNUP_URL, json=payload)
        
    if response.status_code != 200:
        error_data = response.json().get("error", {})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_data.get("message", "Signup failed")
        )
        
    return response.json()

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserCredentials):
    if not FIREBASE_API_KEY or FIREBASE_API_KEY == "fake-api-key":
        # Dev mode mock
        return {"idToken": "dev-mock-token", "refreshToken": "dev-mock-refresh", "expiresIn": "3600", "localId": "00000000-0000-0000-0000-000000000000", "email": credentials.email}

    payload = {
        "email": credentials.email,
        "password": credentials.password,
        "returnSecureToken": True
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(LOGIN_URL, json=payload)
        
    if response.status_code != 200:
        error_data = response.json().get("error", {})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_data.get("message", "Login failed")
        )
        
    return response.json()

@router.get("/me")
async def get_me(user_info: dict = Depends(get_current_user), session: AsyncSession = Depends(get_db)):
    email = user_info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token: no email")
        
    # Check if user exists in PG
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        user = User(email=email, password_hash="firebase_managed")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
    # Check if portfolio exists
    stmt = select(Portfolio).where(Portfolio.user_id == user.id)
    result = await session.execute(stmt)
    portfolio = result.scalars().first()
    
    if not portfolio:
        portfolio = Portfolio(
            user_id=user.id,
            name="Main Portfolio",
            total_value=100000.0, # Default Paper Trading Cash
            cash_balance=100000.0
        )
        session.add(portfolio)
        await session.commit()
        await session.refresh(portfolio)
        
    return {
        "user_id": str(user.id),
        "email": user.email,
        "portfolio_id": str(portfolio.id)
    }
