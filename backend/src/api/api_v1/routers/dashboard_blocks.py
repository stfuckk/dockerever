from fastapi import APIRouter, Depends
from src.services.auth import auth_service
from src.services.dashboard_block import dashboard_block_service
from src.schemas.dashboard import DashboardBlock, DashboardBlockCreate, DashboardBlockUpdate
from src import models


router = APIRouter(prefix="/dashboard-blocks", tags=["dashboard-blocks"])


@router.post("/{dashboard_id}", response_model=DashboardBlock)
async def create_block(
    dashboard_id: int,
    block: DashboardBlockCreate,
    current_user: models.User = Depends(auth_service.get_current_active_user),
) -> DashboardBlock:
    return await dashboard_block_service.create_block(dashboard_id, block)


@router.patch("/{block_id}", response_model=DashboardBlock)
async def update_block(
    block_id: int,
    data: DashboardBlockUpdate,
    current_user: models.User = Depends(auth_service.get_current_active_user),
) -> DashboardBlock:
    return await dashboard_block_service.update_block(block_id, data)


@router.delete("/{block_id}")
async def delete_block(
    block_id: int,
    current_user: models.User = Depends(auth_service.get_current_active_user),
) -> dict:
    await dashboard_block_service.delete_block(block_id)
    return {"status": "deleted"}
