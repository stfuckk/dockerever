from datetime import datetime
from src import datasources, models, schemas
from src.constants.roles import Role
from src.utils import security
import src.config as settings
from src.db.database import get_db
from fastapi import Depends, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError
from src.errors.exceptions import CoreException


scopes = {}

for role_key in Role.roles.keys():
    scopes[Role.roles[role_key]["name"]] = Role.roles[role_key]["description_ru"]

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/access-token",
    scopes=scopes,
)


class AuthService:
    @staticmethod
    async def get_access_token(username: str, password: str) -> schemas.Token:
        async with get_db() as db:
            user = await datasources.user_datasource.authenticate(db, username=username, password=password)
            if not user:
                raise CoreException("errors.auth.incorrect_credentials")
            elif not await datasources.user_datasource.is_active(user):
                raise CoreException("errors.auth.inactive_user")

            return await AuthService.generate_tokens(user, db)

    @staticmethod
    async def generate_tokens(user: models.User, db: AsyncSession) -> schemas.Token:
        if not user.roles:
            roles = ["USER"]
        else:
            roles = [role.name for role in user.roles]

        # Generate new tokens
        access_token_payload = {
            "id": str(user.id),
            "roles": roles,
            "username": user.username,
        }

        refresh_token_payload = {"id": str(user.id)}

        access_token, access_token_exp = security.create_access_token(access_token_payload)
        refresh_token, refresh_token_exp = security.create_refresh_token(refresh_token_payload)

        # Adding tokens to the database
        try:
            token_pair = schemas.TokenPairCreate(
                **{
                    "user_id": str(user.id),
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_at": datetime.fromtimestamp(refresh_token_exp),
                }
            )
            await datasources.token_pair_datasource.create(db, obj_in=token_pair)
        except Exception:
            raise CoreException("errors.auth.token_create_error")

        content = schemas.Token(
            **{
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }
        )

        return content

    @staticmethod
    async def refresh_token(refresh_req: schemas.TokenRefreshRequest) -> schemas.Token:
        async with get_db() as db:
            try:
                token_pair = await datasources.token_pair_datasource.get_by_refresh_token(
                    db, refresh_token=refresh_req.refresh_token
                )

                if not token_pair:
                    raise CoreException("errors.auth.invalid_refresh_token")

                # Delete old tokens before creating new ones
                await datasources.token_pair_datasource.remove(db, id=token_pair.id)

                payload = jwt.decode(
                    refresh_req.refresh_token,
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM],
                )

                user_id = payload.get("id")
                if not user_id:
                    raise CoreException("errors.auth.invalid_refresh_token")

                user = await datasources.user_datasource.get(db, id=user_id)

                if not user or not await datasources.user_datasource.is_active(user):
                    raise CoreException("errors.auth.inactive_user")

                return await AuthService.generate_tokens(user, db)

            except (JWTError, ValidationError):
                raise CoreException("errors.auth.invalid_refresh_token")

    @staticmethod
    async def remove_user_token(access_token: schemas.Token) -> dict[str, str]:
        async with get_db() as db:
            token_pair = await datasources.token_pair_datasource.get_by_access_token(db, access_token=access_token)
            if not token_pair:
                raise CoreException("errors.auth.invalid_access_token")

            token_pair = await datasources.token_pair_datasource.remove(db, id=token_pair.id)
            if not token_pair:
                raise CoreException("errors.auth.logout_error")
            return {"message": "ok!"}

    @staticmethod
    async def remove_all_user_tokens(user: models.User) -> dict[str, str]:
        async with get_db() as db:
            deleted = await datasources.token_pair_datasource.delete_all_pairs_by_user_id(db, user_id=user.id)
            if not deleted:
                raise CoreException("errors.auth.logout_error")
            return {"message": "ok!"}

    @staticmethod
    async def get_current_user(
        security_scopes: SecurityScopes,
        token: str = Depends(reusable_oauth2),
    ) -> models.User:
        async with get_db() as db:
            token_pair = await datasources.token_pair_datasource.get_by_access_token(db, access_token=token)

            if not token_pair:
                raise CoreException("errors.auth.invalid_access_token")

            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
                if payload.get("id") is None:
                    raise CoreException("errors.auth.invalid_access_token")
                token_data = schemas.TokenPayload(**payload)
            except (jwt.JWTError, ValidationError):
                raise CoreException("errors.auth.invalid_access_token")

            user = await datasources.user_datasource.get(db, id=token_data.id)

            if not user:
                raise CoreException("errors.auth.invalid_access_token")

            if security_scopes.scopes and not token_data.roles:
                raise CoreException("errors.auth.not_enough_permissions")

            if security_scopes.scopes and not set(token_data.roles or []).intersection(security_scopes.scopes):
                raise CoreException("errors.auth.not_enough_permissions")
            return user

    @staticmethod
    async def get_current_active_user(
        current_user: models.User = Security(
            get_current_user,
            scopes=[],
        ),
    ) -> models.User:
        current_user = await current_user
        if not current_user.is_active:
            raise CoreException("errors.auth.inactive_user")
        return current_user


auth_service = AuthService()
