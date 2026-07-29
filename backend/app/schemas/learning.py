from pydantic import BaseModel
from typing import List, Optional
import uuid

class QuizSchema(BaseModel):
    id: uuid.UUID
    lesson_id: uuid.UUID
    question: str
    options: List[str]
    correct_option_index: int
    
    class Config:
        from_attributes = True

class LessonSchema(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    content: str
    order: int
    quizzes: List[QuizSchema] = []
    
    class Config:
        from_attributes = True

class CourseSchema(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    level: str
    lessons: List[LessonSchema] = []
    
    class Config:
        from_attributes = True

class UserProgressSchema(BaseModel):
    lesson_id: uuid.UUID
    completed: bool
    score: int
    
    class Config:
        from_attributes = True

class UserProgressUpdate(BaseModel):
    user_id: uuid.UUID
    lesson_id: uuid.UUID
    score: int
