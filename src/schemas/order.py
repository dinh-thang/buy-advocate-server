from typing import List
from pydantic import BaseModel


class OrderUpdate(BaseModel):
    id: str
    order: int

class BatchOrderUpdate(BaseModel):
    updates: List[OrderUpdate]