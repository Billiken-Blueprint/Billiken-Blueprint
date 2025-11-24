from contextlib import asynccontextmanager
from operator import ipow
import subprocess
import os
import asyncio
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


async def check_and_import_rmp_if_needed():
    """Check if RMP data exists, and import if missing."""
    try:
        from billiken_blueprint import services
        
        # Check if we have any RMP reviews
        all_instructors = await services.instructor_repository.get_all()
        has_rmp_data = False
        
        for instructor in all_instructors[:5]:  # Check first 5 instructors
            reviews = await services.rmp_review_repository.get_by_instructor_id(instructor.id)
            if reviews:
                has_rmp_data = True
                break
        
        if not has_rmp_data:
            print("⚠ No RMP data found. Attempting to import...")
            from import_rmp_ratings import import_rmp_ratings
            await import_rmp_ratings()
            
            # Also update course_ids for imported reviews
            try:
                from update_rmp_review_course_ids import update_rmp_review_course_ids
                await update_rmp_review_course_ids()
            except Exception as e:
                print(f"Note: Could not update RMP review course_ids: {e}")
        else:
            print("✓ RMP data already exists in database")
    except Exception as e:
        print(f"RMP import check error (non-fatal): {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await run_migrations_on_startup()
    await check_and_import_rmp_if_needed()
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

