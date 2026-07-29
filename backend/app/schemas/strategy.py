from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid

class StrategyCondition(BaseModel):
    indicator: str # e.g. "RSI", "MACD", "EMA"
    operator: str  # e.g. ">", "<", "=="
    value: float
    timeperiod: Optional[int] = 14

class StrategyConditions(BaseModel):
    entry: List[StrategyCondition]
    exit: List[StrategyCondition]

class StrategyCreate(BaseModel):
    user_id: uuid.UUID
    name: str
    symbol: str
    timeframe: str
    conditions: StrategyConditions

class StrategyResponse(BaseModel):
    id: uuid.UUID
    name: str
    symbol: str
    timeframe: str
    conditions: dict
    
    class Config:
        from_attributes = True

class TradeResult(BaseModel):
    type: str # Buy / Sell
    date: str
    price: float
    shares: int

class BacktestResultResponse(BaseModel):
    id: uuid.UUID
    strategy_id: uuid.UUID
    total_return: float
    win_rate: float
    max_drawdown: float
    trades: List[TradeResult]
    
    class Config:
        from_attributes = True
