from typing import Optional, List
from pydantic import UUID4
from src.schemas import BaseSchema
from src.schemas.site_type import SiteType
from src.schemas.user_filter import UserFilter
from src.schemas.market_status import MarketStatus


class ProjectBase(BaseSchema):
    title: str


class ProjectCreate(ProjectBase):
    site_type_id: UUID4
    user_id: UUID4
    market_status_id: UUID4


class ProjectUpdate(ProjectBase):
    title: Optional[str] = None
    site_type_id: Optional[UUID4] = None
    market_status_id: Optional[UUID4] = None

    class Config:
        from_attributes = True
        exclude_unset = True


class Project(ProjectBase):
    id: UUID4

    user_id: UUID4
    site_type_id: UUID4
    market_status_id: UUID4

    site_types: SiteType
    market_status: MarketStatus
    user_filters: List[UserFilter] = []

    class Config:
        from_attributes = True


