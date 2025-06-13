from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

class AgentListingBase(BaseModel):
    market_status_id: Optional[UUID] = None
    is_active: Optional[bool] = False
    day_on_market: Optional[int] = Field(default=0, ge=0)
    total_view: Optional[int] = Field(default=0, ge=0)
    total_engagement: Optional[int] = Field(default=0, ge=0)
    total_save: Optional[int] = Field(default=0, ge=0)
    total_mail_enquiry: Optional[int] = Field(default=0, ge=0)
    total_call_enquiry: Optional[int] = Field(default=0, ge=0)
    address: Optional[str] = None
    suburb: Optional[str] = None
    postcode: Optional[int] = Field(default=0, ge=0)
    state: Optional[str] = None

class AgentListingCreate(AgentListingBase):
    user_id: str

class AgentListingUpdate(BaseModel):
    market_status_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    day_on_market: Optional[int] = Field(default=None, ge=0)
    total_view: Optional[int] = Field(default=None, ge=0)
    total_engagement: Optional[int] = Field(default=None, ge=0)
    total_save: Optional[int] = Field(default=None, ge=0)
    total_mail_enquiry: Optional[int] = Field(default=None, ge=0)
    total_call_enquiry: Optional[int] = Field(default=None, ge=0)
    address: Optional[str] = None
    suburb: Optional[str] = None
    postcode: Optional[int] = Field(default=None, ge=0)
    state: Optional[str] = None

class AgentListingInDB(AgentListingBase):
    id: UUID
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class AgentListingResponse(AgentListingInDB):
    pass 