from fastapi import APIRouter, Depends, HTTPException
from src.datasources.docker import docker_datasource
from src.services.auth import auth_service
from src import models
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/docker_ext", tags=["docker_ext"])


class ImageInfo(BaseModel):
    id: str
    repo_tag: str
    created: str


class NetworkInfo(BaseModel):
    id: str
    name: str
    driver: str
    # containers: dict  # необязательно отдавать все детали


class VolumeInfo(BaseModel):
    name: str
    created_at: str
    mountpoint: str
    scope: str


# ===== Images =====
@router.get("/images", response_model=List[ImageInfo])
async def list_images(current_user: models.User = Depends(auth_service.get_current_active_user)):
    return docker_datasource.list_images()


@router.delete("/images/{image_id}")
async def delete_image(image_id: str, current_user: models.User = Depends(auth_service.get_current_active_user)):
    try:
        docker_datasource.remove_image(image_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Не удалось удалить образ: {e}")
    return {"status": "deleted"}


# ===== Networks =====
@router.get("/networks", response_model=List[NetworkInfo])
async def list_networks(current_user: models.User = Depends(auth_service.get_current_active_user)):
    return docker_datasource.list_networks()


@router.delete("/networks/{network_id}")
async def delete_network(network_id: str, current_user: models.User = Depends(auth_service.get_current_active_user)):
    try:
        docker_datasource.remove_network(network_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Не удалось удалить сеть: {e}")
    return {"status": "deleted"}


@router.get("/networks/{network_id}/containers")
async def get_network_containers(
    network_id: str, current_user: models.User = Depends(auth_service.get_current_active_user)
):
    """
    Возвращает список контейнеров, подключённых к сети network_id.
    """
    try:
        lst = docker_datasource.get_containers_by_network(network_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при получении контейнеров сети: {e}")
    return {"containers": lst}


# ===== Volumes =====
@router.get("/volumes", response_model=List[VolumeInfo])
async def list_volumes(current_user: models.User = Depends(auth_service.get_current_active_user)):
    return docker_datasource.list_volumes()


@router.delete("/volumes/{volume_name}")
async def delete_volume(volume_name: str, current_user: models.User = Depends(auth_service.get_current_active_user)):
    try:
        docker_datasource.remove_volume(volume_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Не удалось удалить том: {e}")
    return {"status": "deleted"}
