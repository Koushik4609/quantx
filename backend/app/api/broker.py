import uuid
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.schema import BrokerIntegration, User
from app.services.upstox_client import UpstoxClient
from app.core.auth import get_current_user

router = APIRouter(prefix="/broker", tags=["broker"])

async def get_db() -> AsyncSession:
    raise NotImplementedError()

async def get_broker_integration(user_id: uuid.UUID, session: AsyncSession) -> BrokerIntegration:
    stmt = select(BrokerIntegration).where(BrokerIntegration.user_id == user_id, BrokerIntegration.broker_name == "UPSTOX")
    res = await session.execute(stmt)
    bi = res.scalar_one_or_none()
    if not bi:
        raise HTTPException(status_code=404, detail="Broker not connected")
    return bi

@router.get("/upstox/login-url")
async def get_upstox_login_url():
    client = UpstoxClient()
    return {"url": client.get_login_url()}

@router.post("/upstox/callback")
async def upstox_callback(
    code: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    try:
        client = UpstoxClient()
        token_data = await client.exchange_token(code)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to retrieve access token")
            
        # Check if already connected
        stmt = select(BrokerIntegration).where(BrokerIntegration.user_id == current_user.get("uid"), BrokerIntegration.broker_name == "UPSTOX")
        res = await session.execute(stmt)
        bi = res.scalar_one_or_none()
        
        if bi:
            bi.access_token = access_token
        else:
            bi = BrokerIntegration(
                user_id=current_user.get("uid"),
                broker_name="UPSTOX",
                access_token=access_token
            )
            session.add(bi)
            
        await session.commit()
        return {"status": "success", "message": "Upstox connected successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_broker_status(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(BrokerIntegration).where(BrokerIntegration.user_id == current_user.get("uid"), BrokerIntegration.broker_name == "UPSTOX")
    res = await session.execute(stmt)
    bi = res.scalar_one_or_none()
    return {"connected": bi is not None}

@router.get("/profile")
async def get_broker_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    bi = await get_broker_integration(current_user.get("uid"), session)
    client = UpstoxClient(access_token=bi.access_token)
    try:
        return await client.get_profile()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/funds")
async def get_broker_funds(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    bi = await get_broker_integration(current_user.get("uid"), session)
    client = UpstoxClient(access_token=bi.access_token)
    try:
        return await client.get_funds()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/holdings")
async def get_broker_holdings(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    bi = await get_broker_integration(current_user.get("uid"), session)
    client = UpstoxClient(access_token=bi.access_token)
    try:
        return await client.get_holdings()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/orders")
async def get_broker_orders(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    bi = await get_broker_integration(current_user.get("uid"), session)
    client = UpstoxClient(access_token=bi.access_token)
    try:
        return await client.get_orders()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
