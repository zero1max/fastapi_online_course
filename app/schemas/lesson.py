from pydantic import BaseModel
from typing import Optional

class LessonBase(BaseModel):
    title: str
    video_url: str
    content: str

class LessonCreate(LessonBase):
    pass

class LessonOut(LessonBase):
    id: int
    course_id: int

    class Config:
        from_attributes = True

class LessonUpdate(BaseModel):
    title: Optional[str] = None
    video_url: Optional[str] = None
    content: Optional[str] = None