from typing import Dict, Any, Optional

from pydantic import UUID4, Field
from src.schemas import BaseSchema


class FilterBase(BaseSchema):
    filter_type: str
    filter_data: Dict[str, Any] = Field(..., description="Filter data as a JSON object")
    db_column_name: str


class FilterCreate(FilterBase):
    pass 


class Filter(FilterBase):
    id: UUID4
    project_id: UUID4

    class Config:
        from_attributes = True
    