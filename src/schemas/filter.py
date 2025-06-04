from typing import Dict, Any, Optional

from pydantic import UUID4, Field
from src.schemas import BaseSchema


class FilterBase(BaseSchema):
    filter_type: str
    filter_data: Dict[str, Any] = Field(..., description="Filter data as a JSON object")
    db_column_name: Optional[str] = Field(default=None, description="Database column name, optional for some filter types")
    order: int = Field(default=0, description="Order of the filter")
    is_open: bool = Field(default=False, description="Whether the filter is open")


class FilterCreate(FilterBase):
    pass 


class Filter(FilterBase):
    id: UUID4
    project_id: UUID4

    class Config:
        from_attributes = True
    