from typing import Any, List
from src.services.auth import auth_service
from src.services.user import user_service
from src import models, schemas
from src.constants.roles import Role
from fastapi import APIRouter, Depends, Security
from pydantic.types import UUID4


router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[schemas.User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Security(
        auth_service.get_current_active_user,
        scopes=[Role.ADMIN["name"], Role.SUPER_ADMIN["name"]],
    ),
) -> List[schemas.User]:
    users = await user_service.get_users(skip, limit)
    if not users:
        return []
    else:
        return users


@router.post("", response_model=schemas.User)
async def create_user(
    *,
    user_in: schemas.UserCreateSchema,
    current_user: models.User = Security(
        auth_service.get_current_active_user,
        scopes=[Role.ADMIN["name"], Role.SUPER_ADMIN["name"]],
    ),
) -> schemas.User:
    return await user_service.create_user(user_in, current_user)


@router.put("/me", response_model=schemas.User)
async def update_user_me(
    *,
    user_in: schemas.UserUpdateSchema,
    current_user: models.User = Depends(auth_service.get_current_active_user),
) -> schemas.User:
    current_user = await current_user
    return await user_service.update_user(current_user.id, user_in)


@router.get("/me", response_model=schemas.User)
async def read_user_me(current_user: models.User = Depends(auth_service.get_current_active_user)) -> schemas.User:
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
) -> Any:
    return await user_service.update_user(user_id, user_in)
