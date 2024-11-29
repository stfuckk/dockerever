from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base, str_uniq, int_pk


class User(Base):
    # Основные поля таблицы
    id: Mapped[int_pk]
    username: Mapped[str_uniq]
    first_name: Mapped[str]
    last_name: Mapped[str]
    password: Mapped[str]

    # Роли
    is_admin: Mapped[bool] = mapped_column(default=False)

    extend_existing = True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"
