from typing import List

from src.schemas.role import Role
from pydantic import UUID4, BaseModel


# Shared properties
class UserRoleBase(BaseModel):
    user_id: UUID4
    role_id: UUID4


class UserRoleCreate(UserRoleBase):
    pass


class UserRoleUpdate(BaseModel):
    role_id: UUID4


class UserRoleInDBBase(UserRoleBase):
    role: Role

    class Config:
        from_attributes = True


class UserRole(UserRoleInDBBase):
    pass


class UserRoles(BaseModel):
    roles: List[UserRole]

    class Config:
        from_attributes = True
