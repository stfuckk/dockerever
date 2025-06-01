from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional
from datetime import datetime

from src.datasources.docker import docker_datasource
from src.services.auth import auth_service
from src import models

router = APIRouter(prefix="/docker", tags=["docker"])


@router.get("/containers")
def list_containers(
    search: str = "",
    current_user: models.User = Depends(auth_service.get_current_active_user),
) -> dict:
    result = {"containers": docker_datasource.list_containers(search)}
    return result


@router.post("/containers/{container_id}/start")
def start_container(
    container_id: str, current_user: models.User = Depends(auth_service.get_current_active_user)
) -> dict:
    try:
        docker_datasource.start_container(container_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Не удалось запустить контейнер: {e}")
    return {"status": "started"}


@router.post("/containers/{container_id}/stop")
def stop_container(
    container_id: str, current_user: models.User = Depends(auth_service.get_current_active_user)
) -> dict:
    try:
        docker_datasource.stop_container(container_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Не удалось остановить контейнер: {e}")
    return {"status": "stopped"}


@router.delete("/containers/{container_id}")
def remove_container(
    container_id: str, current_user: models.User = Depends(auth_service.get_current_active_user)
) -> dict:
    try:
        docker_datasource.remove_container(container_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Не удалось удалить контейнер: {e}")
    return {"status": "removed"}


@router.get("/containers/{container_id}/logs")
def get_logs(
    container_id: str,
    start_date: Optional[str] = Query(None, description="Дата начала в формате YYYY-MM-DD"),
    start_time: Optional[str] = Query(None, description="Время начала в формате HH:MM"),
    end_date: Optional[str] = Query(None, description="Дата окончания в формате YYYY-MM-DD"),
    end_time: Optional[str] = Query(None, description="Время окончания в формате HH:MM"),
    current_user: models.User = Depends(auth_service.get_current_active_user),
) -> dict:
    try:
        since_ts = None
        until_ts = None

        if start_date and start_time:
            dt_start = datetime.fromisoformat(f"{start_date}T{start_time}:00")
            since_ts = int(dt_start.timestamp())

        if end_date and end_time:
            dt_end = datetime.fromisoformat(f"{end_date}T{end_time}:00")
            until_ts = int(dt_end.timestamp())

        logs_str = docker_datasource.get_logs(container_id, since=since_ts, until=until_ts)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Не удалось получить логи: {e}")

    return {"logs": logs_str}


@router.post("/containers/{container_id}/exec")
def exec_command(
    container_id: str,
    command: str = Query(...),
    current_user: models.User = Depends(auth_service.get_current_active_user),
) -> dict:
    try:
        output = docker_datasource.exec_command(container_id, command)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Не удалось выполнить команду: {e}")
    return {"output": output}
