import asyncio
import time
import yfinance as yf
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.schemas.analytics import ScreenerStock, HeatmapSector, FinancialStatement, CalendarEvent, InstitutionalHolder, InsiderTrade
import datetime

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Simple in-memory cache to avoid rate limits
CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = 300 # 5 minutes

TRACKED_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA",
    "JPM", "V", "JNJ", "WMT", "PG", "MA", "UNH", "HD",
    "BAC", "XOM", "PFE", "DIS", "CSCO"
]

def get_cached(key: str):
    if key in CACHE:
        if time.time() - CACHE[key]["time"] < CACHE_TTL:
            return CACHE[key]["data"]
    return None

def set_cache(key: str, data: Any):
    CACHE[key] = {"time": time.time(), "data": data}

@router.get("/screener", response_model=List[ScreenerStock])
async def get_screener():
    cache_key = "screener"
    cached = get_cached(cache_key)
    if cached:
        return cached

    try:
        # yfinance download handles multiple tickers efficiently
        data = yf.download(TRACKED_TICKERS, period="2d", group_by="ticker", progress=False)
        results = []
        for ticker in TRACKED_TICKERS:
            try:
                # yf.download format depends on version, usually data[ticker] if grouped
                # It's safer to use Ticker.info for market cap and sector, but it's slow.
                # Let's fetch info in parallel or use a simplified approach
                # For real speed, yf.Tickers is better
                pass
            except Exception:
                continue
        
        # Actually yf.Tickers is better for info
        tickers = yf.Tickers(" ".join(TRACKED_TICKERS))
        for symbol in TRACKED_TICKERS:
            try:
                info = tickers.tickers[symbol].info
                if not info or 'previousClose' not in info:
                    continue
                price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                prev = info.get('previousClose', price)
                change = ((price - prev) / prev * 100) if prev else 0
                
                results.append(ScreenerStock(
                    symbol=symbol,
                    price=price,
                    change_percent=change,
                    volume=info.get('volume', 0),
                    market_cap=info.get('marketCap', 0),
                    sector=info.get('sector', 'Unknown')
                ))
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
                continue
                
        set_cache(cache_key, results)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/heatmap", response_model=List[HeatmapSector])
async def get_heatmap():
    screener_data = await get_screener()
    sectors = {}
    for stock in screener_data:
        if stock.sector not in sectors:
            sectors[stock.sector] = []
        sectors[stock.sector].append(stock)
        
    results = []
    for sector, stocks in sectors.items():
        total_cap = sum(s.market_cap for s in stocks)
        if total_cap > 0:
            avg_perf = sum(s.change_percent * (s.market_cap / total_cap) for s in stocks)
        else:
            avg_perf = sum(s.change_percent for s in stocks) / len(stocks)
            
        results.append(HeatmapSector(
            sector=sector,
            performance=avg_perf,
            stocks=stocks
        ))
    return results

@router.get("/{ticker}/financials", response_model=List[FinancialStatement])
async def get_financials(ticker: str):
    cache_key = f"financials_{ticker}"
    cached = get_cached(cache_key)
    if cached: return cached
    
    try:
        t = yf.Ticker(ticker)
        inc = t.financials
        bal = t.balance_sheet
        
        if inc is None or inc.empty:
            return []
            
        results = []
        for date in inc.columns:
            date_str = str(date).split(" ")[0]
            try:
                rev = inc.loc["Total Revenue", date] if "Total Revenue" in inc.index else None
                ni = inc.loc["Net Income", date] if "Net Income" in inc.index else None
                op = inc.loc["Operating Income", date] if "Operating Income" in inc.index else None
                
                ta = bal.loc["Total Assets", date] if bal is not None and "Total Assets" in bal.index and date in bal.columns else None
                tl = bal.loc["Total Liabilities Net Minority Interest", date] if bal is not None and "Total Liabilities Net Minority Interest" in bal.index and date in bal.columns else None
                
                results.append(FinancialStatement(
                    date=date_str,
                    total_revenue=float(rev) if rev and not str(rev) == 'nan' else None,
                    net_income=float(ni) if ni and not str(ni) == 'nan' else None,
                    operating_income=float(op) if op and not str(op) == 'nan' else None,
                    total_assets=float(ta) if ta and not str(ta) == 'nan' else None,
                    total_liabilities=float(tl) if tl and not str(tl) == 'nan' else None
                ))
            except Exception as e:
                print(e)
                continue
                
        set_cache(cache_key, results)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calendar", response_model=List[CalendarEvent])
async def get_calendar():
    # Mocking this slightly by returning upcoming data for tracked tickers
    cache_key = "calendar"
    cached = get_cached(cache_key)
    if cached: return cached
    
    results = []
    # Only pick a few to avoid long delays
    for symbol in ["AAPL", "MSFT", "GOOGL"]:
        try:
            t = yf.Ticker(symbol)
            cal = t.calendar
            if cal is not None and not cal.empty:
                for idx, row in cal.iterrows():
                    # Format differs by yfinance version, check if Earnings Date exists
                    date_val = None
                    if "Earnings Date" in cal.index:
                        dates = cal.loc["Earnings Date"]
                        if isinstance(dates, list) and len(dates) > 0:
                            date_val = str(dates[0])
                    
                    if date_val:
                        results.append(CalendarEvent(
                            symbol=symbol,
                            date=date_val,
                            type="earnings",
                            value=None
                        ))
                        break
        except Exception:
            continue
            
    set_cache(cache_key, results)
    return results

@router.get("/{ticker}/institutional", response_model=List[InstitutionalHolder])
async def get_institutional(ticker: str):
    cache_key = f"inst_{ticker}"
    cached = get_cached(cache_key)
    if cached: return cached
    
    try:
        t = yf.Ticker(ticker)
        inst = t.institutional_holders
        if inst is None or inst.empty:
            return []
            
        results = []
        for idx, row in inst.iterrows():
            if len(results) >= 10: break
            results.append(InstitutionalHolder(
                holder=str(row.get("Holder", "Unknown")),
                shares=int(row.get("Shares", 0)),
                date_reported=str(row.get("Date Reported", "")).split(" ")[0],
                percent_out=float(row.get("% Out", 0))
            ))
            
        set_cache(cache_key, results)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ticker}/insider", response_model=List[InsiderTrade])
async def get_insider(ticker: str):
    cache_key = f"insider_{ticker}"
    cached = get_cached(cache_key)
    if cached: return cached
    
    try:
        t = yf.Ticker(ticker)
        insider = t.insider_transactions
        if insider is None or insider.empty:
            return []
            
        results = []
        for idx, row in insider.iterrows():
            if len(results) >= 10: break
            results.append(InsiderTrade(
                insider=str(row.get("Insider Purchases", row.get("Insider", "Unknown"))),
                position=str(row.get("Position", "Unknown")),
                date=str(row.get("Start Date", row.get("Date", ""))).split(" ")[0],
                shares=int(row.get("Shares", 0)),
                transaction_type="Buy" if row.get("Shares", 0) > 0 else "Sell",
                value=float(row.get("Value", 0))
            ))
            
        set_cache(cache_key, results)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
