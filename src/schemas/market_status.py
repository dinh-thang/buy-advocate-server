from pydantic import UUID4
from src.schemas import BaseSchema


class MarketStatusBase(BaseSchema):
    name: str


class MarketStatusCreate(MarketStatusBase):
    pass


class MarketStatus(MarketStatusBase):
    id: UUID4

    class Config:
        from_attributes = True 