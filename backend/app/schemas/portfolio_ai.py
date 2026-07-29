from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class RebalancingSuggestion(BaseModel):
    action: str
    symbol: str
    reason: str

class PortfolioIntelligenceResponse(BaseModel):
    diversification_score: float
    risk_score: float
    volatility: float
    sector_allocation: Dict[str, float]
    performance_summary: str
    ai_analysis: str
    advantages: List[str]
    risks: List[str]
    recommendations: List[RebalancingSuggestion]
