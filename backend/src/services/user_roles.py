from src.errors.exceptions import CoreException
from src.datasources.role import role_datasource
from src.datasources.user import user_datasource
from src.datasources.user_role import user_role_datasource
from src.db.database import get_db
from src import schemas, models
from typing import List
from src.constants.roles import Role
from pydantic.types import UUID4


class UserRoleService:
    @staticmethod
    async def assign_role(user_role_in: schemas.UserRoleCreate, current_user: models.User) -> schemas.UserRole:
        async with get_db() as db:
            requested_role = await role_datasource.get(db, id=user_role_in.role_id)
            if not requested_role:
                raise CoreException("errors.roles.role_does_not_exist")

            if (
                requested_role.name == Role.SUPER_ADMIN["name"] or requested_role.name == Role.ADMIN["name"]
            ) and not current_user.has_role([Role.SUPER_ADMIN["name"]]):
                raise CoreException("errors.roles.admin_assign_not_enough_permissions")

            user = await user_datasource.get(db, id=user_role_in.user_id)
            if not user:
                raise CoreException("errors.users.user_not_exists")

            user_role = await user_role_datasource.get_by_user_and_role(
                db, user_id=user_role_in.user_id, role_id=user_role_in.role_id
            )
            if user_role:
                raise CoreException("errors.roles.user_already_have_role")

            user_role = await user_role_datasource.create(db, obj_in=user_role_in)

            return user_role

    @staticmethod
    async def get_user_roles(user_id: UUID4) -> schemas.UserRoles:
        async with get_db() as db:
            roles = await user_role_datasource.get_by_user_id(db, user_id=user_id)
            return roles

    @staticmethod
    async def delete_user_role(
        user_id: UUID4, user_role_in: schemas.UserRoleUpdate, current_user: models.User
    ) -> schemas.UserRole:
        async with get_db() as db:
            requested_role = await role_datasource.get(db, id=user_role_in.role_id)
            if not requested_role:
                raise CoreException("errors.roles.role_does_not_exist")

            if requested_role.name == Role.SUPER_ADMIN["name"] and not current_user.has_role(
                [Role.SUPER_ADMIN["name"]]
            ):
                raise CoreException("errors.roles.role_delete_not_enough_permissions")

            user_role = await user_role_datasource.get_by_user_and_role(
                db, user_id=user_id, role_id=user_role_in.role_id
            )
            if not user_role:
                raise CoreException("errors.roles.role_does_not_exist")

            user_role = await user_role_datasource.remove(db, id=user_role.id)
            return user_role


user_role_service = UserRoleService()
