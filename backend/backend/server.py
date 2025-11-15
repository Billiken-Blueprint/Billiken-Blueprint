import asyncio

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api import identity, supported_majors

with open("jwt_dev.pem", "r") as f:
    JWT_PRIVATE_KEY = f.read()
with open("jwt_dev.pub", "r") as f:
    JWT_PUBLIC_KEY = f.read()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(identity.router)
app.include_router(supported_majors.router)
