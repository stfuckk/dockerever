from src.datasources.dashboard import dashboard_datasource
from src.schemas.dashboard import Dashboard, DashboardCreate, DashboardUpdate
from src.db.database import get_db
from src import models
from pydantic import UUID4
from src.constants.roles import Role


class DashboardService:
    async def get_user_dashboards(self, user: models.User) -> list[Dashboard]:
        async with get_db() as db:
            if user.has_role([Role.ADMIN["name"], Role.SUPER_ADMIN["name"]]):
                return await dashboard_datasource.get_all(db)
            return await dashboard_datasource.get_by_user_or_system(db, user_id=user.id)

    async def create_dashboard(self, dashboard_in: DashboardCreate, user_id: UUID4) -> Dashboard:
        async with get_db() as db:
            return await dashboard_datasource.create(db, obj_in=dashboard_in, user_id=user_id)

    async def update_dashboard(self, dashboard_id: UUID4, data: DashboardUpdate) -> Dashboard:
        async with get_db() as db:
            return await dashboard_datasource.update(db, dashboard_id, data)

    async def delete_dashboard(self, dashboard_id: UUID4) -> None:
        async with get_db() as db:
            await dashboard_datasource.delete(db, dashboard_id)


dashboard_service = DashboardService()
