from pydantic import UUID4, BaseModel
from datetime import datetime


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenPayload(BaseModel):
    id: UUID4
    roles: list[str] | None = None
    username: str


class TokenPairCreate(BaseModel):
    user_id: UUID4
    access_token: str
    refresh_token: str
    expires_at: datetime


class TokenPairUpdate(TokenPairCreate):
    pass


class LogoutRequest(BaseModel):
    access_token: str
