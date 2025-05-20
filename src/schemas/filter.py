from typing import Literal, Optional

from pydantic import UUID4
from schemas import BaseSchema


class FilterBase(BaseSchema):
    filter_type: str
    filter_data: dict


class FilterCreate(FilterBase):
    pass 


class Filter(FilterBase):
    id: UUID4
    project_id: UUID4

    class Config:
        from_attributes = True
    