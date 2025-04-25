from pydantic import BaseModel
from datetime import datetime

class RatingBase(BaseModel):
    stars: int

class RatingCreate(RatingBase):
    pass

class RatingOut(RatingBase):
    id: int
    user_id: int
    lesson_id: int

    class Config:
        from_attributes = True