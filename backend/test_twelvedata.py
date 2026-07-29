import asyncio
from dotenv import load_dotenv
load_dotenv()
from app.services.twelvedata import TwelveDataService

async def main():
    td = TwelveDataService()
    print("Testing Search AAPL...")
    search = await td.search_symbol("AAPL")
    print(f"Search Result: {search[:1]}")

    print("\nTesting Quote AAPL...")
    quote = await td.get_quote("AAPL")
    print(f"Quote: {quote}")
    
    print("\nTesting Profile AAPL...")
    profile = await td.get_profile("AAPL")
    print(f"Profile: {profile}")
    
    print("\nTesting Time Series AAPL...")
    ts = await td.get_time_series("AAPL", interval="1day", outputsize=2)
    print(f"Time Series: {ts}")
    
    print("\nTesting Indicators AAPL...")
    ind = await td.get_indicators("AAPL", interval="1day")
    print(f"Indicators: {ind}")
    
    print("\nTesting Market Status...")
    status = await td.get_market_status()
    print(f"Market Status: {status}")

if __name__ == "__main__":
    asyncio.run(main())
