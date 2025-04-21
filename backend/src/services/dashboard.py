from src.datasources.dashboard import dashboard_datasource
from src.schemas.dashboard import Dashboard, DashboardCreate
from src.db.database import get_db


class DashboardService:
    async def get_all_dashboards(self) -> list[Dashboard]:
        async with get_db() as db:
            dashboards = await dashboard_datasource.get_multi(db)
            return dashboards

    async def get_dashboard_by_title(self, title: str) -> Dashboard | None:
        async with get_db() as db:
            return await dashboard_datasource.get_by_title(db, title)

    async def create_dashboard(self, dashboard_in: DashboardCreate) -> Dashboard:
        async with get_db() as db:
            return await dashboard_datasource.create(db, obj_in=dashboard_in)


dashboard_service = DashboardService()
