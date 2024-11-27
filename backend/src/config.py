import os
from dotenv import load_dotenv

load_dotenv()

DB_USER: str = os.getenv("POSTGRES_USER", "user")
DB_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST: str = os.getenv("DB_HOST", "host")
DB_PORT: str = os.getenv("DB_PORT", "port")
DB_NAME: str = os.getenv("POSTGRES_DB", "dbname")

SECRET_KEY: str = os.getenv("SECRET_KEY", "secret_key")
ALGORITHM: str = os.getenv("ALGORITHM", "algorithm")


def get_db_url() -> str:
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def get_auth_data() -> dict:
    return {"secret_key": SECRET_KEY, "algorithm": ALGORITHM}
