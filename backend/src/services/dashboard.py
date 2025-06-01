from typing import List
from src.datasources.dashboard import dashboard_datasource
from src.schemas.dashboard import DashboardCreate, DashboardUpdate, Dashboard
from src.models.dashboard import Dashboard as DashboardModel
from src.db.database import get_db
from src import models
from pydantic import UUID4
from src.constants.roles import Role
from sqlalchemy import select
from sqlalchemy.orm import selectinload


class DashboardService:
    async def get_user_dashboards(self, user: models.User) -> List[Dashboard]:
        async with get_db() as db:
            if user.has_role([Role.ADMIN["name"], Role.SUPER_ADMIN["name"]]):
                all_ds = await dashboard_datasource.get_all(db)
            else:
                all_ds = await dashboard_datasource.get_by_user_or_system(db, user_id=user.id)

            result: List[Dashboard] = []
            for d in all_ds:
                d.owner_username = d.user.username if d.user else None
                result.append(Dashboard.from_orm(d))
            return result

    async def get_dashboard_by_id(self, dash_id: UUID4) -> Dashboard | None:
        async with get_db() as db:
            return await dashboard_datasource.get_by_id(db, dash_id)

    async def create_dashboard(self, dashboard_in: DashboardCreate, user_id: UUID4) -> Dashboard:
        async with get_db() as db:
            created: Dashboard = await dashboard_datasource.create(db, obj_in=dashboard_in, user_id=user_id)
            if created.user:
                created.owner_username = created.user.username
            else:
                created.owner_username = None

            return Dashboard.from_orm(created)

    async def update_dashboard(self, dashboard_id: UUID4, data: DashboardUpdate) -> Dashboard:
        async with get_db() as db:
            # 1) Сначала делаем сам UPDATE (DAO.update)
            updated = await dashboard_datasource.update(db, dashboard_id, data)
            if not updated:
                return None  # или бросаем HTTPException выше

            # 2) Затем заново «вытаскиваем» этот дашборд вместе с его user и blocks:
            stmt = (
                select(DashboardModel)
                .where(DashboardModel.id == dashboard_id)
                .options(
                    selectinload(DashboardModel.blocks),
                    selectinload(DashboardModel.user),
                )
            )
            fresh = (await db.execute(stmt)).scalar_one_or_none()
            if not fresh:
                return None

            # 3) Заполняем owner_username из freshly загруженного `user`
            fresh.owner_username = fresh.user.username if fresh.user else None

            # 4) Превращаем в Pydantic-схему и возвращаем
            return Dashboard.from_orm(fresh)

    async def delete_dashboard(self, dashboard_id: UUID4) -> None:
        async with get_db() as db:
            await dashboard_datasource.delete(db, dashboard_id)

    async def get_dashboard_by_title(self, title: str) -> Dashboard | None:
        async with get_db() as db:
            d: Dashboard = await dashboard_datasource.get_by_title(db, title)
            if not d:
                return None
            if d.user:
                d.owner_username = d.user.username
            else:
                d.owner_username = None
            return Dashboard.from_orm(d)


dashboard_service = DashboardService()
