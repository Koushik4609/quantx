import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.schema import Strategy, BacktestResult
from app.schemas.strategy import StrategyCreate, StrategyResponse, BacktestResultResponse
from app.services.backtester import Backtester

router = APIRouter(prefix="/strategy", tags=["strategy"])

# Mock DB dependency
async def get_db() -> AsyncSession:
    raise NotImplementedError("Database dependency not overridden")

@router.get("/", response_model=List[StrategyResponse])
async def get_strategies(user_id: uuid.UUID, session: AsyncSession = Depends(get_db)):
    try:
        stmt = select(Strategy).where(Strategy.user_id == user_id)
        result = await session.execute(stmt)
        strategies = result.scalars().all()
        return strategies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=StrategyResponse)
async def create_strategy(strategy: StrategyCreate, session: AsyncSession = Depends(get_db)):
    try:
        new_strategy = Strategy(
            user_id=strategy.user_id,
            name=strategy.name,
            symbol=strategy.symbol,
            timeframe=strategy.timeframe,
            conditions=strategy.conditions.model_dump()
        )
        session.add(new_strategy)
        await session.commit()
        await session.refresh(new_strategy)
        return new_strategy
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{strategy_id}")
async def delete_strategy(strategy_id: uuid.UUID, session: AsyncSession = Depends(get_db)):
    try:
        stmt = select(Strategy).where(Strategy.id == strategy_id)
        result = await session.execute(stmt)
        strategy = result.scalar_one_or_none()
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
            
        await session.delete(strategy)
        await session.commit()
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{strategy_id}/backtest", response_model=BacktestResultResponse)
async def run_backtest(strategy_id: uuid.UUID, session: AsyncSession = Depends(get_db)):
    try:
        stmt = select(Strategy).where(Strategy.id == strategy_id)
        result = await session.execute(stmt)
        strategy = result.scalar_one_or_none()
        
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
            
        # Run Backtester
        engine = Backtester(symbol=strategy.symbol, timeframe=strategy.timeframe)
        results = engine.run(strategy.conditions)
        
        # Save Results
        bt_result = BacktestResult(
            strategy_id=strategy.id,
            total_return=results["total_return"],
            win_rate=results["win_rate"],
            max_drawdown=results["max_drawdown"],
            trades=results["trades"]
        )
        session.add(bt_result)
        await session.commit()
        await session.refresh(bt_result)
        
        return bt_result
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{strategy_id}/backtests", response_model=List[BacktestResultResponse])
async def get_backtests(strategy_id: uuid.UUID, session: AsyncSession = Depends(get_db)):
    try:
        stmt = select(BacktestResult).where(BacktestResult.strategy_id == strategy_id).order_by(BacktestResult.created_at.desc())
        result = await session.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
