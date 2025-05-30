from fastapi import APIRouter, Query, Depends
from src.datasources.docker import docker_datasource
from src.services.auth import auth_service
from src import models

router = APIRouter(prefix="/docker", tags=["docker"])


@router.get("/containers")
def list_containers(
    search: str = "", current_user: models.User = Depends(auth_service.get_current_active_user)
) -> dict:
    result = {"containers": docker_datasource.list_containers(search)}
    return result


@router.delete("/containers/{container_id}")
def remove_container(
    container_id: str, current_user: models.User = Depends(auth_service.get_current_active_user)
) -> dict:
    docker_datasource.remove_container(container_id)
    return {"status": "removed"}


@router.get("/containers/{container_id}/logs")
def get_logs(container_id: str, current_user: models.User = Depends(auth_service.get_current_active_user)) -> dict:
    return {"logs": docker_datasource.get_logs(container_id)}


@router.post("/containers/{container_id}/exec")
def exec_command(
    container_id: str,
    command: str = Query(...),
    current_user: models.User = Depends(auth_service.get_current_active_user),
) -> dict:
    return {"output": docker_datasource.exec_command(container_id, command)}
