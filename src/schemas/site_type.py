from typing import List, Optional
from pydantic import UUID4, Field
from src.schemas import BaseSchema
from src.schemas.filter import Filter
from src.schemas.site_type_market_status_filter import SiteTypeMarketStatusFilter


class SiteTypeBase(BaseSchema):
    name: str
    


class SiteTypeCreate(SiteTypeBase):
    pass


class SiteType(SiteTypeBase):
    id: UUID4

    site_type_market_status_filters: List[SiteTypeMarketStatusFilter]

    class Config:
        from_attributes = True

