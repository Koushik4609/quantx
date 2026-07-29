import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.ai import ChatRequest, ChatResponse, ChatHistorySchema
from app.services.ai_agent import FinancialAssistant
from app.models.schema import AIChatHistory

# Mock DB dependency to be overridden in tests
async def get_db() -> AsyncSession:
    raise NotImplementedError("Database dependency not overridden")

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, session: AsyncSession = Depends(get_db)):
    try:
        response = await FinancialAssistant.generate_response(
            session=session,
            user_id=request.user_id,
            portfolio_id=request.portfolio_id,
            message=request.message
        )
        await session.commit()
        return response
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{user_id}", response_model=List[ChatHistorySchema])
async def get_history(user_id: uuid.UUID, session: AsyncSession = Depends(get_db)):
    try:
        stmt = select(AIChatHistory).where(AIChatHistory.user_id == user_id).order_by(AIChatHistory.created_at.asc())
        result = await session.execute(stmt)
        histories = result.scalars().all()
        return histories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolio-health/{portfolio_id}")
async def get_portfolio_health(portfolio_id: uuid.UUID, session: AsyncSession = Depends(get_db)):
    try:
        return await FinancialAssistant.get_portfolio_health(session, portfolio_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/daily-brief")
async def get_daily_brief():
    try:
        return await FinancialAssistant.get_daily_brief()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
