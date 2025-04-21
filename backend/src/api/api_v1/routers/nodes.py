from fastapi import APIRouter, Depends
from src.services.nodes import node_service
from src.services.auth import auth_service
from typing import List
from src import schemas, models


router = APIRouter(prefix="/nodes", tags=["nodes"])


@router.get("", response_model=List[schemas.NodeInfo])
async def get_nodes(
    current_user: models.User = Depends(auth_service.get_current_active_user),
) -> List[schemas.NodeInfo]:
    """
    Get all nodes.
    """
    return await node_service.get_available_nodes()
