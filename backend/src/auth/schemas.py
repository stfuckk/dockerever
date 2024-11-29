from pydantic import BaseModel, Field
from datetime import datetime


class UserBase(BaseModel):
    id: int
    username: str = Field()
    first_name: str = Field()
    last_name: str = Field()
    password: str = Field()

    is_admin: bool = Field()

    class Config:
        orm_mode = True
        model_config = {"from_attributes": True}


# Описание тела запроса на регистрацию
class UserRegister(BaseModel):
    username: str = Field(..., min_length=5, max_length=30, description="Логин")
    password: str = Field(
        ..., min_length=5, max_length=30, description="Пароль от 5 до 30 знаков"
    )
    first_name: str = Field(
        ..., min_length=3, max_length=50, description="Имя от 3 до 50 знаков"
    )
    last_name: str = Field(
        ..., min_length=3, max_length=50, description="Фамилия от 3 до 50 знаков"
    )


class UserRegisterResponse(BaseModel):
    id: int
    username: str
    created_at: datetime


class UserAuth(BaseModel):
    username: str = Field(..., min_length=5, max_length=30, description="Логин")
    password: str = Field(
        ..., min_length=5, max_length=30, description="Пароль от 5 до 30 знаков"
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str | None = None
