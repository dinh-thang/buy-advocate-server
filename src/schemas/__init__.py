from pydantic import UUID4, BaseModel
from datetime import datetime
from typing import Optional


class BaseSchema(BaseModel):
    id: Optional[UUID4] = None
    created_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            UUID4: str,
            datetime: lambda dt: dt.isoformat()
        }
