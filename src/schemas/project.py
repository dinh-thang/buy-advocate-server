from typing import Optional
from pydantic import UUID4
from src.schemas import BaseSchema
from src.schemas.site_type import SiteType


class ProjectBase(BaseSchema):
    title: str


class ProjectCreate(ProjectBase):
    site_type_id: UUID4
    user_id: UUID4


class Project(ProjectBase):
    id: UUID4

    user_id: UUID4
    site_type_id: UUID4

    site_types: SiteType 

    class Config:
        from_attributes = True


