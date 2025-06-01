from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from src.services.auth import auth_service
from src.services.dashboard_block import dashboard_block_service
from src import models
from src.schemas.dashboard import DashboardBlock, DashboardBlockCreate, DashboardBlockUpdate

router = APIRouter(prefix="/dashboard-blocks", tags=["dashboard-blocks"])


@router.post("/{dashboard_id}", response_model=DashboardBlock)
async def create_block(
    dashboard_id: UUID4,
    block: DashboardBlockCreate,
    current_user: models.User = Depends(auth_service.get_current_active_user),
) -> DashboardBlock:
    """
    Создаёт новый блок внутри Dashboard с указанным dashboard_id.
    """
    try:
        new_block = await dashboard_block_service.create_block(dashboard_id, block)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Не удалось создать блок: {e}")
    return new_block


@router.patch("/{block_id}", response_model=DashboardBlock)
async def update_block(
    block_id: UUID4,
    data: DashboardBlockUpdate,
    current_user: models.User = Depends(auth_service.get_current_active_user),
) -> DashboardBlock:
    """
    Обновляет существующий блок по его block_id.
    """
    try:
        updated = await dashboard_block_service.update_block(block_id, data)
        if not updated:
            # Вдруг DAO вернул None
            raise HTTPException(status_code=404, detail="Блок не найден")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Не удалось обновить блок: {e}")
    return updated


@router.delete("/{block_id}")
async def delete_block(
    block_id: UUID4,
    current_user: models.User = Depends(auth_service.get_current_active_user),
) -> dict:
    """
    Удаляет блок по block_id.
    """
    try:
        await dashboard_block_service.delete_block(block_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Не удалось удалить блок: {e}")
    return {"status": "deleted"}
