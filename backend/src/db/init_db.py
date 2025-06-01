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
            username=settings.SUPER_ADMIN_USERNAME,
            password=settings.SUPER_ADMIN_PASSWORD.get_secret_value(),
            must_change_password=True,
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


async def __create_main_dashboard(db: AsyncSession) -> None:
    existing = await datasources.dashboard_datasource.get_by_title(db, title="Основной серверный мониторинг")
    if existing:
        return

    dashboard = schemas.DashboardCreate(
        title="Основной серверный мониторинг",
        description="Автоматический дашборд для серверных метрик",
        system=True,
        blocks=[
            schemas.DashboardBlockCreate(
                title="Загрузка CPU",
                type="diagram",
                prometheus_query="""
                    100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
                """,
                unit="%",
                metric_type="cpu",
            ),
            schemas.DashboardBlockCreate(
                title="Использование памяти",
                type="diagram",
                prometheus_query="""
                    (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / 1024 / 1024 / 1024
                """,
                unit="ГБ",
                metric_type="memory",
            ),
            schemas.DashboardBlockCreate(
                title="Входящий трафик сети",
                type="diagram",
                prometheus_query="""
                    sum by(instance) (rate(node_network_receive_bytes_total[5m])) / 1024 / 1024
                """,
                unit="МБ/с",
                metric_type="network",
            ),
            schemas.DashboardBlockCreate(
                title="Исходящий трафик сети",
                type="diagram",
                prometheus_query="""
                    sum by(instance) (rate(node_network_transmit_bytes_total[5m])) / 1024 / 1024
                """,
                unit="МБ/с",
                metric_type="network",
            ),
            schemas.DashboardBlockCreate(
                title="Использование дисков",
                type="table",
                prometheus_query="""
                    node_filesystem_size_bytes{mountpoint!~"/(proc|sys|dev|run)"}
                    - node_filesystem_free_bytes{mountpoint!~"/(proc|sys|dev|run)"}
                """,
                unit="используется из общего",
                metric_type="disk",
            ),
        ],
    )

    await datasources.dashboard_datasource.create(db, obj_in=dashboard)
