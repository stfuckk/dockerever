from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import requests
from datetime import datetime, timedelta, timezone
from src.auth.services.auth_service import decode_token

router = APIRouter(prefix="/metrics", tags=["Metrics"])

PROMETHEUS_URL = "http://prometheus:9090/api/v1/query"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def validate_token(token: str = Depends(oauth2_scheme)) -> dict:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    return payload

def query_prometheus(query: str) -> dict:
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=1)
    response = requests.get(PROMETHEUS_URL, params={
        "query": query,
    })
    response.raise_for_status()
    return response.json()

@router.get("/cpu_usage")
async def get_cpu_usage(token: str = Depends(validate_token)):
    query = '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
    result = query_prometheus(query)
    return result

@router.get("/disk_space")
async def get_disk_space(token: str = Depends(validate_token)):
    free_query = 'node_filesystem_free_bytes'
    used_query = 'node_filesystem_size_bytes - node_filesystem_free_bytes'
    free_result = query_prometheus(free_query)
    used_result = query_prometheus(used_query)
    return {"free": free_result, "used": used_result}

@router.get("/network_load")
async def get_network_load(token: str = Depends(validate_token)):
    query = 'rate(node_network_receive_bytes_total[5s]) + rate(node_network_transmit_bytes_total[5s])'
    result = query_prometheus(query)
    return result

@router.get("/memory_usage")
async def get_memory_usage(token: str = Depends(validate_token)):
    query = 'node_memory_MemAvailable_bytes'
    result = query_prometheus(query)
    return result
