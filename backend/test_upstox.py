import os
import pytest
import asyncio
from app.services.upstox_client import UpstoxClient

# Fixture to provide client
@pytest.fixture
def upstox_client():
    token = os.environ.get("UPSTOX_ACCESS_TOKEN", "fake_token_for_testing")
    return UpstoxClient(access_token=token)

@pytest.mark.asyncio
async def test_search(upstox_client):
    results = await upstox_client.search_instruments("INFY")
    assert len(results) > 0
    assert results[0]["symbol"] == "INFY"
    assert results[0]["instrument_key"] == "NSE_EQ|INE009A01021"

@pytest.mark.asyncio
async def test_market_status(upstox_client):
    status = await upstox_client.get_market_status()
    assert "status" in status

@pytest.mark.asyncio
async def test_quotes(upstox_client):
    quote = await upstox_client.get_quotes("NSE_EQ|INE009A01021")
    assert "status" in quote
    assert quote["status"] == "success"

@pytest.mark.asyncio
async def test_company_profile(upstox_client):
    profile = await upstox_client.get_company_profile("NSE_EQ|INE009A01021")
    assert "status" in profile
    assert profile["data"]["company_name"] == "Profile Name (Mocked)"

@pytest.mark.asyncio
async def test_historical_candles(upstox_client):
    candles = await upstox_client.get_historical_candles("NSE_EQ|INE009A01021", "1minute", "2023-10-30", "2023-10-01")
    assert "status" in candles
    assert candles["status"] == "success"
