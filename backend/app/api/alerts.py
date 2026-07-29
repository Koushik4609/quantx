import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.schema import Alert, User
from app.schemas.alerts import AlertCreate, AlertResponse
from app.core.auth import get_current_user

router = APIRouter(prefix="/alerts", tags=["alerts"])

# Mock DB dependency - must be overridden in main
async def get_db() -> AsyncSession:
    raise NotImplementedError("Database dependency not overridden")

@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    current_user: User = Depends(get_current_user), 
    session: AsyncSession = Depends(get_db)
):
    stmt = select(Alert).where(Alert.user_id == current_user.get("uid")).order_by(Alert.created_at.desc())
    result = await session.execute(stmt)
    alerts = result.scalars().all()
    return alerts

@router.post("/", response_model=AlertResponse)
async def create_alert(
    alert: AlertCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    db_alert = Alert(
        user_id=current_user.get("uid"),
        symbol=alert.symbol.upper() if alert.symbol else None,
        alert_type=alert.alert_type.upper(),
        condition=alert.condition.upper(),
        value=alert.value,
        status="ACTIVE"
    )
    session.add(db_alert)
    await session.commit()
    await session.refresh(db_alert)
    return db_alert

@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(Alert).where(Alert.id == alert_id, Alert.user_id == current_user.get("uid"))
    result = await session.execute(stmt)
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    await session.delete(alert)
    await session.commit()
    return {"status": "deleted"}
