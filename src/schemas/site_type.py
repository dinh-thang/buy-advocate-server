import datetime
from typing import List, Optional

from pydantic import UUID4, Field
from src.schemas import BaseSchema


class SiteTypeBase(BaseSchema):
    name: str
    


class SiteTypeCreate(SiteTypeBase):
    filter_ids: Optional[List[UUID4]] = Field(default_factory=list, description="List of filter IDs associated with this site type")


class SiteType(SiteTypeBase):
    id: UUID4

    class Config:
        from_attributes = True

