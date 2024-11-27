from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from src.auth.services.auth_service import (
    create_access_token,
    authenticate_user,
    get_user_by_id,
    create_user,
    decode_token,
)
from src.auth import schemas
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/auth", tags=["Auth"])


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
) -> schemas.UserRegisterResponse | None:

    db_user = await authenticate_user(user.username, user.password)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Пользователь уже существует"
        )
    return await create_user(user)


@router.post("/login")
async def login(response: Response, user: schemas.UserAuth) -> dict:
    db_user = await authenticate_user(user.username, user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль"
        )
    access_token = create_access_token({"sub": str(db_user.id)})

    # кладем токен в куки
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {"access_token": access_token, "refresh_token": None}


@router.get("/me/", response_model=schemas.UserBase)
async def get_me(token: str = Depends(get_token)) -> schemas.BaseModel:
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
