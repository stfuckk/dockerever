from pydantic import BaseModel, UUID4
from typing import Optional, List, Literal


class DashboardBlockBase(BaseModel):
    title: str
    type: Literal["diagram", "table"]
    prometheus_query: str
    unit: Optional[str] = None


class DashboardBlockCreate(DashboardBlockBase):
    pass


class DashboardBlock(DashboardBlockBase):
    id: UUID4
    dashboard_id: UUID4

    class Config:
        from_attributes = True


class DashboardBase(BaseModel):
    title: str
    description: Optional[str] = ""
    system: bool = False


class DashboardCreate(DashboardBase):
    blocks: List[DashboardBlockCreate]


class Dashboard(DashboardBase):
    id: UUID4
    blocks: List[DashboardBlock]

    class Config:
        from_attributes = True
