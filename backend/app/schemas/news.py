from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

class ArticleSchema(BaseModel):
    id: str
    title: str
    source: str
    url: str
    published_at: str
    related_tickers: List[str]
    summary: str

class BookmarkCreate(BaseModel):
    user_id: uuid.UUID
    article_url: str
    article_title: str
    source: Optional[str] = None
    published_at: Optional[str] = None

class BookmarkResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    article_url: str
    article_title: str
    source: Optional[str]
    published_at: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class SummarizeRequest(BaseModel):
    url: str
