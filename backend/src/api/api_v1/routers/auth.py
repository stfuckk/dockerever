from fastapi import APIRouter, Depends
from src import models, schemas
from src.services.auth import auth_service
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/refresh-token", response_model=schemas.Token)
async def do_refresh_token(request: schemas.TokenRefreshRequest) -> schemas.Token:
    return await auth_service.refresh_token(request)


@router.post("/access-token", response_model=schemas.Token)
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    return await auth_service.get_access_token(form_data.username, form_data.password)


@router.post("/test-token", response_model=schemas.User)
async def test_token(
    current_user: models.User = Depends(auth_service.get_current_user),
) -> Any:
    return current_user


@router.post("/logout")
async def logout_user(access_token: str = schemas.LogoutRequest) -> dict:
    return await auth_service.remove_user_token(access_token=access_token)


@router.post("/logout-all")
async def logout_all(
    current_user: models.User = Depends(auth_service.get_current_user),
) -> dict:
    return await auth_service.remove_all_user_tokens(current_user)
