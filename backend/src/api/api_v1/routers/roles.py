from typing import Any, List
from src import datasources, schemas, models
from src.services.roles import role_service
from src.services.auth import auth_service
from fastapi import APIRouter, Security
from src.constants.roles import Role

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=List[schemas.Role])
async def get_roles(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Security(
        auth_service.get_current_active_user,
        scopes=[
            Role.ADMIN["name"],
            Role.SUPER_ADMIN["name"],
        ],
    ),
) -> Any:
    """
    Retrieve all available user roles.
    """
    return await role_service.get_all_roles(skip=skip, limit=limit)
