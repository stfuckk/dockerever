from src.errors.exceptions import CoreException
from src.datasources.role import role_datasource
from src.db.database import get_db
from src import schemas, models
import src.config as settings
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import UUID4
from typing import List


class RoleService:
    @staticmethod
    async def get_all_roles(skip: int = 0, limit: int = 100) -> List[schemas.Role]:
        async with get_db() as db:
            roles = await role_datasource.get_multi(db, skip=skip, limit=limit)
            if roles is None:
                return []
            return roles


role_service = RoleService()
