from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List
from app.services.twelvedata import TwelveDataService, TwelveDataAPIError, RateLimitError
from app.services.finnhub import FinnhubService, FinnhubAPIError, RateLimitError as FinnhubRateLimitError

router = APIRouter(prefix="/market", tags=["market"])

def get_twelvedata_client() -> TwelveDataService:
    return TwelveDataService()
    
def get_finnhub_client() -> FinnhubService:
    return FinnhubService()

@router.get("/search", response_model=List[Dict[str, str]])
async def search_instruments(
    query: str = Query(..., min_length=1),
    client: TwelveDataService = Depends(get_twelvedata_client)
):
    try:
        return await client.search_symbol(query)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/quote", response_model=Dict[str, Any])
async def get_market_quote(
    symbol: str = Query(..., description="Stock or Crypto Symbol"),
    client: TwelveDataService = Depends(get_twelvedata_client)
):
    try:
        return await client.get_quote(symbol)
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/profile")
async def get_company_profile(
    symbol: str = Query(..., description="E.g., AAPL"),
    client: TwelveDataService = Depends(get_twelvedata_client)
):
    try:
        return await client.get_profile(symbol)
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status")
async def get_market_status(
    client: TwelveDataService = Depends(get_twelvedata_client)
):
    try:
        return await client.get_market_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/historical")
async def get_historical_candles(
    symbol: str = Query(..., description="E.g., AAPL"),
    interval: str = Query(..., description="1min, 5min, 1h, 1day"),
    outputsize: int = Query(30, description="Number of candles"),
    client: TwelveDataService = Depends(get_twelvedata_client)
):
    try:
        return await client.get_time_series(symbol, interval=interval, outputsize=outputsize)
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/indicators")
async def get_indicators(
    symbol: str = Query(..., description="E.g., AAPL"),
    interval: str = Query("1day", description="1min, 5min, 1h, 1day"),
    client: TwelveDataService = Depends(get_twelvedata_client)
):
    try:
        return await client.get_indicators(symbol, interval=interval)
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/movers")
async def get_market_movers():
    raise HTTPException(status_code=501, detail="Market Movers data is not supported by TwelveData basic tier.")

@router.get("/news")
async def get_market_news(client: FinnhubService = Depends(get_finnhub_client)):
    try:
        return await client.get_market_news("general")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ipo")
async def get_ipo_calendar(client: FinnhubService = Depends(get_finnhub_client)):
    try:
        return await client.get_ipo_calendar()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sentiment")
async def get_market_sentiment():
    raise HTTPException(status_code=501, detail="Fear & Greed Sentiment data is not supported by current upstream provider.")

@router.get("/calendar")
async def get_economic_calendar(client: FinnhubService = Depends(get_finnhub_client)):
    try:
        return await client.get_economic_calendar()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/heatmap")
async def get_sector_heatmap():
    raise HTTPException(status_code=501, detail="Sector Heatmap is not supported by current upstream provider.")
