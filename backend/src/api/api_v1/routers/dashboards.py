from fastapi import APIRouter, Depends
from src.services.dashboard import dashboard_service
from src.schemas.dashboard import Dashboard, DashboardCreate, DashboardUpdate
from typing import List
from src.services.auth import auth_service
from src import models


router = APIRouter(prefix="/dashboards", tags=["dashboards"])


@router.get("", response_model=List[Dashboard])
async def get_dashboards(current_user: models.User = Depends(auth_service.get_current_active_user)) -> List[Dashboard]:
    return await dashboard_service.get_user_dashboards(current_user)


@router.post("", response_model=Dashboard)
async def create_dashboard(
    dashboard_in: DashboardCreate,
    current_user: models.User = Depends(auth_service.get_current_active_user),
) -> Dashboard:
    return await dashboard_service.create_dashboard(dashboard_in, user_id=current_user.id)


@router.patch("/{dashboard_id}", response_model=Dashboard)
async def update_dashboard(
    dashboard_id: int,
    data: DashboardUpdate,
    current_user: models.User = Depends(auth_service.get_current_active_user),
) -> Dashboard:
    return await dashboard_service.update_dashboard(dashboard_id, data)


@router.delete("/{dashboard_id}")
async def delete_dashboard(
    dashboard_id: int,
    current_user: models.User = Depends(auth_service.get_current_active_user),
) -> dict:
    await dashboard_service.delete_dashboard(dashboard_id)
    return {"status": "deleted"}
