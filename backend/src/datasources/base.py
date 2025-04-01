from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from src.db.base import Base
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4, BaseModel
from src.config import logger


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class DataSourceBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> Optional[List[ModelType]]:
        try:
            result = await db.execute(select(self.model).offset(skip).limit(limit))
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"DB ERROR - Cannot get list of objects: {e}")
            return None

    async def get(self, db: AsyncSession, *, id: UUID4) -> Optional[ModelType]:
        try:
            result = await db.execute(select(self.model).filter(self.model.id == id))
            return result.unique().scalar_one()
        except SQLAlchemyError as e:
            logger.error(f"DB ERROR - Cannot get object: {e}")
            return None

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> Optional[ModelType]:
        try:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"DB ERROR - Cannot create object: {e}")
            return None

    async def create_without_commit(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> Optional[ModelType]:
        try:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)
            db.add(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"DB ERROR - Cannot create object: {e}")
            return None

    async def update(
        self, db: AsyncSession, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> Optional[ModelType]:
        try:
            obj_data = jsonable_encoder(obj_in)
            for field, value in obj_data.items():
                setattr(db_obj, field, value)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"DB ERROR - Cannot update object: {e}")
            return None

    async def remove(self, db: AsyncSession, *, id: UUID4) -> Optional[ModelType]:
        try:
            result = await db.execute(select(self.model).filter(self.model.id == id))
            obj = result.scalar_one_or_none()
            if obj is None:
                return None
            await db.delete(obj)
            await db.commit()
            return obj
        except SQLAlchemyError as e:
            logger.error(f"DB ERROR - Cannot remove object: {e}")
            return None
