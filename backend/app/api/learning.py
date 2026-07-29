import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.schema import Course, Lesson, Quiz, UserProgress
from app.schemas.learning import CourseSchema, UserProgressUpdate

# Mock DB dependency
async def get_db() -> AsyncSession:
    raise NotImplementedError("Database dependency not overridden")

router = APIRouter(prefix="/learning", tags=["learning"])

@router.get("/courses", response_model=List[CourseSchema])
async def get_courses(session: AsyncSession = Depends(get_db)):
    try:
        stmt = select(Course).options(
            selectinload(Course.lessons).selectinload(Lesson.quizzes)
        )
        result = await session.execute(stmt)
        courses = result.scalars().all()
        return courses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/progress/{user_id}")
async def get_user_progress(user_id: uuid.UUID, session: AsyncSession = Depends(get_db)):
    try:
        stmt = select(UserProgress).where(UserProgress.user_id == user_id)
        result = await session.execute(stmt)
        progress = result.scalars().all()
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/progress")
async def update_user_progress(progress_update: UserProgressUpdate, session: AsyncSession = Depends(get_db)):
    try:
        stmt = select(UserProgress).where(
            UserProgress.user_id == progress_update.user_id,
            UserProgress.lesson_id == progress_update.lesson_id
        )
        result = await session.execute(stmt)
        progress = result.scalar_one_or_none()
        
        if progress:
            progress.completed = True
            if progress_update.score > progress.score:
                progress.score = progress_update.score
        else:
            progress = UserProgress(
                user_id=progress_update.user_id,
                lesson_id=progress_update.lesson_id,
                completed=True,
                score=progress_update.score
            )
            session.add(progress)
            
        await session.commit()
        return {"status": "success"}
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
