from contextlib import asynccontextmanager
from operator import ipow
import subprocess
import os
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from billiken_blueprint.api import routers


async def run_migrations_on_startup():
    """Run database migrations on application startup."""
    try:
        # Check if database exists
        db_path = "data/data.db"
        if not os.path.exists(db_path):
            os.makedirs("data", exist_ok=True)
        
        # Try to upgrade all heads first
        result = subprocess.run(
            ["uv", "run", "alembic", "upgrade", "heads"],
            capture_output=True,
            text=True,
            cwd="/app"
        )
        
        if result.returncode != 0:
            # If that fails, try merging heads and then upgrading
            print("Multiple heads detected, attempting to merge...")
            merge_result = subprocess.run(
                ["uv", "run", "alembic", "merge", "heads", "-m", "merge_heads"],
                capture_output=True,
                text=True,
                cwd="/app"
            )
            if merge_result.returncode == 0:
                subprocess.run(
                    ["uv", "run", "alembic", "upgrade", "head"],
                    cwd="/app"
                )
            else:
                print(f"Migration warning: {result.stderr}")
    except Exception as e:
        print(f"Migration error (non-fatal): {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await run_migrations_on_startup()
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

