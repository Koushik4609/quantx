import os
import uuid
import json
import logging
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from groq import AsyncGroq

from app.models.schema import AIChatHistory, Portfolio
from app.schemas.ai import ChatResponse, ChatMessage
from app.services.twelvedata import TwelveDataService
from app.services.trading_engine import TradingEngine

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
# Using current robust production models
FAST_MODEL = "llama-3.1-8b-instant"
REASONING_MODEL = "llama-3.3-70b-versatile"

client = AsyncGroq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

class FinancialAssistant:
    
    @staticmethod
    async def extract_ticker(query: str) -> Optional[str]:
        """Uses a fast LLM call to extract the ticker symbol from the user's query."""
        if not client:
            # Fallback mock extraction for local testing without API key
            words = query.upper().split()
            for word in words:
                if word in ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN"]:
                    return word
            return None

        prompt = f"""
        Extract the primary stock ticker symbol mentioned in the following query. 
        Return ONLY the ticker symbol in uppercase. If no ticker or company is mentioned, return the exact word "NONE".
        Do not add any other text.
        
        Query: {query}
        """
        try:
            chat_completion = await client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=FAST_MODEL,
                temperature=0.0
            )
            result = chat_completion.choices[0].message.content.strip().upper()
            if result == "NONE" or "NONE" in result:
                return None
            return ''.join(e for e in result if e.isalnum())
        except Exception as e:
            logger.error(f"Failed to extract ticker: {e}")
            return None

    @staticmethod
    async def generate_response(
        session: AsyncSession, 
        user_id: uuid.UUID, 
        portfolio_id: uuid.UUID, 
        message: str
    ) -> ChatResponse:
        
        tool_calls_made = []
        
        # 1. Detect Ticker
        ticker = await FinancialAssistant.extract_ticker(message)
        market_context = ""
        
        # 2. Fetch Live Market Data if ticker is found
        if ticker:
            tool_calls_made.append(f"Detected Ticker: {ticker}")
            try:
                td = TwelveDataService()
                quote = await td.get_quote(ticker)
                profile = await td.get_profile(ticker)
                
                market_context = f"""
                Live Market Data for {ticker}:
                - Last Price: {quote.get('last_price', 'N/A')}
                - Open: {quote.get('open', 'N/A')}
                - High: {quote.get('high', 'N/A')}
                - Low: {quote.get('low', 'N/A')}
                
                Company Profile:
                - Name: {profile.get('name', 'N/A')}
                - Sector: {profile.get('sector', 'N/A')}
                - Industry: {profile.get('industry', 'N/A')}
                - Description: {profile.get('description', 'N/A')}
                """
                tool_calls_made.append(f"Fetched Market Data for {ticker} from TwelveData")
            except Exception as e:
                # Inject failure so AI explicitly knows it can't guess!
                market_context = f"""
                [SYSTEM ALERT: The Live Market Data feed is currently disconnected or the ticker could not be retrieved. 
                Upstox API returned an error: {str(e)}. 
                DO NOT hallucinate or invent prices, ratios, or market data for {ticker}. 
                Explicitly inform the user that live market data is currently unavailable and base any general analysis purely on historical structural knowledge of the company.]
                """
                tool_calls_made.append(f"Market Data Fetch Failed: {str(e)}")
                
        # 3. Fetch User's Portfolio Context
        portfolio_context = ""
        try:
            summary = await TradingEngine.get_portfolio_summary(session, portfolio_id, {})
            portfolio_context = f"""
            User's Portfolio:
            - Total Equity: ${summary.total_equity:.2f}
            - Cash Balance: ${summary.cash_balance:.2f}
            - Unrealized PnL: ${summary.total_unrealized_pnl:.2f}
            
            Current Positions:
            """
            if summary.positions:
                for pos in summary.positions:
                    portfolio_context += f"- {pos.quantity} shares of {pos.symbol} @ Avg Cost ${pos.average_cost:.2f} (Unrealized PnL: ${pos.unrealized_pnl:.2f})\n"
            else:
                portfolio_context += "- No active positions.\n"
            tool_calls_made.append(f"Fetched Portfolio Context")
        except Exception as e:
            portfolio_context = f"[SYSTEM ALERT: Could not fetch user portfolio: {str(e)}]"

        # 4. Fetch Chat History
        stmt = select(AIChatHistory).where(AIChatHistory.user_id == user_id).order_by(AIChatHistory.created_at.desc()).limit(5)
        result = await session.execute(stmt)
        histories = result.scalars().all()
        histories.reverse() # Oldest first
        
        chat_messages = []
        for h in histories:
            chat_messages.append({"role": h.message_role, "content": h.content})

        # 5. Build System Prompt
        system_prompt = f"""
        You are QuantX AI, a highly advanced, professional, and elite AI financial assistant.
        Your primary directive is to provide accurate, insightful, and strictly factual financial analysis based ON THE CONTEXT PROVIDED.
        
        CRITICAL RULES:
        1. NEVER hallucinate financial data, stock prices, valuations, or news.
        2. NEVER use fake or placeholder data.
        3. If market data is provided in the context below, use it to answer the user's question accurately.
        4. If market data is explicitly stated as unavailable or disconnected, YOU MUST TELL THE USER. Do not guess the price or metrics.
        5. Provide responses in clean, well-formatted Markdown. Use bolding and bullet points for readability.
        
        --- LIVE CONTEXT ---
        {market_context}
        
        {portfolio_context}
        --------------------
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(chat_messages)
        messages.append({"role": "user", "content": message})
        
        # 6. Groq Inference
        ai_response_content = ""
        if not client:
            ai_response_content = (
                "**SYSTEM CONFIGURATION ERROR**\n\n"
                "The `GROQ_API_KEY` is missing in the backend environment. "
                "I am running in offline stub mode. \n\n"
                f"**Context gathered:**\n{market_context}\n{portfolio_context}"
            )
        else:
            try:
                chat_completion = await client.chat.completions.create(
                    messages=messages,
                    model=REASONING_MODEL,
                    temperature=0.2
                )
                ai_response_content = chat_completion.choices[0].message.content
            except Exception as e:
                logger.error(f"Groq API connection error: {e}")
                ai_response_content = f"**Connection Error:** Failed to connect to Groq API. {str(e)}"
        
        # 7. Persist to DB
        user_msg_db = AIChatHistory(user_id=user_id, message_role="user", content=message)
        ai_msg_db = AIChatHistory(user_id=user_id, message_role="assistant", content=ai_response_content)
        session.add_all([user_msg_db, ai_msg_db])
        # We don't commit here, the API layer will commit.
        
        return ChatResponse(response=ai_response_content, tool_calls_made=tool_calls_made)

    @staticmethod
    async def get_portfolio_health(session: AsyncSession, portfolio_id: uuid.UUID) -> dict:
        portfolio_context = ""
        try:
            summary = await TradingEngine.get_portfolio_summary(session, portfolio_id, {})
            portfolio_context = f"""
            User's Portfolio:
            - Total Equity: ${summary.total_equity:.2f}
            - Cash Balance: ${summary.cash_balance:.2f}
            - Unrealized PnL: ${summary.total_unrealized_pnl:.2f}
            - Realized PnL: ${summary.total_realized_pnl:.2f}
            
            Current Positions:
            """
            if summary.positions:
                for pos in summary.positions:
                    portfolio_context += f"- {pos.quantity} shares of {pos.symbol} @ Avg Cost ${pos.average_cost:.2f} (Unrealized PnL: ${pos.unrealized_pnl:.2f})\n"
            else:
                portfolio_context += "- No active positions.\n"
        except Exception as e:
            portfolio_context = f"[SYSTEM ALERT: Could not fetch user portfolio: {str(e)}]"

        if not client:
            return {
                "score": 50,
                "health": "Offline Mode",
                "analysis": "GROQ_API_KEY is missing. Unable to analyze portfolio health."
            }
            
        prompt = f"""
        Analyze the following portfolio and return a JSON object with strictly these keys:
        - "score": an integer from 1 to 100 representing portfolio health/diversification (higher is better).
        - "health": a short string (e.g., "Excellent", "Good", "Needs Diversification", "High Risk").
        - "analysis": a 2-sentence summary of the risk and health.
        
        {portfolio_context}
        
        Output ONLY valid JSON. Do not return markdown formatting blocks like ```json.
        """
        
        try:
            chat_completion = await client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=FAST_MODEL,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            content = chat_completion.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.error(f"Portfolio health API error: {e}")
            return {"score": 0, "health": "Error", "analysis": str(e)}

    @staticmethod
    async def get_daily_brief() -> dict:
        if not client:
            return {
                "brief": "GROQ_API_KEY missing. Cannot generate brief."
            }
        
        prompt = "Provide a 3 sentence daily market brief summary as if you are a professional analyst based on broadly known structural factors (since you do not have live news). Return a JSON object with a single key 'brief'. Do not use markdown blocks."
        try:
            chat_completion = await client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=FAST_MODEL,
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            content = chat_completion.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.error(f"Daily brief error: {e}")
            return {"brief": str(e)}

    @staticmethod
    async def summarize_article(url: str) -> dict:
        if not client:
            return {"summary": "GROQ_API_KEY missing. Cannot generate summary."}
        
        from app.services.news_client import NewsClient
        article_text = await NewsClient.extract_article_text(url)
        
        if not article_text:
            return {"summary": "Could not extract sufficient text from the article URL."}
            
        prompt = f"""
        Provide a concise, professional 3-sentence summary of the following financial news article.
        Never invent information.
        
        Article Text:
        {article_text}
        
        Return a JSON object with a single key 'summary'. Do not use markdown blocks.
        """
        
        try:
            chat_completion = await client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=FAST_MODEL,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            content = chat_completion.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.error(f"Summarize article error: {e}")
            return {"summary": str(e)}
