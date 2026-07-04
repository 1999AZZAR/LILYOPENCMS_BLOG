#!/bin/bash
set -e

echo "=== LilyOpenCMS Entrypoint ==="

# Run migrations/stamp
echo "Running database setup..."
python -c "
from app import create_app
from alembic.config import Config
from alembic import command

app = create_app()
with app.app_context():
    # Run all pending migrations
    try:
        alembic_cfg = Config('migrations/alembic.ini')
        command.upgrade(alembic_cfg, 'head')
        print('Alembic migrations applied to head.')
    except Exception as e:
        print(f'Alembic upgrade failed: {e}')
        # Fallback: create tables if migrations fail
        from app.extensions import db
        db.create_all()
        print('Fallback: created tables via db.create_all().')
        try:
            command.stamp(alembic_cfg, 'head')
        except Exception:
            pass
"

# Seed database (idempotent — skips if data exists)
echo "Seeding database..."
python seed.py

echo "=== Starting gunicorn ==="
exec "$@"
