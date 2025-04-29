from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.lesson import Lesson
from app.models.course import Course, UserCourse
from app.models.user import User
from app.schemas.lesson import LessonCreate, LessonOut, LessonUpdate

router = APIRouter()

@router.post("/{course_id}", response_model=LessonOut, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    course_id: int,
    lesson: LessonCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_user = await db.execute(select(User).filter(User.email == current_user["email"]))
    db_user = db_user.scalar()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_course = await db.execute(select(Course).filter(Course.id == course_id))
    db_course = db_course.scalar()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if db_course.author_id != db_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add lessons to this course")

    db_lesson = Lesson(
        course_id=course_id,
        title=lesson.title,
        video_url=lesson.video_url,
        content=lesson.content
    )
    db.add(db_lesson)
    await db.commit()
    await db.refresh(db_lesson)
    return db_lesson

@router.get("/{lesson_id}", response_model=LessonOut)
async def get_lesson(
    lesson_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_user = await db.execute(select(User).filter(User.email == current_user["email"]))
    db_user = db_user.scalar()
    db_lesson = await db.execute(select(Lesson).filter(Lesson.id == lesson_id))
    db_lesson = db_lesson.scalar()
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    db_user_course = await db.execute(
        select(UserCourse).filter(UserCourse.user_id == db_user.id, UserCourse.course_id == db_lesson.course_id)
    )
    if not db_user_course.scalar() and not db_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enrolled in course")
    return db_lesson

@router.put("/{lesson_id}", response_model=LessonOut)
async def update_lesson(
    lesson_id: int,
    lesson_update: LessonUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_user = await db.execute(select(User).filter(User.email == current_user["email"]))
    db_user = db_user.scalar()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_lesson = await db.execute(select(Lesson).filter(Lesson.id == lesson_id))
    db_lesson = db_lesson.scalar()
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    db_course = await db.execute(select(Course).filter(Course.id == db_lesson.course_id))
    db_course = db_course.scalar()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if db_course.author_id != db_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this lesson")

    for key, value in lesson_update.dict(exclude_unset=True).items():
        setattr(db_lesson, key, value)
    
    db.add(db_lesson)
    await db.commit()
    await db.refresh(db_lesson)
    return db_lesson

@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    lesson_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_user = await db.execute(select(User).filter(User.email == current_user["email"]))
    db_user = db_user.scalar()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_lesson = await db.execute(select(Lesson).filter(Lesson.id == lesson_id))
    db_lesson = db_lesson.scalar()
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    db_course = await db.execute(select(Course).filter(Course.id == db_lesson.course_id))
    db_course = db_course.scalar()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if db_course.author_id != db_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this lesson")

    await db.delete(db_lesson)
    await db.commit()
    return None