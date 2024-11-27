from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from src.config import get_auth_data
from sqlalchemy.future import select
from src.auth.models import User
from src.database import get_db
from src.auth.utils import verify_password
from src.auth.utils import get_password_hash
from src.auth import schemas


# Генерация JWT токена
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"exp": expire})
    auth_data = get_auth_data()
    encode_jwt = jwt.encode(
        to_encode, auth_data["secret_key"], algorithm=auth_data["algorithm"]
    )
    return encode_jwt


# TODO: - вместо возврата None лучше сделать нормальный ответ
#       - условия if user с возвратом None и подобные правильнее заменить на try/except
def decode_token(token: str) -> dict | None:
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(
            token, auth_data["secret_key"], algorithms=[auth_data["algorithm"]]
        )
        return payload
    except JWTError:
        return None


async def authenticate_user(username: str, password: str) -> schemas.UserBase | None:
    async with get_db():
        user = await get_user_by_username(username)
        if user and verify_password(password, user.password):
            return user
        else:
            return None


async def get_user_by_username(username: str) -> schemas.UserBase | None:
    async with get_db() as db:
        user = await db.execute(select(User).filter(User.username == username))
        if user:
            return user.scalars().first()
        else:
            return None


async def get_user_by_id(id: int) -> schemas.UserBase | None:
    async with get_db() as db:
        result = await db.execute(select(User).filter(User.id == id))
        if result:
            return result.scalars().first()
        else:
            return None


async def create_user(user: schemas.UserRegister) -> schemas.UserRegisterResponse | None:
    async with get_db() as db:
        hashed = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            password=hashed,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        response = schemas.UserRegisterResponse(
            id=db_user.id,
            username=db_user.username,
            created_at=db_user.created_at
        )
        return response
