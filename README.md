# Setup

## Docker

For a fresh clone, simply run:

```bash
docker compose build
docker compose up
```

The Docker build process automatically:
- Runs database migrations
- Imports courses, instructors, sections, degrees, and course attributes
- **RMP reviews load automatically from JSON files** (no import needed)

The compose configuration targets the dev build of the frontend and backend images.
These run their respective dev server which listen to changes you make in your local source directories,
which get bind-mounted into the containers.

## Local

### Backend

Install uv

```bash
cd backend
uv sync
uv run alembic upgrade head
```

**Note:** After cloning the repository, the database will be empty. To populate it with initial data, you have two options:

**Option 1: Build a clean seed database (recommended)**
```bash
# Builds a clean database with courses, instructors, etc.
uv run scripts/build_seed_db.py
# Update instructor RMP rating fields (needed for ratings to show)
uv run scripts/update_instructor_rmp_data.py
```

**Option 2: Import data manually**
```bash
# Import courses, instructors, sections, degrees, and course attributes from JSON files
uv run scripts/import_data.py
```

**Important:** RMP (RateMyProfessor) reviews are automatically loaded from JSON files in `data_dumps/` when needed - they should NOT be imported into the database. If your database has RMP reviews and is too large, run:
```bash
# Remove RMP reviews from database to reduce size
uv run scripts/clean_rmp_reviews.py
```

The database only stores user-created ratings and essential data (courses, instructors), keeping it small (~100-200KB instead of 800KB+).

Then start the server:

```bash
uv run fastapi dev server.py
```

**Important:** User-created ratings are stored in the local database file (`data/data.db`), which is gitignored. When you clone the repository to a new location:
- Run database migrations (creates empty database)
- Run the data import script (populates courses, instructors, etc.)
- RMP reviews will be automatically available from JSON files
- Any user-created ratings from your original setup won't be in the new clone - you'll need to create them again

### Frontend

Install pnpm

```bash
cd web
pnpm install
pnpm run start
```

# Development

Backend uses SQLAlchemy and alembic. Any new models should inherit from Base and also be exported in the db_metadata package.
Generate migrations with `uv run alembic revision --autogenerate -m "<message>"`

# Deployment

Build each image with `--target prod`. Backend exposes port 8000, frontend exposes port 8080. Frontend expects
environment variable `API_URL` which is used to reverse proxy '/api/*' requests to the backend.

Both images are built automatically on push to main and are available in the repo and organization's packages.

