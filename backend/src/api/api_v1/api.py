from src.api.api_v1.routers import (
    auth,
    users,
    roles,
    user_roles,
    nodes,
    dashboards,
    prometheus,
    docker,
    dashboard_blocks,
    docker_ext,
)
from fastapi import APIRouter
from src.schemas.core_message import CoreMessage

api_router = APIRouter()
responses = {422: {"model": CoreMessage}}

api_router.include_router(auth.router, responses=responses)
api_router.include_router(users.router, responses=responses)
api_router.include_router(roles.router, responses=responses)
api_router.include_router(user_roles.router, responses=responses)
api_router.include_router(nodes.router, responses=responses)
api_router.include_router(dashboards.router, responses=responses)
api_router.include_router(dashboard_blocks.router, responses=responses)
api_router.include_router(prometheus.router, responses=responses)
api_router.include_router(docker.router, responses=responses)
api_router.include_router(docker_ext.router, responses=responses)
