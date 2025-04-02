from typing import List
from src import datasources, models, schemas
from src.services.auth import auth_service
from src.services.user_roles import user_role_service
from src.constants.roles import Role
from fastapi import APIRouter, HTTPException, Security
from pydantic.types import UUID4

router = APIRouter(prefix="/user-roles", tags=["user-roles"])


@router.post("", response_model=schemas.UserRole)
async def assign_user_role(
    *,
    user_role_in: schemas.UserRoleCreate,
    current_user: models.User = Security(
        auth_service.get_current_active_user,
        scopes=[
            Role.SUPER_ADMIN["name"],
        ],
    ),
) -> schemas.UserRole:
    return await user_role_service.assign_role(user_role_in=user_role_in, current_user=current_user)


@router.get("/{user_id}", response_model=List[schemas.UserRole])
async def get_user_roles(
    *,
    user_id: UUID4,
    current_user: models.User = Security(
        auth_service.get_current_active_user,
        scopes=[Role.ADMIN["name"], Role.SUPER_ADMIN["name"]],
    ),
) -> List[schemas.UserRole]:
    return await user_role_service.get_user_roles(user_id)


@router.delete("/{user_id}", response_model=schemas.UserRole)
async def delete_user_role(
    *,
    user_id: UUID4,
    user_role_in: schemas.UserRoleUpdate,
    current_user: models.User = Security(
        auth_service.get_current_active_user,
        scopes=[
            Role.SUPER_ADMIN["name"],
        ],
    ),
) -> schemas.UserRole:
    return await user_role_service.delete_user_role(user_id, user_role_in, current_user)
