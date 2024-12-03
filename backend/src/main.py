from fastapi import FastAPI
from src.auth.router import router as auth_router
from typing import AsyncGenerator
from src.auth.models import User
from src.database import get_db
from src.auth.utils import get_password_hash
from sqlalchemy.future import select
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import os

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with get_db() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()

        if not users:
            username = os.getenv("DEFAULT_USER_USERNAME", "admin")
            password = os.getenv("DEFAULT_USER_PASSWORD", "admin")
            first_name = 'noname'
            last_name = 'nolastname'
            is_admin = True

            hashed_password = get_password_hash(password)

            default_user = User(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=hashed_password,
                is_admin=is_admin
            )

            db.add(default_user)
            await db.commit()
    yield


app = FastAPI(lifespan=lifespan, root_path='/api/')


@app.get("/")
async def index() -> dict:
    return {"status": "It's working!"}


app.include_router(auth_router)
