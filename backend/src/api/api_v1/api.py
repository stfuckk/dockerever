from src.api.api_v1.routers import auth, users, roles, user_roles
from fastapi import APIRouter
from src.schemas.core_message import CoreMessage

api_router = APIRouter()
responses = {422: {"model": CoreMessage}}

api_router.include_router(auth.router, responses=responses)
api_router.include_router(users.router, responses=responses)
api_router.include_router(roles.router, responses=responses)
api_router.include_router(user_roles.router, responses=responses)
