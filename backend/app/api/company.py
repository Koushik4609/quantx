from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List
from app.services.finnhub import FinnhubService, FinnhubAPIError, RateLimitError

router = APIRouter(prefix="/company", tags=["company"])

def get_finnhub_client() -> FinnhubService:
    return FinnhubService()

@router.get("/{ticker}", response_model=Dict[str, Any])
async def get_company_profile(
    ticker: str,
    client: FinnhubService = Depends(get_finnhub_client)
):
    try:
        return await client.get_company_profile(ticker)
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{ticker}/financials", response_model=Dict[str, Any])
async def get_company_financials(
    ticker: str,
    client: FinnhubService = Depends(get_finnhub_client)
):
    try:
        return await client.get_financials(ticker)
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{ticker}/analyst-ratings", response_model=List[Dict[str, Any]])
async def get_company_analyst_ratings(
    ticker: str,
    client: FinnhubService = Depends(get_finnhub_client)
):
    try:
        return await client.get_analyst_ratings(ticker)
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{ticker}/insiders", response_model=Dict[str, Any])
async def get_company_insiders(
    ticker: str,
    client: FinnhubService = Depends(get_finnhub_client)
):
    try:
        return await client.get_insider_transactions(ticker)
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{ticker}/earnings", response_model=List[Dict[str, Any]])
async def get_company_earnings(
    ticker: str,
    client: FinnhubService = Depends(get_finnhub_client)
):
    try:
        return await client.get_earnings(ticker)
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{ticker}/ownership", response_model=Dict[str, Any])
async def get_company_ownership(
    ticker: str,
    client: FinnhubService = Depends(get_finnhub_client)
):
    try:
        return await client.get_institutional_ownership(ticker)
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
