from typing import Optional
from pydantic import UUID4, Field
from src.schemas import BaseSchema


class SiteTypeBasic(BaseSchema):
    name: str


class POIBase(BaseSchema):
    name: str
    db_column_name: str
    icon_svg: str
    order: int = Field(description="Order for displaying POI")
    details_table_name: str = Field(description="Name of the table to fetch details from")


class POICreate(POIBase):
    pass


class POIUpdate(BaseSchema):
    name: Optional[str] = None
    db_column_name: Optional[str] = None
    icon_svg: Optional[str] = None
    order: Optional[int] = None
    details_table_name: Optional[str] = None

    class Config:
        from_attributes = True
        exclude_unset = True


class POI(POIBase):
    id: UUID4
    site_type_id: UUID4
    
    site_types: Optional[SiteTypeBasic] = None

    class Config:
        from_attributes = True
