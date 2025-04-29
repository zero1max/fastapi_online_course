from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.rating import Rating
from app.models.user import User
from app.schemas.rating import RatingCreate, RatingOut

router = APIRouter()

@router.post("/{lesson_id}", response_model=RatingOut, status_code=status.HTTP_201_CREATED)
async def create_rating(
    lesson_id: int,
    rating: RatingCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_user = await db.execute(select(User).filter(User.email == current_user["email"]))
    db_user = db_user.scalar()
    db_rating = await db.execute(
        select(Rating).filter(Rating.user_id == db_user.id, Rating.lesson_id == lesson_id)
    )
    if db_rating.scalar():
        raise HTTPException(status_code=400, detail="Rating already exists")
    db_rating = Rating(**rating.dict(), user_id=db_user.id, lesson_id=lesson_id)
    db.add(db_rating)
    await db.commit()
    await db.refresh(db_rating)
    return db_rating

@router.get("/{lesson_id}")
async def get_average_rating(lesson_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(func.avg(Rating.stars)).filter(Rating.lesson_id == lesson_id))
    avg_rating = result.scalar() or 0
    return {"average_rating": round(avg_rating, 2)}