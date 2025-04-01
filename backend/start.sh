#!/bin/bash
pdm run python pre_start.py
pdm run alembic upgrade head
pdm run python init_data.py
pdm run uvicorn src.main:app --host 0.0.0.0 --reload
