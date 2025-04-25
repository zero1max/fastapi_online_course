from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.course import Course, UserCourse
from app.models.user import User
from app.schemas.course import CourseCreate, CourseOut

router = APIRouter()

@router.post("/", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
async def create_course(
    course: CourseCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_user = await db.execute(select(User).filter(User.email == current_user["email"]))
    db_user = db_user.scalar()
    db_course = Course(**course.dict(), author_id=db_user.id)
    db.add(db_course)
    await db.commit()
    await db.refresh(db_course)
    return db_course

@router.get("/", response_model=list[CourseOut])
async def list_courses(db: AsyncSession = Depends(get_db), search: str | None = None):
    query = select(Course)
    if search:
        query = query.filter(Course.title.ilike(f"%{search}%"))
    courses = await db.execute(query)
    return courses.scalars().all()

@router.post("/{course_id}/enroll")
async def enroll_course(
    course_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_user = await db.execute(select(User).filter(User.email == current_user["email"]))
    db_user = db_user.scalar()
    db_course = await db.execute(select(Course).filter(Course.id == course_id))
    db_course = db_course.scalar()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    db_user_course = UserCourse(user_id=db_user.id, course_id=course_id)
    db.add(db_user_course)
    await db.commit()
    return {"detail": "Enrolled successfully"}