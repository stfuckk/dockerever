from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from src.utils.security import get_password_hash, verify_password
from src.datasources.base import DataSourceBase
from src.models.user import User
from src.schemas.user import UserCreateSchema, UserUpdateSchema
from src.datasources.user_role import user_role_datasource
from src.config import logger
from src.errors.exceptions import CoreException


class DataSourceUser(DataSourceBase[User, UserCreateSchema, UserUpdateSchema]):
    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        try:
            result = await db.execute(
                select(self.model)
                .options(selectinload(User.roles))
                .options(selectinload(User.user_roles))
                .filter(User.username == username)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Cannot get user by username: {e}")
            return None

    async def create(self, db: AsyncSession, *, obj_in: UserCreateSchema) -> Optional[User]:
        try:
            db_obj = User(
                username=obj_in.username,
                hashed_password=get_password_hash(obj_in.password.get_secret_value()),
            )
            db.add(db_obj)
            await db.flush()
            await user_role_datasource.assign_base_role(db, user_id=db_obj.id)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"Cannot create user: {e}")
            return None

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: User,
        obj_in: Union[UserUpdateSchema, Dict[str, Any]],
    ) -> Optional[User]:
        try:
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.model_dump(exclude_unset=True)

            if not verify_password(update_data["prev_password"].get_secret_value(), db_obj.hashed_password):
                raise CoreException("errors.auth.incorrect_credentials")

            if "password" in update_data:
                hashed_password = get_password_hash(update_data["password"].get_secret_value())
                del update_data["password"]
                update_data["hashed_password"] = hashed_password
            return await super().update(db, db_obj=db_obj, obj_in=update_data)
        except SQLAlchemyError as e:
            logger.error(f"Cannot update user: {e}")
            return None

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Optional[List[User]]:
        try:
            result = await db.execute(select(self.model).offset(skip).limit(limit))
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Cannot get list of users: {e}")
            return None

    async def authenticate(self, db: AsyncSession, *, username: str, password: str) -> Optional[User]:
        try:
            user = await self.get_by_username(db, username=username)
            if not user:
                return None
            if not verify_password(password, user.hashed_password):
                return None
            return user
        except Exception as e:
            logger.error(f"Cannot authentificate user: {e}")
            return None

    async def is_active(self, user: User) -> bool:
        return user.is_active


user_datasource = DataSourceUser(User)
