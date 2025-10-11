# Backend

For backend use PDM. Maybe you can use pip or some other dependency manager but idk how to install from a pylock file with pip.

`brew install pdm`

`cd backend`

`pdm install`

`pdm run alembic upgrade head`

`chmod +x scripts/run_dev.sh`

`pdm run scripts/run_dev.sh`
