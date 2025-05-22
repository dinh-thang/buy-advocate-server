from typing import Any, Dict, Optional
from pydantic import UUID4, Field
from src.schemas import BaseSchema


class BaseUserFilter(BaseSchema):
    filter_type: str
    filter_data: Dict[str, Any] = Field(..., description="Filter data as a JSON object")
    db_column_name: str


class UserFilterCreate(BaseUserFilter):
    project_id: UUID4


class UserFilterUpdate(BaseUserFilter):    
    filter_type: Optional[str] = None
    filter_data: Optional[Dict[str, Any]] = None
    db_column_name: Optional[str] = None


class UserFilter(BaseUserFilter):
    id: UUID4
    project_id: UUID4

    class Config:
        from_attributes = True
