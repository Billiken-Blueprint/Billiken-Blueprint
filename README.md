# Setup

## Docker

```bash
docker compose build
docker compose up
```

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
uv run fastapi dev server.py
```

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

