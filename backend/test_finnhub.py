import asyncio
from dotenv import load_dotenv
load_dotenv()
from app.services.finnhub import FinnhubService

async def main():
    fh = FinnhubService()
    
    print("Testing Market News...")
    news = await fh.get_market_news()
    print(f"Market News: {len(news)} articles found. First article: {news[0].get('headline') if news else 'None'}")
    
    print("\nTesting Company News (AAPL)...")
    c_news = await fh.get_company_news("AAPL")
    print(f"Company News: {len(c_news)} articles found. First article: {c_news[0].get('headline') if c_news else 'None'}")
    
    print("\nTesting Company Profile (AAPL)...")
    prof = await fh.get_company_profile("AAPL")
    print(f"Profile: {prof}")
    
    print("\nTesting Financials (AAPL)...")
    fin = await fh.get_financials("AAPL")
    print(f"Financials: {fin.get('metric', {}).get('52WeekHigh', 'N/A')} (52w High)")
    
    print("\nTesting Analyst Ratings (AAPL)...")
    rat = await fh.get_analyst_ratings("AAPL")
    print(f"Ratings: {rat[0] if rat else 'None'}")
    
    print("\nTesting IPO Calendar...")
    ipo = await fh.get_ipo_calendar()
    print(f"IPO Calendar: {len(ipo.get('ipoCalendar', []))} IPOs found.")
    
    print("\nTesting Economic Calendar...")
    eco = await fh.get_economic_calendar()
    print(f"Economic Calendar: {len(eco.get('economicCalendar', []))} events found.")

if __name__ == "__main__":
    asyncio.run(main())
