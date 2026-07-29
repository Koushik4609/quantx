import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_get_screener(client: AsyncClient):
    # This might take a few seconds due to yfinance
    response = await client.get("/analytics/screener")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "symbol" in data[0]

@pytest.mark.asyncio
async def test_get_heatmap(client: AsyncClient):
    response = await client.get("/analytics/heatmap")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "sector" in data[0]

@pytest.mark.asyncio
async def test_get_financials(client: AsyncClient):
    response = await client.get("/analytics/AAPL/financials")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_get_calendar(client: AsyncClient):
    response = await client.get("/analytics/calendar")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_get_institutional(client: AsyncClient):
    response = await client.get("/analytics/AAPL/institutional")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_get_insider(client: AsyncClient):
    response = await client.get("/analytics/AAPL/insider")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
