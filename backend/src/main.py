import os
from fastapi import FastAPI
from typing import AsyncGenerator
from sqlalchemy.future import select
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from src.utils.expired_tokens import start_scheduler
from src.api.api_v1.api import api_router
import src.config as settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    start_scheduler()
    yield


app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/api/docs",
)

if settings.CORS_MODE == "cors":
    app.add_middleware(
        CORSMiddleware,  # noqa
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
def health() -> dict:
    return {"message": "ok!"}
