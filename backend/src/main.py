from fastapi import FastAPI
from src.auth.router import router as auth_router


app = FastAPI()


@app.get("/")
async def index() -> dict:
    return {"status": "It's working! You can check /docs or /redoc"}


app.include_router(auth_router)
