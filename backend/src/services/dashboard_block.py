from typing import Optional
from src.models.dashboard import DashboardBlock
from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.dashboard import DashboardBlockCreate, DashboardBlockUpdate

# Для cAdvisor используем метрики:
# - CPU:   rate(container_cpu_usage_seconds_total{id=~".*<container_id>.*"}[5m]) * 100
# - Memory usage (в ГБ): container_memory_usage_bytes{id=~".*<container_id>.*"} / 1024 / 1024 / 1024
# - Memory limit (в ГБ):  container_spec_memory_limit_bytes{id=~".*<container_id>.*"} / 1024 / 1024 / 1024
# - Network in:  rate(container_network_receive_bytes_total{id=~".*<container_id>.*"}[5m]) / 1024 / 1024
# - Network out: rate(container_network_transmit_bytes_total{id=~".*<container_id>.*"}[5m]) / 1024 / 1024
# - Disk usage:  container_fs_usage_bytes{id=~".*<container_id>.*"} / 1024 / 1024 / 1024

METRIC_QUERIES = {
    "cpu": lambda cid: f'rate(container_cpu_usage_seconds_total{{id=~"/docker/{cid}"}}[5m]) * 100',
    "memory": lambda cid: f'container_memory_usage_bytes{{id=~"/docker/{cid}"}} / 1024 / 1024 / 1024',
    "memory_limit": lambda cid: f'container_spec_memory_limit_bytes{{id=~"/docker/{cid}"}} / 1024 / 1024 / 1024',
    "network_in": lambda cid: f'rate(container_network_receive_bytes_total{{id=~"/docker/{cid}"}}[5m]) / 1024 / 1024',
    "network_out": lambda cid: f'rate(container_network_transmit_bytes_total{{id=~"/docker/{cid}"}}[5m]) / 1024 / 1024',
    "disk": lambda cid: f'container_fs_usage_bytes{{id=~"/docker/{cid}"}} / 1024 / 1024 / 1024',
}


def build_promql(container_id: str, metric_type: str) -> str:
    """
    Собираем PromQL по типу метрики и идентификатору контейнера.
    Для memory_limit не будет вставляться в prometheus_query — это нужно только для Y-max.
    """
    if metric_type not in METRIC_QUERIES:
        return ""
    return METRIC_QUERIES[metric_type](container_id)


class DashboardBlockService:
    async def create_block(self, dashboard_id: str, block: DashboardBlockCreate) -> DashboardBlock:
        async with get_db() as db:
            # Построим prometheus_query:
            promql = build_promql(block.container_id, block.metric_type or "")
            db_obj = DashboardBlock(
                dashboard_id=dashboard_id,
                title=block.title,
                type=block.type,
                unit=block.unit,
                container_id=block.container_id,
                metric_type=block.metric_type,
                prometheus_query=promql or "",
            )
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj

    async def update_block(self, block_id: str, update_data: DashboardBlockUpdate) -> Optional[DashboardBlock]:
        async with get_db() as db:
            block = await db.get(DashboardBlock, block_id)
            if not block:
                return None
            for field, value in update_data.dict(exclude_unset=True).items():
                setattr(block, field, value)
            # Если есть container_id и metric_type (для блоков всегда требуется),
            # пересоздадим prometheus_query
            if block.container_id and block.metric_type:
                block.prometheus_query = build_promql(block.container_id, block.metric_type)
            await db.commit()
            await db.refresh(block)
            return block

    async def delete_block(self, block_id: str) -> None:
        async with get_db() as db:
            block = await db.get(DashboardBlock, block_id)
            if block:
                await db.delete(block)
                await db.commit()


dashboard_block_service = DashboardBlockService()
