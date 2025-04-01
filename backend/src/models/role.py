from typing import Annotated
from sqlalchemy.orm import Mapped, mapped_column, declared_attr
from src.db.database import Base
from sqlalchemy import Text


class Role(Base):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return "roles"

    name: Mapped[Annotated[str, mapped_column(nullable=False)]]
    description_ru: Mapped[Annotated[str, mapped_column(Text, nullable=False)]]
    description_en: Mapped[Annotated[str, mapped_column(Text, nullable=False)]]
