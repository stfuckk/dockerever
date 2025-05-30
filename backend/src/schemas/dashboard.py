from pydantic import BaseModel, UUID4
from typing import Optional, List, Literal


class DashboardBlockBase(BaseModel):
    title: Optional[str]
    type: Optional[Literal["diagram", "table"]]
    unit: Optional[str] = None
    container_id: Optional[str] = None
    metric_type: Optional[Literal["cpu", "memory", "network", "disk"]] = None


class DashboardBlockCreate(DashboardBlockBase):
    pass


class DashboardBlockUpdate(DashboardBlockBase):
    title: Optional[str] = None
    type: Optional[Literal["diagram", "table"]] = None
    container_id: Optional[str] = None
    metric_type: Optional[Literal["cpu", "memory", "network", "disk"]] = None


class DashboardBlock(DashboardBlockBase):
    id: UUID4
    dashboard_id: UUID4
    prometheus_query: str

    class Config:
        from_attributes = True


class DashboardBase(BaseModel):
    title: str
    description: Optional[str] = ""
    system: bool = False


class DashboardCreate(DashboardBase):
    blocks: List[DashboardBlockCreate] = []


class DashboardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class Dashboard(DashboardBase):
    id: UUID4
    blocks: List[DashboardBlock]
    user_id: Optional[UUID4]

    class Config:
        from_attributes = True
