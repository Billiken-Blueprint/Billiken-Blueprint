from operator import ipow
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from billiken_blueprint.api import routers
import asyncio
from check_and_import_rmp import check_and_import_if_needed
from check_and_seed_courses import check_and_seed_courses_if_needed


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Check and seed courses if needed, then check and import RMP data if needed
    await check_and_seed_courses_if_needed()
    await check_and_import_if_needed()
    yield
    # Shutdown (if needed)


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routers under /api prefix
for router in routers:
    app.include_router(router, prefix="/api")

