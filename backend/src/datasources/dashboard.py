from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional
from src.models.dashboard import Dashboard, DashboardBlock
from src.schemas.dashboard import DashboardCreate, DashboardBase, DashboardUpdate
from src.datasources.base import DataSourceBase
from pydantic import UUID4


class DashboardDatasource(DataSourceBase[Dashboard, DashboardCreate, DashboardBase]):
    async def get_by_title(self, db: AsyncSession, title: str) -> Optional[Dashboard]:
        stmt = (
            select(Dashboard)
            .where(Dashboard.title == title)
            .options(
                selectinload(Dashboard.blocks),
                selectinload(Dashboard.user),  # <–– подгружаем связанного user
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Dashboard]:
        stmt = select(Dashboard).options(selectinload(Dashboard.blocks)).offset(skip).limit(limit)
        return (await db.execute(stmt)).scalars().all()

    async def get_by_user_or_system(self, db: AsyncSession, user_id: UUID4) -> list[Dashboard]:
        stmt = (
            select(Dashboard)
            .where((Dashboard.user_id == user_id) | (Dashboard.system.is_(True)))
            .options(
                selectinload(Dashboard.blocks),
                selectinload(Dashboard.user),  # <-- user подгружен
            )
        )
        rv = await db.execute(stmt)
        return rv.scalars().all()

    async def get_all(self, db: AsyncSession) -> list[Dashboard]:
        stmt = select(Dashboard).options(selectinload(Dashboard.blocks), selectinload(Dashboard.user))
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: DashboardCreate, user_id: Optional[UUID4] = None) -> Dashboard:
        db_obj = Dashboard(
            title=obj_in.title,
            description=obj_in.description,
            system=obj_in.system,
            user_id=user_id,
        )
        db.add(db_obj)
        await db.flush()

        # Создаём блоки (у пользовательских дашбордов prometheus_query оставляем пустым)
        for block in obj_in.blocks:
            block_obj = DashboardBlock(
                title=block.title,
                type=block.type,
                unit=block.unit,
                dashboard_id=db_obj.id,
                container_id=block.container_id,
                metric_type=block.metric_type,
                prometheus_query=block.prometheus_query or "",
            )
            db.add(block_obj)

        await db.commit()
        # После коммита явно сделаем новый SELECT, чтобы снова подгрузить блоки и user
        stmt = (
            select(Dashboard)
            .where(Dashboard.id == db_obj.id)
            .options(
                selectinload(Dashboard.blocks),
                selectinload(Dashboard.user),
            )
        )
        fresh = (await db.execute(stmt)).scalar_one()
        return fresh

    async def update(self, db: AsyncSession, dashboard_id: UUID4, update_data: DashboardUpdate) -> Dashboard:
        dashboard = await db.get(Dashboard, dashboard_id)
        if not dashboard:
            return None  # или поднять исключение, если нужно
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
