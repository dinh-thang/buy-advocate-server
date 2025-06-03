from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PoiDetailRequest(BaseModel):
    """Request model for dynamic table query"""
    table_name: str = Field(..., description="Name of the table to query")
    columns: Optional[List[str]] = Field(default=None, description="Specific columns to select (if None, selects all)")
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(default=50, ge=1, le=1000, description="Number of records per page")


class PoiDetailResponse(BaseModel):
    """Response model for dynamic table query"""
    data: List[Dict[str, Any]]
    total_count: int
    page: int
    page_size: int
    total_pages: int 