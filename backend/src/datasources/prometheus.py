import httpx
from src.config import PROMETHEUS_URL
from src import schemas
import re


class PrometheusDatasource:
    async def get_node_targets(self) -> list[schemas.NodeInfo]:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{PROMETHEUS_URL}/api/v1/targets")
            data = res.json()["data"]["activeTargets"]

        result = []
        for target in data:
            if "node_exporter" in target["labels"].get("job"):
                ip = target["discoveredLabels"].get("__address__")
                # Попытка получить hostname
                hostname = target["labels"].get("instance") or ""
                result.append(schemas.NodeInfo(ip=ip, hostname=hostname))
        return result

    def _inject_instance(self, query: str, instance: str) -> str:
        if not instance or f'instance="{instance}"' in query:
            return query

        # Ищем выражения внутри скобок после sum by(...) (
        if match := re.search(r"\b(sum|avg|max|min)\s+by\([^)]*\)\s*\(([^()]+)\)", query):
            metric_expr = match.group(2)
            if "{" in metric_expr:
                metric_expr = re.sub(r"\{", f'{{instance="{instance}", ', metric_expr, count=1)
            else:
                metric_expr = re.sub(r"(\w+)", r'\1{instance="' + instance + '"}', metric_expr, count=1)

            return query.replace(match.group(2), metric_expr)

        return query

    async def query(self, query: str, instance: str = "") -> dict:
        query = self._inject_instance(query, instance)

        async with httpx.AsyncClient() as client:
            res = await client.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
        return res.json()


prometheus_datasource = PrometheusDatasource()
