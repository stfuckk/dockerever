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
        if not instance:
            return query
        # Если есть label-селектор {...}, то вставляем instance в первый
        if "{" in query:
            return re.sub(r"\{", f'{{instance="{instance}",', query, count=1)
        # Иначе просто добавляем лейбл
        return f'{query}{{instance="{instance}"}}'

    async def query(self, query: str, instance: str = "") -> dict:
        query = self._inject_instance(query, instance)

        async with httpx.AsyncClient() as client:
            res = await client.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
        return res.json()

    async def query_range(
        self,
        query: str,
        instance: str,
        start: int,
        end: int,
        step: int,
    ) -> dict:
        params = {"query": query, "start": start, "end": end, "step": step}
        if instance:
            params["instance"] = instance
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{PROMETHEUS_URL}/api/v1/query_range", params=params)
        return res.json()


prometheus_datasource = PrometheusDatasource()
