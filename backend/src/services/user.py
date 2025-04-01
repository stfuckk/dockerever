from src.errors.exceptions import CoreException
from src.datasources.user import user_datasource
from src.db.database import get_db
from src import schemas, models
from src.constants.roles import Role
from src.utils.security import verify_password
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import UUID4
from typing import List


# TODO: Добавить CoreExceptions для пользователей - проверки полей и действий
class UserService:
    @staticmethod
    async def get_users(skip: int = 0, limit: int = 100) -> List[schemas.User]:
        async with get_db() as db:
            users = await user_datasource.get_multi(
                db,
                skip=skip,
                limit=limit,
            )
            if users is None:
                return []
            return users

    @staticmethod
    async def update_user(
        user_id: UUID4, update_data: schemas.UserUpdateSchema, current_user: models.User
    ) -> schemas.User:
        async with get_db() as db:
            user = await user_datasource.get(db, id=user_id)
            if not user:
                raise CoreException("errors.user.user_not_exists")
            if current_user.has_role([Role.USER["name"]]) and user.id != current_user.id:
                raise CoreException("errors.auth.not_enough_permissions")
            if current_user.has_role([Role.ADMIN["name"]]) and user.has_role([Role.SUPER_ADMIN["name"]]):
                raise CoreException("errors.auth.not_enough_permissions")

            updated_user = await user_datasource.update(db, db_obj=user, obj_in=update_data)
            return updated_user

    @staticmethod
    async def create_user(user_in: schemas.UserCreateSchema) -> schemas.User:
        async with get_db() as db:
            user = await user_datasource.get_by_username(db, username=user_in.username)
            if user:
                raise CoreException("errors.user.username_exists")
            user = await user_datasource.create(db, obj_in=user_in)
            return user

    @staticmethod
    async def get_user(current_user: models.User) -> schemas.User:
        user_data = schemas.User(
            id=current_user.id,
            username=current_user.username,
            is_active=current_user.is_active,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at,
            roles=current_user.roles,
        )
        return user_data

    @staticmethod
    async def get_specific_user(user_id: UUID4) -> schemas.User:
        async with get_db() as db:
            user = await user_datasource.get(db, id=user_id)
            return user


user_service = UserService()
