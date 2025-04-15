from pydantic import BaseModel, Field, UUID4, SecretStr, field_validator
from typing import Optional, List
from src.errors.exceptions import CoreException
from datetime import datetime
from src.schemas.role import Role


class UserSchema(BaseModel):
    username: str = Field(
        ...,
        min_length=5,
        max_length=50,
        description="Имя пользователя, минимальная длина 5" "символа, максимальная 50",
    )


class UserCreateSchema(UserSchema):
    password: SecretStr = Field(..., min_length=5, max_length=25, description="Пароль от 5 до 25 символов")
    must_change_password: Optional[bool] = False

    @field_validator("password")
    def validate_password(cls, v: SecretStr) -> SecretStr:
        min_length = 5
        max_length = 30
        includes_numbers = True

        if not isinstance(v.get_secret_value(), str):
            raise CoreException("errors.validators.no_password")
        if len(v.get_secret_value()) < min_length or len(v.get_secret_value()) > max_length:
            raise CoreException("errors.validators.wrong_password_length")
        if includes_numbers and not any(char.isdigit() for char in v.get_secret_value()):
            raise CoreException("errors.validators.not_numeral_password")

        return v


class UserUpdateSchema(BaseModel):
    username: Optional[str] = Field(
        ...,
        min_length=5,
        max_length=50,
        description="Имя пользователя, минимальная длина 5" "символа, максимальная 50",
    )
    password: Optional[SecretStr] = Field(None, min_length=5, max_length=25, description="Пароль от 5 до 25 символов")
    prev_password: SecretStr = Field(..., min_length=5, max_length=25, description="Пароль от 5 до 25 символов")


class UserLoginSchema(BaseModel):
    username: str = Field(
        ...,
        min_length=5,
        max_length=50,
        description="Имя пользователя, минимальная длина 5" "символа, максимальная 50",
    )
    password: SecretStr = Field(..., min_length=5, max_length=25, description="Пароль от 5 до 25 символов")


class UserInDBBase(UserSchema):
    is_active: Optional[bool] = Field(True, description="Пользователь активен")
    id: UUID4 = Field(..., description="ID пользователя")
    roles: List[Role]
    created_at: datetime
    updated_at: datetime
    must_change_password: bool

    class Config:
        from_attributes = True


class User(UserInDBBase):
    pass


class UserListResponse(BaseModel):
    users: List[User]
    total: int
