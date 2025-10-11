import asyncio

from fastapi import FastAPI

from src.api import identity, supported_majors

app = FastAPI()

app.include_router(identity.router)
app.include_router(supported_majors.router)
