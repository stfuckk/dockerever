from src.db.database import Base
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declared_attr


class UserRole(Base):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return "user_roles"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        primary_key=True,
        nullable=False,
    )
    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("roles.id"),
        primary_key=True,
        nullable=False,
    )

    user = relationship("User", back_populates="user_roles", uselist=False, lazy="selectin")
    role = relationship("Role", uselist=False, lazy="selectin")

    __table_args__ = (UniqueConstraint("user_id", "role_id", name="unique_user_role"),)
