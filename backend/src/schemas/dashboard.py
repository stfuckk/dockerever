from pydantic import BaseModel, UUID4
from typing import Optional, List, Literal


class DashboardBlockBase(BaseModel):
    title: str
    type: Literal["diagram", "table"]
    prometheus_query: str
    unit: Optional[str] = None
    container_id: Optional[str] = None
    metric_type: Optional[Literal["cpu", "memory", "network", "network_in", "network_out", "disk"]] = None


class DashboardBlockCreate(DashboardBlockBase):
    pass


class DashboardBlockUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[Literal["diagram", "table"]] = None
    prometheus_query: Optional[str] = None
    unit: Optional[str] = None
    container_id: Optional[str] = None
    metric_type: Optional[Literal["cpu", "memory", "network", "network_in", "network_out", "disk"]] = None


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
    blocks: List[DashboardBlockCreate] = []


class DashboardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class Dashboard(DashboardBase):
    id: UUID4
    blocks: List[DashboardBlock]
    owner_username: Optional[str]
    user_id: Optional[UUID4]

    class Config:
        from_attributes = True
