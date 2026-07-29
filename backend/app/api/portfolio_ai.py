import os
import json
import uuid
import yfinance as yf
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from groq import AsyncGroq

from app.models.schema import Position, Portfolio
from app.schemas.portfolio_ai import PortfolioIntelligenceResponse, RebalancingSuggestion

router = APIRouter(prefix="/portfolio/intelligence", tags=["portfolio-ai"])

# Mock DB dependency
async def get_db() -> AsyncSession:
    raise NotImplementedError("Database dependency not overridden")

@router.get("/", response_model=PortfolioIntelligenceResponse)
async def get_portfolio_intelligence(user_id: uuid.UUID, session: AsyncSession = Depends(get_db)):
    try:
        # Fetch portfolio
        stmt_port = select(Portfolio).where(Portfolio.user_id == user_id)
        res_port = await session.execute(stmt_port)
        portfolio = res_port.scalar_one_or_none()
        
        if not portfolio:
            positions = []
        else:
            stmt = select(Position).where(Position.portfolio_id == portfolio.id)
            result = await session.execute(stmt)
            positions = result.scalars().all()

        if not positions:
            return PortfolioIntelligenceResponse(
                diversification_score=0.0,
                risk_score=0.0,
                volatility=0.0,
                sector_allocation={},
                performance_summary="Portfolio is empty.",
                ai_analysis="You currently have no open positions. Start trading to receive AI portfolio intelligence.",
                advantages=[],
                risks=[],
                recommendations=[]
            )

        # Calculate metrics
        total_value = float(sum(float(p.quantity) * float(p.average_price) for p in positions))
            
        sector_allocation = {}
        # Fetch sectors via yfinance
        symbols = [p.symbol for p in positions]
        if symbols:
            tickers = yf.Tickers(" ".join(symbols))
            for p in positions:
                try:
                    info = tickers.tickers[p.symbol].info
                    sector = info.get("sector", "Unknown")
                    if sector not in sector_allocation:
                        sector_allocation[sector] = 0.0
                    val = float(p.quantity) * float(p.average_price)
                    sector_allocation[sector] += val
                except Exception:
                    sector = "Unknown"
                    if sector not in sector_allocation:
                        sector_allocation[sector] = 0.0
                    val = float(p.quantity) * float(p.average_price)
                    sector_allocation[sector] += val

        # Normalize sector allocation to percentages
        if total_value > 0:
            for s in sector_allocation:
                sector_allocation[s] = round((sector_allocation[s] / total_value) * 100, 2)

        # HHI index for diversification
        hhi = sum((pct ** 2) for pct in sector_allocation.values())
        # HHI: 10000 = perfectly concentrated, 0 = perfectly diversified
        # Let's map it to 0-100 score where 100 is highly diversified
        diversification_score = max(0, 100 - (hhi / 100))
        
        # Volatility mock based on diversification (since full covariance matrix takes time)
        volatility = max(5.0, 30.0 - (diversification_score * 0.2)) 
        
        # Risk score (0-100)
        risk_score = min(100, max(0, (volatility * 2) + (hhi / 200)))

        # Format prompt for Groq
        portfolio_str = "\n".join([f"{p.symbol}: {p.quantity} shares, Cost Basis: ${p.average_price}" for p in positions])
        sector_str = json.dumps(sector_allocation)
        
        prompt = f"""
        You are QuantX AI, an elite financial advisor.
        Your ONLY job is to analyze the following numerical summary of a user's portfolio.
        
        CRITICAL RULES:
        1. NEVER invent, hallucinate, or assume any financial data, stock prices, valuations, news, or metrics.
        2. Base your analysis STRICTLY on the numbers provided below. Do not pull outside data.
        3. Provide actionable rebalancing recommendations if needed.
        
        Numerical Summary:
        - Total Portfolio Value: ${total_value:.2f}
        
        Positions Details:
        {portfolio_str}
        
        Calculated Metrics:
        - Diversification Score (HHI Index): {hhi} (lower is better, <1500 is good, >2500 is concentrated)
        - Estimated Volatility: {volatility:.2f}%
        - Assigned Risk Score: {risk_score:.2f}/100
        
        Sector Breakdown:
        {sector_str}
        
        Return your analysis as a JSON object strictly matching this format:
        {{
            "ai_analysis": "A detailed 3-paragraph analysis of their portfolio health and risk.",
            "performance_summary": "A 2-sentence summary of their PnL performance.",
            "advantages": ["Advantage 1", "Advantage 2"],
            "risks": ["Risk 1", "Risk 2"],
            "recommendations": [
                {{
                    "symbol": "TICKER",
                    "action": "BUY or SELL",
                    "reason": "Why?"
                }}
            ]
        }}
        
        Output ONLY valid JSON. Do not include markdown tags like ```json.
        """

        groq_key = os.environ.get("GROQ_API_KEY")
        
        if groq_key:
            client = AsyncGroq(api_key=groq_key)
            completion = await client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            response_text = completion.choices[0].message.content
            ai_data = json.loads(response_text)
        else:
            # Fallback if no key
            ai_data = {
                "performance_summary": "API Key missing.",
                "ai_analysis": "Configure GROQ_API_KEY to see real AI analysis.",
                "advantages": ["No key provided"],
                "risks": ["No key provided"],
                "recommendations": []
            }

        return PortfolioIntelligenceResponse(
            diversification_score=round(diversification_score, 2),
            risk_score=round(risk_score, 2),
            volatility=round(volatility, 2),
            sector_allocation=sector_allocation,
            performance_summary=ai_data.get("performance_summary", ""),
            ai_analysis=ai_data.get("ai_analysis", ""),
            advantages=ai_data.get("advantages", []),
            risks=ai_data.get("risks", []),
            recommendations=[RebalancingSuggestion(**r) for r in ai_data.get("recommendations", [])]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
