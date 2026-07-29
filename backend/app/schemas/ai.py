from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime

class ChatMessage(BaseModel):
    role: str # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    user_id: uuid.UUID
    portfolio_id: uuid.UUID
    message: str

class ChatResponse(BaseModel):
    response: str
    tool_calls_made: List[str] = []

class ChatHistorySchema(BaseModel):
    id: uuid.UUID
    message_role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
