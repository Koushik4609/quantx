import uuid
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class AlertCreate(BaseModel):
    symbol: Optional[str] = None
    alert_type: str # PRICE, VOLUME, RSI, MACD, NEWS, PORTFOLIO, EARNINGS
    condition: str  # ABOVE, BELOW, EQUAL
    value: float

class AlertResponse(BaseModel):
    id: uuid.UUID
    symbol: Optional[str]
    alert_type: str
    condition: str
    value: float
    status: str
    created_at: datetime
    triggered_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
