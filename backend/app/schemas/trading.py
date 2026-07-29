import uuid
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class TradeRequest(BaseModel):
    portfolio_id: uuid.UUID
    symbol: str
    quantity: float = Field(..., gt=0)
    price: float = Field(..., gt=0, description="Simulated execution price")

class PositionSchema(BaseModel):
    symbol: str
    quantity: float
    average_cost: float
    current_price: float
    unrealized_pnl: float

class PortfolioSummary(BaseModel):
    portfolio_id: uuid.UUID
    cash_balance: float
    total_equity: float
    total_unrealized_pnl: float
    total_realized_pnl: float
    positions: List[PositionSchema]

class TransactionSchema(BaseModel):
    id: uuid.UUID
    transaction_type: str
    symbol: Optional[str]
    amount: float
    created_at: datetime

    class Config:
        from_attributes = True
