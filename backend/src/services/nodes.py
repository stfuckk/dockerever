from src.datasources.prometheus import prometheus_datasource
from src import schemas


class NodeService:
    async def get_available_nodes(self) -> list[schemas.NodeInfo]:
        return await prometheus_datasource.get_node_targets()


node_service = NodeService()
