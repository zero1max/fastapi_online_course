from pydantic import BaseModel

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