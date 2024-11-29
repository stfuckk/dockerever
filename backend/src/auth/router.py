from fastapi import APIRouter, Depends, HTTPException, status, Request
from src.auth.services.auth_service import (
    create_access_token,
    authenticate_user,
    get_user_by_id,
    create_user,
    decode_token,
)
from src.auth import schemas
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/api/auth", tags=["Auth"])


# достать токен из куки
async def get_token(request: Request) -> str:
    token = request.cookies.get("users_access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен не найден"
        )
    return token


@router.post("/register/")
async def register_user(
    user: schemas.UserRegister,
    token: str = Depends(oauth2_scheme)
) -> schemas.UserRegisterResponse | None:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User ID not found"
        )
    current_user = await get_user_by_id(int(user_id))
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to register users"
        )

    db_user = await authenticate_user(user.username, user.password)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )
    return await create_user(user)


@router.post("/login", response_model=schemas.TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    db_user = await authenticate_user(form_data.username, form_data.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль"
        )
    access_token = create_access_token({"sub": str(db_user.id)})

    return {"access_token": access_token, "token_type": "bearer", "refresh_token": None}


@router.get("/me/", response_model=schemas.UserBase)
async def get_me(
    token: str = Depends(oauth2_scheme)
) -> schemas.BaseModel:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен не найден"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Не найден ID пользователя"
        )

    user = await get_user_by_id(int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден"
        )

    return user


@router.get("/token_validate", response_model=dict)
async def validate_token(token: str = Depends(oauth2_scheme)) -> dict:
    payload = decode_token(token)
    if not payload:
        return {"status": False}
    return {"status": True}
