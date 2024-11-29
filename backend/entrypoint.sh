#!/bin/bash
set -e

# Run Alembic migrations
alembic upgrade head
exec "$@"