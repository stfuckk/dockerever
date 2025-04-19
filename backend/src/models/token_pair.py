from typing import Annotated
from sqlalchemy.orm import Mapped, mapped_column, declared_attr
from src.db.database import Base
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime


class TokenPair(Base):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return "token_pairs"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    hashed_access_token: Mapped[Annotated[str, mapped_column(nullable=False)]]
    hashed_refresh_token: Mapped[Annotated[str, mapped_column(nullable=False)]]

    expires_at: Mapped[datetime]

    __table_args__ = (
        UniqueConstraint("hashed_access_token", "hashed_refresh_token", name="uq_unique_token_pair"),
        UniqueConstraint("hashed_access_token", name="uq_hashed_access_token"),
        UniqueConstraint("hashed_refresh_token", name="uq_hashed_refresh_token"),
    )
