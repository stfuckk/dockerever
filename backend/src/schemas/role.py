from typing import Optional
from pydantic import UUID4, BaseModel, Field


class RoleBase(BaseModel):
    name: Optional[str] = Field(None, description="The name of the role")
    description_ru: Optional[str] = Field(None, description="The RU description of the role")
    description_en: Optional[str] = Field(None, description="The EN description of the role")

    class Config:
        from_attributes = True


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass


class RoleInDBBase(RoleBase):
    id: UUID4

    class Config:
        from_attributes = True


class Role(RoleInDBBase):
    pass
