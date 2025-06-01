from fastapi import APIRouter, Depends
from src.services.dashboard import dashboard_service
from src.schemas.dashboard import Dashboard, DashboardCreate, DashboardUpdate
from typing import List
from src.services.auth import auth_service
from src import models
from pydantic import UUID4


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
    dashboard_id: UUID4,
    data: DashboardUpdate,
    current_user: models.User = Depends(auth_service.get_current_active_user),
) -> Dashboard:
    # здесь можно добавить проверку, что пользователь владеет этим дашбордом,
    # либо роль админ.
    return await dashboard_service.update_dashboard(dashboard_id, data)


@router.delete("/{dashboard_id}")
async def delete_dashboard(
    dashboard_id: UUID4,
    current_user: models.User = Depends(auth_service.get_current_active_user),
) -> dict:
    await dashboard_service.delete_dashboard(dashboard_id)
    return {"status": "deleted"}


from fastapi import HTTPException


@router.get("/title/{title}", response_model=Dashboard)
async def get_dashboard_by_title(
    title: str,
    current_user: models.User = Depends(auth_service.get_current_active_user),
) -> Dashboard:
    dashboard = await dashboard_service.get_dashboard_by_title(title)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboard
