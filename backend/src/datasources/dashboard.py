from src.datasources.base import DataSourceBase
from src.models.dashboard import Dashboard
from src.schemas.dashboard import (
    DashboardCreate,
    DashboardBase,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.dashboard import DashboardBlock as DashboardBlockModel
from typing import Optional
from sqlalchemy.orm import selectinload


class DashboardDatasource(DataSourceBase[Dashboard, DashboardCreate, DashboardBase]):
    async def get_by_title(self, db: AsyncSession, title: str) -> Optional[Dashboard]:
        stmt = select(Dashboard).where(Dashboard.title == title)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Dashboard]:
        stmt = select(self.model).options(selectinload(self.model.blocks)).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: DashboardCreate) -> Dashboard:
        db_obj = Dashboard(title=obj_in.title, description=obj_in.description, system=obj_in.system)
        db.add(db_obj)
        await db.flush()  # получаем ID

        for block in obj_in.blocks:
            block_obj = DashboardBlockModel(
                title=block.title,
                type=block.type,
                prometheus_query=block.prometheus_query,
                unit=block.unit,
                dashboard_id=db_obj.id,
            )
            db.add(block_obj)

        await db.commit()
        await db.refresh(db_obj)
        return db_obj


dashboard_datasource = DashboardDatasource(Dashboard)
