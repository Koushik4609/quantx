import yfinance as yf
from typing import List, Dict, Any
import datetime
import urllib.parse
from bs4 import BeautifulSoup
import httpx
import logging

class NewsClient:
    """
    A service that fetches live news from yfinance.
    """
    
    @staticmethod
    def get_market_news() -> List[Dict[str, Any]]:
        """
        Fetch general market news by looking at a broad index like SPY.
        """
        spy = yf.Ticker("SPY")
        news = spy.news
        return NewsClient._format_news(news)

    @staticmethod
    def get_company_news(ticker: str) -> List[Dict[str, Any]]:
        """
        Fetch company-specific news.
        """
        t = yf.Ticker(ticker)
        news = t.news
        return NewsClient._format_news(news)
        
    @staticmethod
    def _format_news(raw_news: List[dict]) -> List[Dict[str, Any]]:
        formatted = []
        for item in raw_news:
            # yfinance returns a list of dictionaries with title, publisher, link, providerPublishTime
            pub_time = item.get("providerPublishTime")
            if pub_time:
                dt = datetime.datetime.fromtimestamp(pub_time, tz=datetime.timezone.utc).isoformat()
            else:
                dt = datetime.datetime.now(datetime.timezone.utc).isoformat()
                
            formatted.append({
                "id": item.get("uuid", ""),
                "title": item.get("title", "No Title"),
                "source": item.get("publisher", "Unknown"),
                "url": item.get("link", ""),
                "published_at": dt,
                "related_tickers": item.get("relatedTickers", []),
                "summary": item.get("summary", "") # Sometimes available
            })
        return formatted
        
    @staticmethod
    async def extract_article_text(url: str) -> str:
        """
        Attempt to scrape the article text given a URL.
        Yahoo Finance redirects often, but we will do our best.
        """
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                resp = await client.get(url, headers=headers, timeout=10.0)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    # Very naive extraction: just grab paragraphs
                    paragraphs = soup.find_all('p')
                    text = "\n".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
                    return text[:4000] # Cap to avoid huge prompts
        except Exception as e:
            logging.error(f"Failed to extract article {url}: {e}")
        return ""
