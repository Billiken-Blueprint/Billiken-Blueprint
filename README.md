# Backend

For backend use PDM. Maybe you can use pip or some other dependency manager but idk how to install from a pylock file with pip.

`brew install pdm`

`cd backend`

`pdm install`

`pdm run alembic upgrade head` - This creates/applies migrations to the database

`chmod +x scripts/run_dev.sh`

`pdm run scripts/run_dev.sh`

# Frontend

For frontend use pnpm. You may be able to use npm but you might run into issues installing dependencies at first.

`brew install pnpm`

`cd web`

`pnpm install`

At this point you should be able to use npm as it just uses node_modules

`pnpm run start`
