from typing import List, Optional
from pydantic import UUID4, Field
from src.schemas import BaseSchema
from src.schemas.filter import Filter
from src.schemas.site_type_filter import SiteTypeFilter


class SiteTypeBase(BaseSchema):
    name: str
    


class SiteTypeCreate(SiteTypeBase):
    filter_ids: Optional[List[UUID4]] = Field(default_factory=list, description="List of filter IDs associated with this site type")


class SiteType(SiteTypeBase):
    id: UUID4

    site_types_filters: List[SiteTypeFilter]

    class Config:
        from_attributes = True

