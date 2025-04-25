from pydantic import BaseModel

class CourseBase(BaseModel):
    title: str
    description: str

class CourseCreate(CourseBase):
    pass

class CourseOut(CourseBase):
    id: int
    author_id: int

    class Config:
        from_attributes = True