import os
import httpx
import logging
from typing import Dict, Any, List, Optional
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type, before_sleep_log
from cachetools import TTLCache
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Cache configurations (Finnhub API limits to 60 calls/minute, heavily cache static data)
profile_cache = TTLCache(maxsize=1000, ttl=86400) # 24 hrs
ratings_cache = TTLCache(maxsize=500, ttl=86400) # 24 hrs
financials_cache = TTLCache(maxsize=500, ttl=86400) # 24 hrs
insiders_cache = TTLCache(maxsize=500, ttl=86400) # 24 hrs
ownership_cache = TTLCache(maxsize=500, ttl=86400) # 24 hrs
news_cache = TTLCache(maxsize=50, ttl=900) # 15 mins for news
calendar_cache = TTLCache(maxsize=10, ttl=3600) # 1 hour for calendars

class FinnhubAPIError(Exception):
    pass

class RateLimitError(FinnhubAPIError):
    pass

class FinnhubService:
    BASE_URL = "https://finnhub.io/api/v1"
    
    def __init__(self):
        self.api_key = os.environ.get("FINNHUB_API_KEY")
        if not self.api_key:
            logger.warning("FINNHUB_API_KEY is not set in environment!")
            
    async def _request(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        if not params:
            params = {}
        params['token'] = self.api_key
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"{self.BASE_URL}/{endpoint}"
            try:
                response = await client.get(url, params=params)
                
                if response.status_code == 429:
                    raise RateLimitError("Finnhub rate limit exceeded.")
                if response.status_code == 403:
                    # Return empty dict for premium endpoints on free tier
                    return {}
                    
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    raise RateLimitError("Finnhub rate limit exceeded.")
                if e.response.status_code == 403:
                    return {}
                raise FinnhubAPIError(f"HTTP Error: {e}")
            except httpx.RequestError as e:
                raise FinnhubAPIError(f"Request Error: {e}")

    @retry(
        retry=retry_if_exception_type((RateLimitError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def get_market_news(self, category: str = "general") -> List[Dict[str, Any]]:
        cache_key = f"market_news_{category}"
        if cache_key in news_cache:
            return news_cache[cache_key]
            
        data = await self._request("news", {"category": category})
        news_cache[cache_key] = data
        return data

    @retry(
        retry=retry_if_exception_type((RateLimitError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3)
    )
    async def get_company_news(self, symbol: str) -> List[Dict[str, Any]]:
        cache_key = f"company_news_{symbol}"
        if cache_key in news_cache:
            return news_cache[cache_key]
            
        # Finnhub requires from and to dates for company news. Fetch last 7 days.
        to_date = datetime.now().strftime('%Y-%m-%d')
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        data = await self._request("company-news", {
            "symbol": symbol,
            "from": from_date,
            "to": to_date
        })
        news_cache[cache_key] = data
        return data

    @retry(
        retry=retry_if_exception_type((RateLimitError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3)
    )
    async def get_company_profile(self, symbol: str) -> Dict[str, Any]:
        if symbol in profile_cache:
            return profile_cache[symbol]
            
        data = await self._request("stock/profile2", {"symbol": symbol})
        profile_cache[symbol] = data
        return data
        
    @retry(
        retry=retry_if_exception_type((RateLimitError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3)
    )
    async def get_financials(self, symbol: str) -> Dict[str, Any]:
        if symbol in financials_cache:
            return financials_cache[symbol]
            
        data = await self._request("stock/metric", {"symbol": symbol, "metric": "all"})
        financials_cache[symbol] = data
        return data

    @retry(
        retry=retry_if_exception_type((RateLimitError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3)
    )
    async def get_analyst_ratings(self, symbol: str) -> List[Dict[str, Any]]:
        if symbol in ratings_cache:
            return ratings_cache[symbol]
            
        data = await self._request("stock/recommendation", {"symbol": symbol})
        ratings_cache[symbol] = data
        return data

    @retry(
        retry=retry_if_exception_type((RateLimitError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3)
    )
    async def get_insider_transactions(self, symbol: str) -> Dict[str, Any]:
        if symbol in insiders_cache:
            return insiders_cache[symbol]
            
        data = await self._request("stock/insider-transactions", {"symbol": symbol})
        insiders_cache[symbol] = data
        return data

    @retry(
        retry=retry_if_exception_type((RateLimitError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3)
    )
    async def get_earnings(self, symbol: str) -> List[Dict[str, Any]]:
        cache_key = f"earnings_{symbol}"
        if cache_key in profile_cache:
            return profile_cache[cache_key]
            
        data = await self._request("stock/earnings", {"symbol": symbol})
        profile_cache[cache_key] = data
        return data

    @retry(
        retry=retry_if_exception_type((RateLimitError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3)
    )
    async def get_institutional_ownership(self, symbol: str) -> Dict[str, Any]:
        if symbol in ownership_cache:
            return ownership_cache[symbol]
            
        data = await self._request("stock/institutional-ownership", {"symbol": symbol})
        ownership_cache[symbol] = data
        return data

    @retry(
        retry=retry_if_exception_type((RateLimitError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3)
    )
    async def get_ipo_calendar(self) -> Dict[str, Any]:
        if "ipo" in calendar_cache:
            return calendar_cache["ipo"]
            
        to_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        from_date = datetime.now().strftime('%Y-%m-%d')
        
        data = await self._request("calendar/ipo", {"from": from_date, "to": to_date})
        calendar_cache["ipo"] = data
        return data

    @retry(
        retry=retry_if_exception_type((RateLimitError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3)
    )
    async def get_economic_calendar(self) -> Dict[str, Any]:
        if "economic" in calendar_cache:
            return calendar_cache["economic"]
            
        data = await self._request("calendar/economic")
        calendar_cache["economic"] = data
        return data
