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
    
    # Check if database is empty (check file size - empty DB is usually < 10KB)
    DB_SIZE=$(stat -f%z /app/data/data.db 2>/dev/null || stat -c%s /app/data/data.db 2>/dev/null || echo "0")
    if [ "$DB_SIZE" -lt 10240 ]; then
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

