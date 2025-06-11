from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class UserProfileBase(BaseModel):
    name: Optional[str] = None
    profile_url: Optional[str] = None
    phone_numb: Optional[str] = None
    company_name: Optional[str] = None
    address_1: Optional[str] = None
    address_2: Optional[str] = None
    postcode: Optional[int] = None
    state: Optional[str] = None

class UserProfileCreate(UserProfileBase):
    user_id: UUID

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={UUID: str}
    )

class UserProfileUpdate(UserProfileBase):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={UUID: str}
    )

class UserProfileResponse(UserProfileBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={UUID: str}
    ) 