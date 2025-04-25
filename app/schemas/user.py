from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    full_name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: str | None = None

class UserOut(UserBase):
    id: int
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True