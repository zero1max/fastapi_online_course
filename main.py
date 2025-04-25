from fastapi import FastAPI
from app.core.database import engine, Base
from app.api.v1 import auth, users, courses, lessons, comments, ratings

app = FastAPI(title="Online Kurs Platformasi", version="1.0.0")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(courses.router, prefix="/courses", tags=["Courses"])
app.include_router(lessons.router, prefix="/lessons", tags=["Lessons"])
app.include_router(comments.router, prefix="/comments", tags=["Comments"])
app.include_router(ratings.router, prefix="/ratings", tags=["Ratings"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)