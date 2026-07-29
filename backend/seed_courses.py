import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from app.models.schema import Course, Lesson, Quiz
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./quantx.db")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

BEGINNER_COURSE = {
    "title": "Stock Market Basics",
    "description": "Learn the fundamentals of the stock market, how it works, and basic terminology.",
    "level": "Beginner",
    "lessons": [
        {
            "title": "What is a Stock?",
            "content": "# What is a Stock?\n\nA stock represents a share in the ownership of a company. When you buy a stock, you become a part-owner of that company. Companies issue stocks to raise capital for their operations, and investors buy them for a return on their investment.\n\n## Key Concepts\n- **Shareholder:** An individual or institution that legally owns one or more shares of a public or private corporation.\n- **Dividends:** A distribution of a portion of a company's earnings to its shareholders.\n\n![Stock Market Basics](https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&q=80&w=800)",
            "quizzes": [
                {
                    "question": "What does buying a stock represent?",
                    "options": ["A loan to the company", "Ownership in the company", "A guaranteed return", "A physical asset"],
                    "correct_index": 1
                }
            ]
        },
        {
            "title": "How the Market Works",
            "content": "# How the Market Works\n\nThe stock market is a platform where buyers and sellers trade shares of publicly held companies. It operates through exchanges, like the New York Stock Exchange (NYSE) or NASDAQ.\n\n## Supply and Demand\nStock prices are driven by supply and demand. If more people want to buy a stock (demand) than sell it (supply), the price goes up. Conversely, if more people want to sell a stock than buy it, the price goes down.",
            "quizzes": [
                {
                    "question": "What primary force drives stock prices up or down?",
                    "options": ["Government regulations", "Supply and demand", "Corporate marketing", "Interest rates"],
                    "correct_index": 1
                }
            ]
        }
    ]
}

INTERMEDIATE_COURSE = {
    "title": "Technical Analysis",
    "description": "Learn how to read charts, identify trends, and use indicators for trading.",
    "level": "Intermediate",
    "lessons": [
        {
            "title": "Candlestick Patterns",
            "content": "# Candlestick Patterns\n\nCandlestick charts are used by traders to determine possible price movement based on past patterns. Each candlestick represents the open, high, low, and close (OHLC) for a specific time period.\n\n## Bullish vs Bearish\n- **Bullish (Green/White):** The closing price is higher than the opening price.\n- **Bearish (Red/Black):** The closing price is lower than the opening price.\n\n![Candlestick Chart](https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&q=80&w=800)",
            "quizzes": [
                {
                    "question": "What does a green (bullish) candlestick indicate?",
                    "options": ["Price closed lower than it opened", "Price closed higher than it opened", "Price didn't move", "The market is closed"],
                    "correct_index": 1
                }
            ]
        }
    ]
}

ADVANCED_COURSE = {
    "title": "Options Trading",
    "description": "Master advanced strategies using options contracts.",
    "level": "Advanced",
    "lessons": [
        {
            "title": "Calls and Puts",
            "content": "# Calls and Puts\n\nOptions are financial derivatives that give buyers the right, but not the obligation, to buy or sell an underlying asset at an agreed-upon price and date.\n\n## Types of Options\n- **Call Option:** Gives you the right to BUY the asset. You buy calls when you are bullish.\n- **Put Option:** Gives you the right to SELL the asset. You buy puts when you are bearish.",
            "quizzes": [
                {
                    "question": "When would you typically buy a Put option?",
                    "options": ["When you expect the price to rise", "When you expect the price to fall", "When you expect the price to stay flat", "When you want to earn dividends"],
                    "correct_index": 1
                }
            ]
        }
    ]
}

async def seed_data():
    async with AsyncSessionLocal() as session:
        # Check if courses exist
        result = await session.execute(select(Course))
        if result.scalars().first():
            print("Courses already exist. Skipping seed.")
            return

        print("Seeding courses...")
        for course_data in [BEGINNER_COURSE, INTERMEDIATE_COURSE, ADVANCED_COURSE]:
            c = Course(title=course_data["title"], description=course_data["description"], level=course_data["level"])
            session.add(c)
            await session.flush()
            
            for idx, lesson_data in enumerate(course_data["lessons"]):
                l = Lesson(course_id=c.id, title=lesson_data["title"], content=lesson_data["content"], order=idx+1)
                session.add(l)
                await session.flush()
                
                for q_data in lesson_data["quizzes"]:
                    q = Quiz(lesson_id=l.id, question=q_data["question"], options=q_data["options"], correct_option_index=q_data["correct_index"])
                    session.add(q)
        
        await session.commit()
        print("Successfully seeded courses.")

if __name__ == "__main__":
    asyncio.run(seed_data())
