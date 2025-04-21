from fastapi import APIRouter, Depends
from src.services.dashboard import dashboard_service
from src.schemas.dashboard import Dashboard
from typing import List
from src.services.auth import auth_service
from src import models

router = APIRouter(prefix="/dashboards", tags=["dashboards"])


@router.get("", response_model=List[Dashboard])
async def get_dashboards(
    current_user: models.User = Depends(auth_service.get_current_active_user),
) -> List[Dashboard]:
    return await dashboard_service.get_all_dashboards()
