from datetime import datetime, timedelta
from typing import Any, Union
import src.config as settings
from jose import jwt
from passlib.context import CryptContext
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.ALGORITHM


def create_jwt_token(subject: Union[str, Any], expires_delta: timedelta) -> str:
    expire = datetime.now() + expires_delta
    if isinstance(subject, dict):
        to_encode = {"exp": expire, **subject}
    else:
        to_encode = {"exp": expire, "sub": subject}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_access_token(subject: Union[str, Any]) -> tuple[str, Any]:
    expires_timedelta = timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    token = create_jwt_token(subject, expires_delta=expires_timedelta)

    return token, jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])["exp"]


def create_refresh_token(subject: Union[str, Any]) -> tuple[str, Any]:
    expires_timedelta = timedelta(minutes=int(settings.REFRESH_TOKEN_EXPIRE_MINUTES))
    token = create_jwt_token(subject, expires_delta=expires_timedelta)

    return token, jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])["exp"]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
