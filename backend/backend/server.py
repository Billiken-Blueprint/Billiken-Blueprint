import asyncio

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api import identity, supported_majors, instructors, courses, ratings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routers under /api prefix
app.include_router(identity.router, prefix="/api")
app.include_router(supported_majors.router, prefix="/api")
app.include_router(instructors.router, prefix="/api")
app.include_router(courses.router, prefix="/api")
app.include_router(ratings.router, prefix="/api")
