from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional
from src.models.dashboard import Dashboard, DashboardBlock
from src.schemas.dashboard import DashboardCreate, DashboardBase, DashboardUpdate
from src.datasources.base import DataSourceBase


class DashboardDatasource(DataSourceBase[Dashboard, DashboardCreate, DashboardBase]):

    async def get_by_title(self, db: AsyncSession, title: str) -> Optional[Dashboard]:
        stmt = select(Dashboard).where(Dashboard.title == title)
        return (await db.execute(stmt)).scalar_one_or_none()

    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Dashboard]:
        stmt = select(Dashboard).options(selectinload(Dashboard.blocks)).offset(skip).limit(limit)
        return (await db.execute(stmt)).scalars().all()

    async def get_by_user_or_system(self, db: AsyncSession, user_id: int) -> list[Dashboard]:
        stmt = select(Dashboard).where((Dashboard.user_id == user_id) | (Dashboard.system is True))
        stmt = stmt.options(selectinload(Dashboard.blocks))
        return (await db.execute(stmt)).scalars().all()

    async def get_all(self, db: AsyncSession) -> list[Dashboard]:
        stmt = select(Dashboard).options(selectinload(Dashboard.blocks))
        return (await db.execute(stmt)).scalars().all()

    async def create(self, db: AsyncSession, obj_in: DashboardCreate, user_id: Optional[int] = None) -> Dashboard:
        db_obj = Dashboard(title=obj_in.title, description=obj_in.description, system=obj_in.system, user_id=user_id)
        db.add(db_obj)
        await db.flush()

        for block in obj_in.blocks:
            block_obj = DashboardBlock(
                title=block.title,
                type=block.type,
                unit=block.unit,
                dashboard_id=db_obj.id,
                container_id=block.container_id,
                metric_type=block.metric_type,
                prometheus_query="",  # задаётся позже через update
            )
            db.add(block_obj)

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, dashboard_id: int, update_data: DashboardUpdate) -> Dashboard:
        dashboard = await db.get(Dashboard, dashboard_id)
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(dashboard, field, value)
        await db.commit()
        await db.refresh(dashboard)
        return dashboard

    async def delete(self, db: AsyncSession, dashboard_id: int) -> None:
        dashboard = await db.get(Dashboard, dashboard_id)
        await db.delete(dashboard)
        await db.commit()


dashboard_datasource = DashboardDatasource(Dashboard)
