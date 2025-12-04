#!/bin/sh
set -e

echo "Starting backend server..."

# Ensure data directory exists
mkdir -p /app/data

# Check if database exists and is initialized
if [ ! -f "/app/data/data.db" ]; then
    echo "Database not found. Initializing database..."
    uv run alembic upgrade head
    echo "Database schema created."
    
    echo "Database is empty. Importing data..."
    uv run scripts/import_data.py
    echo "Data imported."
    
    # Update instructor RMP data
    if [ -d "/app/data_dumps" ] && [ -n "$(ls -A /app/data_dumps/*.json 2>/dev/null)" ]; then
        echo "Updating instructor RMP data..."
        uv run scripts/update_instructor_rmp_data.py || echo "Warning: RMP data update failed, but continuing..."
    else
        echo "Warning: data_dumps directory not found, skipping RMP data update"
    fi
else
    echo "Database exists. Checking if migrations are needed..."
    uv run alembic upgrade head
    
    # Check if database is empty (no instructors)
    INSTRUCTOR_COUNT=$(uv run python -c "
import asyncio
import sys
sys.path.insert(0, '/app')
from billiken_blueprint import services

async def check():
    instructors = await services.instructor_repository.get_all()
    print(len(instructors))

asyncio.run(check())
" 2>/dev/null || echo "0")
    
    if [ "$INSTRUCTOR_COUNT" = "0" ]; then
        echo "Database is empty. Importing data..."
        uv run scripts/import_data.py
        echo "Data imported."
        
        # Update instructor RMP data
        if [ -d "/app/data_dumps" ] && [ -n "$(ls -A /app/data_dumps/*.json 2>/dev/null)" ]; then
            echo "Updating instructor RMP data..."
            uv run scripts/update_instructor_rmp_data.py || echo "Warning: RMP data update failed, but continuing..."
        fi
    else
        echo "Database already has $INSTRUCTOR_COUNT instructors. Skipping data import."
    fi
fi

echo "Starting FastAPI server..."
exec "$@"

