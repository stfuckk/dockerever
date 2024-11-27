from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])


# Проверка пароля
def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# Создание хеша пароля
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
