from fastapi import APIRouter, Query, Depends
from src.services.auth import auth_service
from src.datasources.prometheus import prometheus_datasource
from src import models

router = APIRouter(prefix="/prometheus", tags=["prometheus"])


@router.get("", dependencies=[Depends(auth_service.get_current_active_user)])
async def instant_query(
    query: str = Query(..., description="PromQL expression"),
    instance: str = Query(None, description="IP сервера (node_exporter)"),
) -> dict:
    return await prometheus_datasource.query(query, instance)


@router.get("/range", dependencies=[Depends(auth_service.get_current_active_user)])
async def range_query(
    query: str = Query(...),
    instance: str = Query(...),
    start: int = Query(...),
    end: int = Query(...),
    step: int = Query(...),
) -> dict:
    return await prometheus_datasource.query_range(query, instance, start, end, step)
