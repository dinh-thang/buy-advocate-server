from typing import Any, Dict, Optional
from pydantic import UUID4, Field
from src.schemas import BaseSchema


class BaseUserFilter(BaseSchema):
    filter_type: str
    filter_data: Dict[str, Any] = Field(..., description="Filter data as a JSON object")
    db_column_name: str
    order: int = Field(default=0, description="Order of the filter")
    is_open: bool = Field(default=False, description="Whether the filter is open")


class UserFilterCreate(BaseUserFilter):
    project_id: UUID4


class UserFilterUpdate(BaseUserFilter):    
    filter_type: Optional[str] = None
    filter_data: Optional[Dict[str, Any]] = None
    db_column_name: Optional[str] = None
    order: Optional[int] = None
    is_open: Optional[bool] = None


class UserFilter(BaseUserFilter):
    id: UUID4
    project_id: UUID4

    class Config:
        from_attributes = True
