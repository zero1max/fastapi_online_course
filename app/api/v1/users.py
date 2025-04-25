from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate

router = APIRouter()

@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    db_user = await db.execute(select(User).filter(User.email == current_user["email"]))
    db_user = db_user.scalar()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/me", response_model=UserOut)
async def update_user_me(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_user = await db.execute(select(User).filter(User.email == current_user["email"]))
    db_user = db_user.scalar()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    for var, value in user_update.dict(exclude_unset=True).items():
        setattr(db_user, var, value)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.get("/admin/users", response_model=list[UserOut])
async def list_users(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    db_user = await db.execute(select(User).filter(User.email == current_user["email"]))
    db_user = db_user.scalar()
    
    # Foydalanuvchi topilmasa yoki admin bo‘lmasa xatolik
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not db_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    
    # Barcha foydalanuvchilarni olish
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users