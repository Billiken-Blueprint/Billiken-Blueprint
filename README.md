# Docker

The project can be ran with Docker Compose. Podman not tested.

```bash
docker compose build
docker compose up
```

Only the src folders are bind mounted for both backend and web services.
If you edit config files or add dependencies, you will have to run `docker compose build` again.

If you want, you can bind mount the backend/data directory so the database persists between container lifecycles.

# No docker

## Backend

For backend use uv. Previously we used pdm but it wasn't working well with docker.

`brew install uv`

`cd backend`

`uv sync`

`uv run alembic upgrade head` - This creates/applies migrations to the database

`chmod +x scripts/run_dev.sh`

`uv run scripts/run_dev.sh`

## Frontend

For frontend use pnpm. You may be able to use npm but you might run into issues installing dependencies at first.

`brew install pnpm`

`cd web`

`pnpm install`

At this point you should be able to use npm as it just uses node_modules

`pnpm run start`
