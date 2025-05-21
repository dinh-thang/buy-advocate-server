from typing import List, Optional
from pydantic import UUID4, BaseModel

from src.schemas.filter import Filter


class SiteTypeFilter(BaseModel):
    filters: Optional[List[Filter]]  

    class Config:
        from_attributes = True
