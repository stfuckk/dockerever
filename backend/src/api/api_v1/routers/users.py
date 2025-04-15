from typing import Any, List, Optional
from src.services.auth import auth_service
from src.services.user import user_service
from src import models, schemas
from src.constants.roles import Role
from fastapi import APIRouter, Depends, Security
from pydantic.types import UUID4


router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=schemas.UserListResponse)
async def read_users(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: models.User = Security(
        auth_service.get_current_active_user,
        scopes=[Role.ADMIN["name"], Role.SUPER_ADMIN["name"]],
    ),
) -> schemas.UserListResponse:
    users, total = await user_service.get_users(skip, limit, search=search)
    return {"users": users, "total": total}


@router.post("", response_model=schemas.User)
async def create_user(
    *,
    user_in: schemas.UserCreateSchema,
    current_user: models.User = Security(
        auth_service.get_current_active_user,
        scopes=[Role.ADMIN["name"], Role.SUPER_ADMIN["name"]],
    ),
) -> schemas.User:
    return await user_service.create_user(user_in)


@router.put("/me", response_model=schemas.User)
async def update_user_me(
    *,
    user_in: schemas.UserUpdateSchema,
    current_user: models.User = Depends(auth_service.get_current_active_user_for_update),
) -> schemas.User:
    return await user_service.update_user(current_user.id, user_in, current_user)


@router.get("/me", response_model=schemas.User)
async def read_user_me(
    current_user: models.User = Depends(auth_service.get_current_active_user),
) -> schemas.User:
    return await user_service.get_user(current_user)


@router.get("/{user_id}", response_model=schemas.User)
async def read_user_by_id(
    user_id: UUID4,
    current_user: models.User = Security(
        auth_service.get_current_active_user,
        scopes=[Role.ADMIN["name"], Role.SUPER_ADMIN["name"]],
    ),
) -> schemas.User:
    return await user_service.get_specific_user(user_id)


@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    *,
    user_id: UUID4,
    user_in: schemas.UserUpdateSchema,
    current_user: models.User = Depends(auth_service.get_current_active_user),
) -> schemas.User:
    return await user_service.update_user(user_id, user_in, current_user)


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: UUID4,
    current_user: models.User = Depends(auth_service.get_current_active_user),
) -> None:
    await user_service.delete_user(user_id, current_user)
