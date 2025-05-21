from typing import List, Optional
from pydantic import UUID4, BaseModel

from src.schemas.filter import Filter


class SiteTypeMarketStatusFilter(BaseModel):
    site_type_id: UUID4
    market_status_id: UUID4
    filter_id: UUID4
    filters: Optional[List[Filter]]

    class Config:
        from_attributes = True 