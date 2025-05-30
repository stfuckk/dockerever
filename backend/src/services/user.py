from src.errors.exceptions import CoreException
from src.datasources.user import user_datasource
from src.db.database import get_db
from src import schemas, models
from src.constants.roles import Role
from pydantic import UUID4
from typing import List, Optional, Tuple


class UserService:
    @staticmethod
    async def get_users(
        skip: int = 0, limit: int = 100, search: Optional[str] = None
    ) -> Tuple[List[schemas.User], int]:
        async with get_db() as db:
            return await user_datasource.get_multi(db, skip=skip, limit=limit, search=search)

    @staticmethod
    async def update_user(
        user_id: UUID4, update_data: schemas.UserUpdateSchema, current_user: models.User
    ) -> schemas.User:
        async with get_db() as db:
            user = await user_datasource.get(db, id=user_id)
            if update_data.username and update_data.username != user.username:
                existing = await user_datasource.get_by_username(db, username=update_data.username)
                if existing and existing.id != user_id:
                    raise CoreException("errors.user.username_exists")

            if not user:
                raise CoreException("errors.user.user_not_exists")
            if (
                not current_user.has_role([Role.ADMIN["name"], Role.SUPER_ADMIN["name"]])
            ) and user.id != current_user.id:
                raise CoreException("errors.auth.not_enough_permissions")
            if current_user.has_role([Role.ADMIN["name"]]) and user.has_role([Role.SUPER_ADMIN["name"]]):
                raise CoreException("errors.auth.not_enough_permissions")

            is_admin = False
            if (
                current_user.has_role([Role.SUPER_ADMIN["name"]]) or current_user.has_role([Role.ADMIN["name"]])
            ) and user.id != current_user.id:
                is_admin = True

            updated_user = await user_datasource.update(db, db_obj=user, obj_in=update_data, is_admin_update=is_admin)
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
            must_change_password=current_user.must_change_password,
        )
        return user_data

    @staticmethod
    async def get_specific_user(user_id: UUID4) -> schemas.User:
        async with get_db() as db:
            user = await user_datasource.get(db, id=user_id)
            return user

    @staticmethod
    async def delete_user(user_id: UUID4, current_user: models.User) -> schemas.User:
        if user_id == current_user.id:
            raise CoreException("errors.user.cannot_delete_self")
        async with get_db() as db:
            user_to_delete = await user_datasource.get(db, id=user_id)
            if not user_to_delete:
                raise CoreException("errors.user.user_not_exists")

            if not current_user.has_role([Role.ADMIN["name"], Role.SUPER_ADMIN["name"]]):
                raise CoreException("errors.auth.not_enough_permissions")

            if current_user.has_role([Role.ADMIN["name"]]) and user_to_delete.has_role(
                [Role.ADMIN["name"], Role.SUPER_ADMIN["name"]]
            ):
                raise CoreException("errors.auth.not_enough_permissions")
            await user_datasource.remove(db, id=user_id)


user_service = UserService()
