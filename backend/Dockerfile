FROM python:3.12

WORKDIR /app

COPY ./pyproject.toml ./pdm.lock ./
RUN pip install pdm && pdm install

COPY ./alembic ./alembic
COPY ./alembic.ini ./alembic.ini
COPY src ./src

ENV PATH="/app/.venv/bin:${PATH}"

CMD ["pdm", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--reload"]