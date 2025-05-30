from src.models.dashboard import DashboardBlock
from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.dashboard import DashboardBlockCreate, DashboardBlockUpdate


METRIC_QUERIES = {
    "cpu": lambda cid: f'rate(container_cpu_usage_seconds_total{{id=~".*{cid}.*"}}[5m]) * 100',
    "memory": lambda cid: f'container_memory_usage_bytes{{id=~".*{cid}.*"}} / 1024 / 1024',
    "network": lambda cid: f'rate(container_network_receive_bytes_total{{id=~".*{cid}.*"}}[5m]) / 1024',
    "disk": lambda cid: f'container_fs_usage_bytes{{id=~".*{cid}.*"}} / 1024 / 1024 / 1024',
}


def build_promql(container_id: str, metric_type: str) -> str:
    return METRIC_QUERIES[metric_type](container_id)


class DashboardBlockService:
    async def create_block(self, dashboard_id: int, block: DashboardBlockCreate) -> DashboardBlock:
        async with get_db() as db:
            query = (
                build_promql(block.container_id, block.metric_type) if block.container_id and block.metric_type else ""
            )
            db_obj = DashboardBlock(
                dashboard_id=dashboard_id,
                title=block.title,
                type=block.type,
                unit=block.unit,
                container_id=block.container_id,
                metric_type=block.metric_type,
                prometheus_query=query,
            )
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj

    async def update_block(self, block_id: int, update_data: DashboardBlockUpdate) -> DashboardBlock:
        async with get_db() as db:
            block = await db.get(DashboardBlock, block_id)
            for field, value in update_data.dict(exclude_unset=True).items():
                setattr(block, field, value)
            if block.container_id and block.metric_type:
                block.prometheus_query = build_promql(block.container_id, block.metric_type)
            await db.commit()
            await db.refresh(block)
            return block

    async def delete_block(self, block_id: int) -> None:
        async with get_db() as db:
            block = await db.get(DashboardBlock, block_id)
            await db.delete(block)
            await db.commit()


dashboard_block_service = DashboardBlockService()
