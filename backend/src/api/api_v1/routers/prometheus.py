from fastapi import APIRouter, Query, Depends
from src.datasources.prometheus import prometheus_datasource
from src import models
from src.services.auth import auth_service
import httpx
from src.config import PROMETHEUS_URL

router = APIRouter(prefix="/prometheus", tags=["prometheus"])


@router.get("")
async def query_prometheus(
    query: str = Query(..., description="PromQL expression"),
    instance: str = Query(None, description="IP сервера (node_exporter)"),
    current_user: models.User = Depends(auth_service.get_current_active_user),
) -> dict:
    return await prometheus_datasource.query(query, instance)


@router.get("/range")
async def prometheus_range(query: str, instance: str, start: int, end: int, step: int) -> dict:
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{PROMETHEUS_URL}/api/v1/query_range",
            params={
                "query": query,
                "start": start,
                "end": end,
                "step": step,
            },
        )
    return res.json()
