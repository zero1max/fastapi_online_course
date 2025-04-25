from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.comment import Comment
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentOut

router = APIRouter()

@router.post("/lessons/{lesson_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
async def create_comment(
    lesson_id: int,
    comment: CommentCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_user = await db.execute(select(User).filter(User.email == current_user["email"]))
    db_user = db_user.scalar()
    db_comment = Comment(**comment.dict(), user_id=db_user.id, lesson_id=lesson_id)
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment

@router.get("/lessons/{lesson_id}/comments", response_model=list[CommentOut])
async def list_comments(lesson_id: int, db: AsyncSession = Depends(get_db)):
    comments = await db.execute(select(Comment).filter(Comment.lesson_id == lesson_id))
    return comments.scalars().all()