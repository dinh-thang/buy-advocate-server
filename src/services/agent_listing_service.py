from typing import List, Optional, Dict, Any
from uuid import UUID
from postgrest.exceptions import APIError

from src.services.supabase_service import supabase_service
from src.config import settings, logger
from src.schemas.agent_listing import AgentListingCreate, AgentListingUpdate, AgentListingResponse

TABLE_NAME = "agent_listing_info"

class AgentListingService:
    @staticmethod
    async def create_listing(listing: AgentListingCreate) -> AgentListingResponse:
        """Create a new agent listing"""
        try:
            supabase = await supabase_service.client
            response = await supabase.table(TABLE_NAME).insert(listing.model_dump()).execute()
            
            if not response.data:
                raise Exception("Failed to create listing")
                
            return AgentListingResponse(**response.data[0])
        except Exception as e:
            logger.error(f"Error creating agent listing: {str(e)}")
            raise

    @staticmethod
    async def get_listing(listing_id: UUID, user_id: str) -> Optional[AgentListingResponse]:
        """Get a single agent listing by ID"""
        try:
            supabase = await supabase_service.client
            response = await supabase.table(TABLE_NAME).select("*").eq("id", str(listing_id)).eq("user_id", user_id).execute()
            
            if not response.data:
                return None
                
            return AgentListingResponse(**response.data[0])
        except Exception as e:
            logger.error(f"Error getting agent listing {listing_id}: {str(e)}")
            raise

    @staticmethod
    async def get_listings(
        user_id: str,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get all agent listings with pagination"""
        try:
            supabase = await supabase_service.client
            
            # Calculate range for pagination (0-based for Supabase)
            start = (page - 1) * page_size
            end = start + page_size - 1
            
            # Build base query with user filter
            query = supabase.table(TABLE_NAME).select("*").eq("user_id", user_id)
            
            # Get total count
            count_query = query.select("*", count="exact")
            count_response = await count_query.execute()
            total_count = count_response.count if count_response.count is not None else 0
            
            # Apply pagination
            query = query.range(start, end)
            
            # Get paginated data
            response = await query.execute()
            
            # Calculate total pages
            total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
            
            return {
                "data": [AgentListingResponse(**item) for item in (response.data or [])],
                "pagination": {
                    "total_count": total_count,
                    "total_pages": total_pages,
                    "current_page": page,
                    "page_size": page_size,
                    "has_next": page < total_pages,
                    "has_previous": page > 1
                }
            }
        except Exception as e:
            logger.error(f"Error getting agent listings: {str(e)}")
            raise

    @staticmethod
    async def update_listing(listing_id: UUID, listing: AgentListingUpdate, user_id: str) -> Optional[AgentListingResponse]:
        """Update an agent listing"""
        try:
            supabase = await supabase_service.client
            # Only update fields that are provided (not None)
            update_data = {k: v for k, v in listing.model_dump().items() if v is not None}
            
            if not update_data:
                raise ValueError("No valid fields to update")
                
            response = await supabase.table(TABLE_NAME).update(update_data).eq("id", str(listing_id)).eq("user_id", user_id).execute()
            
            if not response.data:
                return None
                
            return AgentListingResponse(**response.data[0])
        except Exception as e:
            logger.error(f"Error updating agent listing {listing_id}: {str(e)}")
            raise

    @staticmethod
    async def delete_listing(listing_id: UUID, user_id: str) -> bool:
        """Delete an agent listing"""
        try:
            supabase = await supabase_service.client
            response = await supabase.table(TABLE_NAME).delete().eq("id", str(listing_id)).eq("user_id", user_id).execute()
            
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error deleting agent listing {listing_id}: {str(e)}")
            raise

agent_listing_service = AgentListingService() 