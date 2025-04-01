from src import datasources, schemas
from src.constants.roles import Role
import src.config as settings
from sqlalchemy.ext.asyncio import AsyncSession


async def __create_role_if_not_exists(db: AsyncSession, role: dict) -> None:
    assert "name" in role
    assert "description_ru" in role
    assert "description_en" in role

    role_db = await datasources.role_datasource.get_by_name(db, name=role["name"])
    if not role_db:
        role_in = schemas.RoleCreate(**role)
        await datasources.role_datasource.create(db, obj_in=role_in)
    else:
        update_needed = False
        update_data = {}

        for key in role.keys():
            if getattr(role_db, key) != role[key]:
                update_needed = True
                update_data[key] = role[key]

        if update_needed:
            role_update = schemas.RoleUpdate(**update_data)
            await datasources.role_datasource.update_attributes(db, db_obj=role_db, obj_in=role_update)


async def init_db(db: AsyncSession) -> None:
    # Create Roles If They Don't Exist

    for role_name in Role.roles.keys():
        await __create_role_if_not_exists(db, Role.roles[role_name])

    # Create Super Admin Account
    user = await datasources.user_datasource.get_by_username(db, username=settings.SUPER_ADMIN_USERNAME)

    if not user:
        user_in = schemas.UserCreateSchema(
            username=settings.SUPER_ADMIN_USERNAME, password=settings.SUPER_ADMIN_PASSWORD.get_secret_value()
        )
        user = await datasources.user_datasource.create(db, obj_in=user_in)

    # Assign super_admin role to user
    super_admin_role = await datasources.role_datasource.get_by_name(db, name=Role.SUPER_ADMIN["name"])
    if super_admin_role and user:
        user_role = await datasources.user_role_datasource.get_by_user_and_role(
            db, user_id=user.id, role_id=super_admin_role.id
        )
        if not user_role:
            user_role_in = schemas.UserRoleCreate(user_id=user.id, role_id=super_admin_role.id)
            await datasources.user_role_datasource.create(db, obj_in=user_role_in)
