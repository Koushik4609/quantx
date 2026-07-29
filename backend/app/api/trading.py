import uuid
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.trading import TradeRequest, PortfolioSummary, TransactionSchema
from app.services.trading_engine import TradingEngine

# Mock DB dependency to be overridden in tests
async def get_db() -> AsyncSession:
    raise NotImplementedError("Database dependency not overridden")

router = APIRouter(prefix="/trading", tags=["trading"])

@router.post("/buy")
async def buy(request: TradeRequest, session: AsyncSession = Depends(get_db)):
    try:
        order = await TradingEngine.execute_buy(session, request.portfolio_id, request.symbol, request.quantity, request.price)
        await session.commit()
        return {"status": "success", "order_id": order.id, "message": f"Bought {request.quantity} {request.symbol}"}
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sell")
async def sell(request: TradeRequest, session: AsyncSession = Depends(get_db)):
    try:
        order = await TradingEngine.execute_sell(session, request.portfolio_id, request.symbol, request.quantity, request.price)
        await session.commit()
        return {"status": "success", "order_id": order.id, "message": f"Sold {request.quantity} {request.symbol}"}
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/portfolio", response_model=PortfolioSummary)
async def get_portfolio(
    portfolio_id: uuid.UUID = Body(...),
    current_prices: Dict[str, float] = Body(default_factory=dict),
    session: AsyncSession = Depends(get_db)
):
    """
    Pass current_prices to calculate real-time unrealized PnL.
    E.g. {"AAPL": 155.0}
    """
    try:
        return await TradingEngine.get_portfolio_summary(session, portfolio_id, current_prices)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/transactions/{portfolio_id}", response_model=List[TransactionSchema])
async def get_transactions(portfolio_id: uuid.UUID, session: AsyncSession = Depends(get_db)):
    return await TradingEngine.get_transaction_history(session, portfolio_id)
