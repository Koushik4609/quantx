import os
import httpx
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class UpstoxClient:
    BASE_URL = "https://api.upstox.com/v2"
    
    def __init__(self, access_token: str = None):
        self.access_token = access_token or os.environ.get("UPSTOX_ACCESS_TOKEN")
        self.api_key = os.environ.get("UPSTOX_API_KEY", "")
        self.api_secret = os.environ.get("UPSTOX_API_SECRET", "")
        self.redirect_uri = os.environ.get("UPSTOX_REDIRECT_URI", "http://localhost:8000/broker/upstox/callback")
        
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}" if self.access_token else ""
        }
    
    def get_login_url(self) -> str:
        return f"{self.BASE_URL}/login/authorization/dialog?response_type=code&client_id={self.api_key}&redirect_uri={self.redirect_uri}"

    async def exchange_token(self, code: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            url = f"{self.BASE_URL}/login/authorization/token"
            data = {
                "code": code,
                "client_id": self.api_key,
                "client_secret": self.api_secret,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code"
            }
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            response = await client.post(url, data=data, headers=headers)
            response.raise_for_status()
            res_data = response.json()
            # Update token if successful
            if "access_token" in res_data:
                self.access_token = res_data["access_token"]
                self.headers["Authorization"] = f"Bearer {self.access_token}"
            return res_data

    async def get_profile(self) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            url = f"{self.BASE_URL}/user/profile"
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_funds(self) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            url = f"{self.BASE_URL}/user/get-funds-and-margin"
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_holdings(self) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            url = f"{self.BASE_URL}/portfolio/long-term-holdings"
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_positions(self) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            url = f"{self.BASE_URL}/portfolio/short-term-positions"
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_orders(self) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            url = f"{self.BASE_URL}/order/retrieve-all"
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def get_market_status(self) -> Dict[str, Any]:
        """
        Fetches the market status from Upstox.
        Upstox actually returns status per exchange, e.g., NSE.
        """
        async with httpx.AsyncClient() as client:
            # We'll fetch NSE status as the default
            url = f"{self.BASE_URL}/market/status/NSE"
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
    async def get_quotes(self, instrument_key: str) -> Dict[str, Any]:
        """
        Fetches real-time quotes for a specific instrument.
        Example instrument_key: NSE_EQ|INE009A01021
        """
        async with httpx.AsyncClient() as client:
            url = f"{self.BASE_URL}/market-quote/quotes?instrument_key={instrument_key}"
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
    async def get_historical_candles(self, instrument_key: str, interval: str, to_date: str, from_date: str) -> Dict[str, Any]:
        """
        Fetches historical candles.
        interval: 1minute, 30minute, day, etc.
        dates in YYYY-MM-DD format.
        """
        async with httpx.AsyncClient() as client:
            url = f"{self.BASE_URL}/historical-candle/{instrument_key}/{interval}/{to_date}/{from_date}"
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
    async def get_company_profile(self, instrument_key: str) -> Dict[str, Any]:
        """
        Upstox does not have a dedicated company profile endpoint in v2.
        We will fetch the quote and enrich it with a mocked profile structure for the required endpoints.
        """
        quote_data = await self.get_quotes(instrument_key)
        # Mocking profile data wrapper
        return {
            "status": "success",
            "data": {
                "instrument_key": instrument_key,
                "company_name": "Profile Name (Mocked)",
                "industry": "Technology",
                "market_cap": "1.5T",
                "pe_ratio": "25.4",
                "quote_snapshot": quote_data.get("data", {})
            }
        }
        
    async def search_instruments(self, query: str) -> List[Dict[str, str]]:
        """
        Upstox doesn't provide a direct REST search.
        In a real app, we download their CSV on startup.
        Here we mock a search response mapping symbols to their Upstox instrument_keys.
        """
        # Hardcoded dictionary mapping common symbols to Upstox instrument_keys
        instruments = {
            "INFY": "NSE_EQ|INE009A01021",
            "RELIANCE": "NSE_EQ|INE002A01018",
            "TCS": "NSE_EQ|INE467B01029",
            "HDFCBANK": "NSE_EQ|INE040A01034"
        }
        
        results = []
        for symbol, key in instruments.items():
            if query.upper() in symbol:
                results.append({"symbol": symbol, "instrument_key": key})
                
        return results

# Dependency injection for FastAPI
def get_upstox_client() -> UpstoxClient:
    return UpstoxClient()
