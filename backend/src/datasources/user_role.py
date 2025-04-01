from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from pydantic.types import UUID4
from src.datasources.base import DataSourceBase
from src.datasources.role import role_datasource
from src.models.user_role import UserRole
from src.schemas.user_role import UserRoleCreate, UserRoleUpdate
from src.config import logger


class DataSourceUserRole(DataSourceBase[UserRole, UserRoleCreate, UserRoleUpdate]):
    async def get_by_user_id(self, db: AsyncSession, *, user_id: UUID4) -> Optional[List[UserRole]]:
        try:
            result = await db.execute(select(UserRole).filter(UserRole.user_id == user_id))
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Cannot get list of roles by user_id: {e}")
            return None

    async def get_by_user_and_role(self, db: AsyncSession, *, user_id: UUID4, role_id: UUID4) -> Optional[UserRole]:
        try:
            result = await db.execute(select(UserRole).filter(UserRole.user_id == user_id, UserRole.role_id == role_id))
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Cannot get role by user_id and role_id: {e}")
            return None

    async def assign_base_role(self, db: AsyncSession, *, user_id: UUID4) -> Optional[UserRole]:
        try:
            role_in = await role_datasource.get_by_name(db, name="User")

            if role_in:
                user_role_in = {
                    "role_id": role_in.id,
                    "user_id": user_id,
                }
            user_role = UserRoleCreate.model_construct(**user_role_in)

            user_role_result = await super().create_without_commit(db, obj_in=user_role)

            return user_role_result
        except SQLAlchemyError as e:
            logger.error(f"Cannot assign base user role: {e}")
            return None


user_role_datasource = DataSourceUserRole(UserRole)
