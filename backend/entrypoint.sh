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
    
    # Check if database is empty (check if instructors table has data)
    # Use Python to check since it's available and works cross-platform
    HAS_DATA=$(uv run python -c "
import sqlite3
try:
    conn = sqlite3.connect('/app/data/data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM instructors')
    count = cursor.fetchone()[0]
    conn.close()
    print('yes' if count > 0 else 'no')
except:
    print('no')
" 2>/dev/null || echo "no")
    
    if [ "$HAS_DATA" = "no" ]; then
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

