import os
import logging
from pydantic import SecretStr
from dotenv import load_dotenv

load_dotenv(dotenv_path="")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_NAME: str = os.getenv("PROJECT_NAME", "FastAPI Auth Service")


DB_USER: str = os.getenv("POSTGRES_USER", "dockerever")
DB_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST: str = os.getenv("DB_HOST", "host")
DB_PORT: str = os.getenv("DB_PORT", "5432")
DB_NAME: str = os.getenv("POSTGRES_DB", "dockereverdb")

SECRET_KEY: str = os.getenv("SECRET_KEY", "secret_key")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 30))

SUPER_ADMIN_USERNAME: str = os.getenv("SUPER_ADMIN_USERNAME", "admin1")
SUPER_ADMIN_PASSWORD: SecretStr = SecretStr(os.getenv("SUPER_ADMIN_PASSWORD", "admin1"))

EXPIRED_TOKENS_CRON_HOUR: str = os.getenv("EXPIRED_TOKENS_CRON_HOUR", "0")
TIMEZONE: str = os.getenv("TIMEZONE", "Europe/Moscow")

CORS_MODE: str = os.getenv("CORS_MODE", "no-cors")
API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")

PROMETHEUS_URL: str = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")


def get_db_url() -> str:
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def get_auth_data() -> dict:
    return {"secret_key": SECRET_KEY, "algorithm": ALGORITHM}
