import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.finnhub import FinnhubService
from app.services.ai_agent import FinancialAssistant
from app.models.schema import BookmarkedArticle
from app.schemas.news import BookmarkCreate, BookmarkResponse, SummarizeRequest

# Mock DB dependency
async def get_db() -> AsyncSession:
    raise NotImplementedError("Database dependency not overridden")

def get_finnhub_client() -> FinnhubService:
    return FinnhubService()

router = APIRouter(prefix="/news", tags=["news"])

@router.get("/market")
async def get_general_news(client: FinnhubService = Depends(get_finnhub_client)):
    try:
        return await client.get_market_news("general")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/company/{ticker}")
async def get_company_news(ticker: str, client: FinnhubService = Depends(get_finnhub_client)):
    try:
        return await client.get_company_news(ticker)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize")
async def summarize_article(request: SummarizeRequest):
    try:
        return await FinancialAssistant.summarize_article(request.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bookmarks", response_model=BookmarkResponse)
async def add_bookmark(bookmark: BookmarkCreate, session: AsyncSession = Depends(get_db)):
    try:
        db_bookmark = BookmarkedArticle(
            user_id=bookmark.user_id,
            article_url=bookmark.article_url,
            article_title=bookmark.article_title,
            source=bookmark.source,
            published_at=bookmark.published_at
        )
        session.add(db_bookmark)
        await session.commit()
        await session.refresh(db_bookmark)
        return db_bookmark
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bookmarks/{user_id}", response_model=List[BookmarkResponse])
async def get_bookmarks(user_id: uuid.UUID, session: AsyncSession = Depends(get_db)):
    try:
        stmt = select(BookmarkedArticle).where(BookmarkedArticle.user_id == user_id).order_by(BookmarkedArticle.created_at.desc())
        result = await session.execute(stmt)
        bookmarks = result.scalars().all()
        return bookmarks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@router.delete("/bookmarks/{bookmark_id}")
async def delete_bookmark(bookmark_id: uuid.UUID, session: AsyncSession = Depends(get_db)):
    try:
        bookmark = await session.get(BookmarkedArticle, bookmark_id)
        if not bookmark:
            raise HTTPException(status_code=404, detail="Bookmark not found")
        await session.delete(bookmark)
        await session.commit()
        return {"status": "success"}
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
