from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from src.db.database import Base
from pydantic import UUID4
from typing import Optional


class Dashboard(Base):
    __tablename__ = "dashboards"

    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(default="", nullable=True)
    system: Mapped[bool] = mapped_column(default=False)

    blocks: Mapped[list["DashboardBlock"]] = relationship(
        "DashboardBlock", back_populates="dashboard", cascade="all, delete-orphan"
    )

    user_id: Mapped[UUID4] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)


class DashboardBlock(Base):
    __tablename__ = "dashboard_blocks"

    title: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)  # diagram / table
    prometheus_query: Mapped[str] = mapped_column(nullable=False)
    unit: Mapped[str] = mapped_column(nullable=True)

    dashboard_id: Mapped[int] = mapped_column(ForeignKey("dashboards.id", ondelete="CASCADE"))
    dashboard: Mapped["Dashboard"] = relationship(back_populates="blocks")

    container_id: Mapped[Optional[str]] = mapped_column(nullable=True)
    metric_type: Mapped[Optional[str]] = mapped_column(nullable=True)
