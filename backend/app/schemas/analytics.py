from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ScreenerStock(BaseModel):
    symbol: str
    price: float
    change_percent: float
    volume: int
    market_cap: float
    sector: str

class HeatmapSector(BaseModel):
    sector: str
    performance: float
    stocks: List[ScreenerStock]

class FinancialStatement(BaseModel):
    date: str
    total_revenue: Optional[float] = None
    net_income: Optional[float] = None
    operating_income: Optional[float] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None

class CalendarEvent(BaseModel):
    symbol: str
    date: str
    type: str # "dividend" or "earnings"
    value: Optional[float] = None # Dividend amount or EPS estimate

class InstitutionalHolder(BaseModel):
    holder: str
    shares: int
    date_reported: str
    percent_out: float

class InsiderTrade(BaseModel):
    insider: str
    position: str
    date: str
    shares: int
    transaction_type: str # Buy or Sell
    value: float
