from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declared_attr, Mapped, mapped_column, DeclarativeBase
import uuid
from sqlalchemy.dialects.postgresql import UUID
from contextlib import asynccontextmanager

from typing import Annotated, AsyncGenerator
from datetime import datetime
from dotenv import load_dotenv

from src.config import get_db_url, logger

load_dotenv()

DATABASE_URL = get_db_url().replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(DATABASE_URL)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


@asynccontextmanager
async def get_db() -> AsyncGenerator:
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()


uuid_pk = Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=datetime.now)]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
str_null_true = Annotated[str, mapped_column(nullable=True)]


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    id: Mapped[uuid_pk]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
