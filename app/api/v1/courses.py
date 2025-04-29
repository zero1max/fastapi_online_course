from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.course import Course, UserCourse
from app.models.user import User
from app.schemas.course import CourseCreate, CourseOut, CourseUpdate

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
async def list_courses(
    db: AsyncSession = Depends(get_db),
    search: str | None = None,
    current_user: dict = Depends(get_current_user)
):
    db_user = await db.execute(select(User).filter(User.email == current_user["email"]))
    db_user = db_user.scalar()
    
    query = select(Course).filter(Course.author_id == db_user.id)
    if search:
        query = query.filter(Course.title.ilike(f"%{search}%"))
    
    courses = await db.execute(query)
    return courses.scalars().all()

@router.put("/{course_id}", response_model=CourseOut)
async def update_course(
    course_id: int,
    course_update: CourseUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_course = await db.execute(select(Course).filter(Course.id == course_id))
    db_course = db_course.scalar()
    
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    db_user = await db.execute(select(User).filter(User.email == current_user["email"]))
    db_user = db_user.scalar()
    
    if db_course.author_id != db_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to update this course")
    
    for key, value in course_update.dict(exclude_unset=True).items():
        setattr(db_course, key, value)
    
    db.add(db_course)
    await db.commit()
    await db.refresh(db_course)
    return db_course

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_course = await db.execute(select(Course).filter(Course.id == course_id))
    db_course = db_course.scalar()
    
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    db_user = await db.execute(select(User).filter(User.email == current_user["email"]))
    db_user = db_user.scalar()
    
    if db_course.author_id != db_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this course")
    
    await db.delete(db_course)
    await db.commit()
    return None

# @router.post("/{course_id}/enroll")
# async def enroll_course(
#     course_id: int,
#     current_user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     db_user = await db.execute(select(User).filter(User.email == current_user["email"]))
#     db_user = db_user.scalar()
#     db_course = await db.execute(select(Course).filter(Course.id == course_id))
#     db_course = db_course.scalar()
#     if not db_course:
#         raise HTTPException(status_code=404, detail="Course not found")
#     db_user_course = UserCourse(user_id=db_user.id, course_id=course_id)
#     db.add(db_user_course)
#     await db.commit()
#     return {"detail": "Enrolled successfully"}