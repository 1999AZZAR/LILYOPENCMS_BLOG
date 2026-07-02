#!/bin/bash
set -e

echo "=== LilyOpenCMS Entrypoint ==="

# Run migrations/stamp
echo "Running database setup..."
python -c "
from app import create_app
from alembic.config import Config
from alembic import command
from sqlalchemy import text

app = create_app()
with app.app_context():
    from app.extensions import db
    # Create tables if they don't exist (first run)
    db.create_all()
    # Stamp alembic head so future migrations work
    try:
        alembic_cfg = Config('migrations/alembic.ini')
        command.stamp(alembic_cfg, 'head')
        print('Alembic stamped to head.')
    except Exception as e:
        print(f'Alembic stamp skipped: {e}')
"

# Seed database (idempotent — skips if data exists)
echo "Seeding database..."
python seed.py

echo "=== Starting gunicorn ==="
exec "$@"
