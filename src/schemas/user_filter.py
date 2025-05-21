from pydantic import UUID4
from src.schemas import BaseSchema


class BaseUserFilter(BaseSchema):
    filter_type: str
    filter_data: dict


class UserFilterCreate(BaseUserFilter):
    project_id: UUID4
    site_type_id: UUID4


class UserFilter(BaseUserFilter):
    id: UUID4
    project_id: UUID4
    site_type_id: UUID4

    class Config:
        from_attributes = True
