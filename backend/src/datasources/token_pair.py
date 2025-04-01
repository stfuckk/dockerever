from src.datasources.base import DataSourceBase
from src.models.token_pair import TokenPair
from src.schemas.token import TokenPairCreate, TokenPairUpdate
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import delete
from pydantic import UUID4
from src.utils import security
from src.config import logger


class DataSourceTokenPair(DataSourceBase[TokenPair, TokenPairCreate, TokenPairUpdate]):

    async def create(self, db: AsyncSession, *, obj_in: TokenPairCreate) -> Optional[TokenPair]:
        try:
            db_obj = TokenPair(
                user_id=obj_in.user_id,
                hashed_access_token=security.hash_token(obj_in.access_token),
                hashed_refresh_token=security.hash_token(obj_in.refresh_token),
                expires_at=obj_in.expires_at,
            )

            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"DB ERROR - Cannot create token pair: {e}")
            return None

    async def _delete_pair(self, pair: TokenPair, session: AsyncSession) -> Optional[bool]:
        try:
            await super().remove(session, id=pair.id)
            return True
        except SQLAlchemyError as e:
            logger.error(f"DB ERROR - Cannot delete token pair: {e}")
            return None

    async def delete_all_pairs_by_user_id(self, db: AsyncSession, *, user_id: UUID4) -> Optional[bool]:
        try:
            await db.execute(delete(TokenPair).filter(TokenPair.user_id == user_id))
            await db.commit()
            return True
        except SQLAlchemyError as e:
            logger.error(f"DB ERROR - Cannot delete all token pairs by user_id: {e}")
            return None

    async def get_by_refresh_token(self, db: AsyncSession, *, refresh_token: str) -> Optional[TokenPair]:
        try:
            hashed_refresh_token = security.hash_token(refresh_token)
            result = await db.execute(
                select(TokenPair).filter(
                    TokenPair.hashed_refresh_token == hashed_refresh_token,
                    TokenPair.expires_at > datetime.utcnow(),
                )
            )
            token_pair_in_db = result.scalar_one_or_none()

            if token_pair_in_db is None:
                return None

            return token_pair_in_db
        except SQLAlchemyError as e:
            logger.error(f"DB ERROR - Cannot get token pair by refresh token: {e}")
            return None

    async def get_by_access_token(self, db: AsyncSession, *, access_token: str) -> Optional[TokenPair]:
        try:
            hashed_access_token = security.hash_token(access_token)

            result = await db.execute(
                select(TokenPair).filter(
                    TokenPair.hashed_access_token == hashed_access_token,
                    TokenPair.expires_at > datetime.utcnow(),
                )
            )

            token_pair_in_db = result.scalar_one_or_none()

            if not token_pair_in_db:
                return None

            return token_pair_in_db
        except SQLAlchemyError as e:
            logger.error(f"DB ERROR - Cannot get token pair by access token: {e}")
            return None

    async def delete_expired_tokens(self, db: AsyncSession) -> Optional[bool]:
        """
        Удаляет токены с истёкшим сроком действия.
        """
        try:
            await db.execute(delete(TokenPair).filter(TokenPair.expires_at < datetime.utcnow()))
            await db.commit()
            return True
        except SQLAlchemyError as e:
            logger.error(f"DB ERROR - Cannot delete expired token pair: {e}")
            return None


token_pair_datasource = DataSourceTokenPair(TokenPair)
