Test change

Test change 2

# Setup

## Docker

```bash
docker compose build
docker compose up
```

Only dev images are built. These run their respective dev server which listen to changes you make in your local source directories,
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
