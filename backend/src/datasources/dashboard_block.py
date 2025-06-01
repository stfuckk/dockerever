from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.dashboard import DashboardBlock
from src.schemas import DashboardBlockCreate, DashboardBlockUpdate
from src.datasources.base import DataSourceBase
from typing import Optional
from pydantic import UUID4


class DashboardBlockDatasource(DataSourceBase[DashboardBlock, DashboardBlockCreate, DashboardBlockUpdate]):
    async def create(self, db: AsyncSession, dashboard_id: UUID4, obj_in: DashboardBlockCreate) -> DashboardBlock:
        db_obj = DashboardBlock(
            title=obj_in.title,
            type=obj_in.type,
            unit=obj_in.unit,
            container_id=obj_in.container_id,
            metric_type=obj_in.metric_type,
            prometheus_query=obj_in.prometheus_query,
            dashboard_id=dashboard_id,
        )
        db.add(db_obj)
        await db.flush()

        # После flush у нас заполнен db_obj.id, теперь делаем commit и снова selectinload,
        # если потребуется: но пока нам достаточно просто вернуть db_obj
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_id(self, db: AsyncSession, block_id: UUID4) -> Optional[DashboardBlock]:
        stmt = select(DashboardBlock).where(DashboardBlock.id == block_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, db: AsyncSession, block_id: UUID4, obj_in: DashboardBlockUpdate) -> DashboardBlock:
        block = await db.get(DashboardBlock, block_id)
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(block, field, value)
        await db.commit()
        await db.refresh(block)
        return block

    async def delete(self, db: AsyncSession, block_id: UUID4) -> None:
        block = await db.get(DashboardBlock, block_id)
        if block:
            await db.delete(block)
            await db.commit()


dashboard_block_datasource = DashboardBlockDatasource(DashboardBlock)
