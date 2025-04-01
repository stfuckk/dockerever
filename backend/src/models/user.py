from typing import Annotated
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.user_role import UserRole
from src.db.database import Base
from src.models.role import Role
from typing import List


class User(Base):
    username: Mapped[Annotated[str, mapped_column(nullable=True)]]
    hashed_password: Mapped[Annotated[str, mapped_column(nullable=False)]]

    is_active: Mapped[Annotated[bool, mapped_column(default=True)]]

    user_roles: Mapped[List["UserRole"]] = relationship("UserRole", back_populates="user", lazy="selectin")
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        lazy="selectin",
        secondary="user_roles",
        viewonly=True,
    )

    def has_role(self, role_names: list[str]) -> bool:
        for role in self.roles:
            if role.name in role_names:
                return True

        return False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"
