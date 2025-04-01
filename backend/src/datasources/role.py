from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from src.datasources.base import DataSourceBase
from src.models.role import Role
from src.schemas.role import RoleCreate, RoleUpdate
from src.config import logger


class DataSourceRole(DataSourceBase[Role, RoleCreate, RoleUpdate]):
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Role]:
        try:
            result = await db.execute(select(self.model).filter(Role.name == name))
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"DB ERROR - Cannot get role: {e}")
            return None

    async def update_attributes(self, db: AsyncSession, *, db_obj: Role, obj_in: RoleUpdate) -> Optional[Role]:
        try:
            # Обновляем только те поля, которые были переданы
            for key, value in obj_in.dict(exclude_unset=True).items():
                setattr(db_obj, key, value)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"DB ERROR - Cannot update role's attributes: {e}")
            return None


role_datasource = DataSourceRole(Role)
