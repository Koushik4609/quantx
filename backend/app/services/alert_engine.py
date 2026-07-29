import asyncio
import logging
import yfinance as yf
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.schema import Alert

logger = logging.getLogger(__name__)

class AlertEngine:
    async def evaluate_alerts(self, session: AsyncSession):
        stmt = select(Alert).where(Alert.status == "ACTIVE")
        result = await session.execute(stmt)
        alerts = result.scalars().all()
        
        if not alerts:
            return 0
            
        # Group by symbol to optimize yfinance calls
        symbols = list(set([a.symbol for a in alerts if a.symbol and a.alert_type == "PRICE"]))
        live_prices = {}
        
        if symbols:
            try:
                tickers = yf.Tickers(" ".join(symbols))
                for sym in symbols:
                    # In a real app we'd use fastquote, but this is a mock.
                    info = tickers.tickers[sym].fast_info
                    live_prices[sym] = info.last_price
            except Exception as e:
                logger.error(f"Failed to fetch live prices: {e}")
                
        triggered_count = 0
        
        for alert in alerts:
            triggered = False
            
            if alert.alert_type == "PRICE" and alert.symbol in live_prices:
                price = live_prices[alert.symbol]
                if alert.condition == "ABOVE" and price > alert.value:
                    triggered = True
                elif alert.condition == "BELOW" and price < alert.value:
                    triggered = True
            
            # Other types like VOLUME, RSI, MACD, etc can be implemented similarly
            # by fetching technical data for the symbol.
            
            if triggered:
                alert.status = "TRIGGERED"
                alert.triggered_at = datetime.utcnow()
                session.add(alert)
                triggered_count += 1
                logger.info(f"Alert {alert.id} triggered for {alert.symbol}")
                
        if triggered_count > 0:
            await session.commit()
            
        return triggered_count

alert_engine = AlertEngine()
