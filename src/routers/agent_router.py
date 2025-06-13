from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Dict, Any
from uuid import UUID

from src.middleware.auth import get_current_user
from src.services.agent_listing_service import agent_listing_service
from src.schemas.agent_listing import AgentListingCreate, AgentListingUpdate, AgentListingResponse

agent_router = APIRouter(prefix="/agent", tags=["agent"])

@agent_router.post("/listings", response_model=AgentListingResponse)
async def create_listing(
    listing: AgentListingCreate,
    current_user_id: str = Depends(get_current_user)
) -> AgentListingResponse:
    """Create a new agent listing"""
    try:
        # Set the user_id from the current user
        listing.user_id = current_user_id
        return await agent_listing_service.create_listing(listing)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@agent_router.get("/listings/{listing_id}", response_model=AgentListingResponse)
async def get_listing(
    listing_id: UUID,
    current_user_id: str = Depends(get_current_user)
) -> AgentListingResponse:
    """Get a single agent listing by ID"""
    listing = await agent_listing_service.get_listing(listing_id, current_user_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing

@agent_router.get("/listings", response_model=Dict[str, Any])
async def get_listings(
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(default=50, ge=1, le=50, description="Number of records per page"),
    current_user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get all agent listings with pagination"""
    try:
        return await agent_listing_service.get_listings(current_user_id, page, page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@agent_router.patch("/listings/{listing_id}", response_model=AgentListingResponse)
async def update_listing(
    listing_id: UUID,
    listing: AgentListingUpdate,
    current_user_id: str = Depends(get_current_user)
) -> AgentListingResponse:
    """Update an agent listing"""
    updated_listing = await agent_listing_service.update_listing(listing_id, listing, current_user_id)
    if not updated_listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return updated_listing

@agent_router.delete("/listings/{listing_id}")
async def delete_listing(
    listing_id: UUID,
    current_user_id: str = Depends(get_current_user)
) -> Dict[str, bool]:
    """Delete an agent listing"""
    success = await agent_listing_service.delete_listing(listing_id, current_user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Listing not found")
    return {"success": True} 