import os
import httpx
import logging
from typing import Dict, Any, List, Optional
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type, before_sleep_log
from cachetools import TTLCache
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Cache configurations
# Profile cache: 24 hours
profile_cache = TTLCache(maxsize=1000, ttl=86400)
# Search cache: 24 hours
search_cache = TTLCache(maxsize=500, ttl=86400)
# Quote cache: 10 seconds to prevent hammering API if multiple users request the same stock
quote_cache = TTLCache(maxsize=1000, ttl=10)
# History cache: 1 minute
history_cache = TTLCache(maxsize=1000, ttl=60)

class TwelveDataAPIError(Exception):
    pass

class RateLimitError(TwelveDataAPIError):
    pass

class TwelveDataService:
    BASE_URL = "https://api.twelvedata.com"
    
    def __init__(self):
        self.api_key = os.environ.get("TWELVEDATA_API_KEY")
        if not self.api_key:
            logger.warning("TWELVEDATA_API_KEY is not set in environment!")
            
    async def _request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        if not params:
            params = {}
        params['apikey'] = self.api_key
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"{self.BASE_URL}/{endpoint}"
            try:
                response = await client.get(url, params=params)
                
                # Handle 429 Too Many Requests natively before parsing JSON
                if response.status_code == 429:
                    raise RateLimitError("TwelveData rate limit exceeded.")
                
                response.raise_for_status()
                data = response.json()
                
                # TwelveData sometimes returns 200 with an error object inside
                if data.get("status") == "error":
                    code = data.get("code")
                    message = data.get("message", "Unknown error")
                    if code == 429:
                        raise RateLimitError(f"Rate limit: {message}")
                    raise TwelveDataAPIError(f"API Error ({code}): {message}")
                    
                return data
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    raise RateLimitError("TwelveData rate limit exceeded.")
                raise TwelveDataAPIError(f"HTTP Error: {e}")
            except httpx.RequestError as e:
                raise TwelveDataAPIError(f"Request Error: {e}")

    @retry(
        retry=retry_if_exception_type((RateLimitError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def search_symbol(self, query: str) -> List[Dict[str, str]]:
        if query in search_cache:
            return search_cache[query]
            
        data = await self._request("symbol_search", {"symbol": query})
        results = data.get("data", [])
        
        # Normalize to standard format
        normalized = []
        for r in results:
            normalized.append({
                "symbol": r.get("symbol"),
                "name": r.get("instrument_name"),
                "exchange": r.get("exchange"),
                "type": r.get("instrument_type"),
                "country": r.get("country")
            })
            
        search_cache[query] = normalized
        return normalized

    @retry(
        retry=retry_if_exception_type((RateLimitError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        stop=stop_after_attempt(3)
    )
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        if symbol in quote_cache:
            return quote_cache[symbol]
            
        data = await self._request("quote", {"symbol": symbol})
        
        # Normalize to standard format
        normalized = {
            "symbol": data.get("symbol"),
            "name": data.get("name"),
            "exchange": data.get("exchange"),
            "datetime": data.get("datetime"),
            "last_price": float(data.get("close", 0)),
            "open": float(data.get("open", 0)),
            "high": float(data.get("high", 0)),
            "low": float(data.get("low", 0)),
            "volume": int(data.get("volume", 0)),
            "previous_close": float(data.get("previous_close", 0)),
            "change": float(data.get("change", 0)),
            "percent_change": float(data.get("percent_change", 0))
        }
        
        quote_cache[symbol] = normalized
        return normalized

    @retry(
        retry=retry_if_exception_type((RateLimitError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3)
    )
    async def get_time_series(self, symbol: str, interval: str = "1day", outputsize: int = 30) -> List[Dict[str, Any]]:
        # Mapping standard intervals to TwelveData format (1min, 5min, 15min, 30min, 45min, 1h, 2h, 4h, 1day, 1week, 1month)
        cache_key = f"{symbol}_{interval}_{outputsize}"
        if cache_key in history_cache:
            return history_cache[cache_key]
            
        data = await self._request("time_series", {
            "symbol": symbol,
            "interval": interval,
            "outputsize": outputsize
        })
        
        values = data.get("values", [])
        
        normalized = []
        for v in values:
            normalized.append({
                "datetime": v.get("datetime"),
                "open": float(v.get("open", 0)),
                "high": float(v.get("high", 0)),
                "low": float(v.get("low", 0)),
                "close": float(v.get("close", 0)),
                "volume": int(v.get("volume", 0))
            })
            
        history_cache[cache_key] = normalized
        return normalized

    @retry(
        retry=retry_if_exception_type((RateLimitError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3)
    )
    async def get_profile(self, symbol: str) -> Dict[str, Any]:
        if symbol in profile_cache:
            return profile_cache[symbol]
            
        data = await self._request("profile", {"symbol": symbol})
        
        normalized = {
            "symbol": data.get("symbol"),
            "name": data.get("name"),
            "exchange": data.get("exchange"),
            "sector": data.get("sector"),
            "industry": data.get("industry"),
            "description": data.get("description"),
            "employees": data.get("employees"),
            "website": data.get("website")
        }
        
        profile_cache[symbol] = normalized
        return normalized

    @retry(
        retry=retry_if_exception_type((RateLimitError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3)
    )
    async def get_indicators(self, symbol: str, interval: str = "1day") -> Dict[str, Any]:
        """Fetch popular technical indicators (MACD, RSI, EMA) in one go (simulated via multiple calls if needed, or just returning a couple)."""
        # Note: Depending on plan, we can fetch multiple indicators. 
        # We will fetch RSI and MACD separately and combine.
        try:
            rsi_data = await self._request("rsi", {"symbol": symbol, "interval": interval, "time_period": 14})
            macd_data = await self._request("macd", {"symbol": symbol, "interval": interval})
            
            rsi_val = rsi_data.get("values", [{}])[0].get("rsi", "0")
            macd_val = macd_data.get("values", [{}])[0]
            
            return {
                "symbol": symbol,
                "interval": interval,
                "rsi": float(rsi_val),
                "macd": float(macd_val.get("macd", 0)),
                "macd_signal": float(macd_val.get("macd_signal", 0)),
                "macd_hist": float(macd_val.get("macd_hist", 0))
            }
        except Exception as e:
            logger.error(f"Failed to fetch indicators for {symbol}: {e}")
            return {}

    async def get_market_status(self) -> Dict[str, str]:
        """TwelveData doesn't have a direct /market_status free endpoint, returning a mocked status or simple check."""
        try:
            # We can check AAPL quote to see if it's trading as a proxy for US Market
            quote = await self.get_quote("AAPL")
            is_open = quote.get("volume", 0) > 0 # Rough heuristic
            return {
                "status": "OPEN" if is_open else "CLOSED",
                "message": "Market status inferred from AAPL volume."
            }
        except Exception:
            return {"status": "UNKNOWN", "message": "Could not fetch market status."}
