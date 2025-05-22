from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from supabase import Client
from uuid import UUID

from src.schemas.filter import FilterCreate
from src.schemas.market_status import MarketStatusCreate
from src.schemas.site_type import SiteTypeCreate
from src.services.supabase_service import get_supabase_client
from src.config import logger


admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)



# FILTERS FILTERS FILTERS FILTERS FILTERS FILTERS FILTERS FILTERS FILTERS FILTERS FILTERS FILTERS

# works well
@admin_router.post("/filters")
async def create_filter(
    filter: FilterCreate,
    market_status_id: UUID4,
    site_type_id: UUID4,
    supabase: Client = Depends(get_supabase_client)
):
    try:
        # Convert filter data and ensure UUIDs are strings
        filter_data = filter.model_dump(exclude={"id", "created_at"})
        
        for key, value in filter_data.items():
            if isinstance(value, UUID):
                filter_data[key] = str(value)

        # Create filter
        response = await supabase.table("filters").insert(filter_data).execute()
        
        if not response.data:
            logger.error(f"Failed to create filter: {filter_data}")
            raise HTTPException(status_code=400, detail="Failed to create filter")

        # Create association
        response_join = await supabase.table("site_type_market_status_filters").insert({
            "site_type_id": str(site_type_id),
            "market_status_id": str(market_status_id),
            "filter_id": response.data[0]["id"]
        }).execute()

        if not response_join.data:
            # Cleanup if association fails
            await supabase.table("filters").delete().eq("id", response.data[0]["id"]).execute()
            logger.error(f"Failed to create filter association: {filter_data}")
            raise HTTPException(status_code=400, detail="Failed to create filter association")

        return response.data[0]

    except Exception as e:
        logger.error(f"Error creating filter: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# SITE TYPES SITE TYPES SITE TYPES SITE TYPES SITE TYPES SITE TYPES SITE TYPES SITE TYPES
@admin_router.post("/site_types")
async def create_site_type(
    site_type: SiteTypeCreate,
    supabase: Client = Depends(get_supabase_client)
):
    try: 
        site_type_data = site_type.model_dump(exclude={"id", "created_at"})

        for key, value in site_type_data.items():
            if isinstance(value, UUID):
                site_type_data[key] = str(value)

        response = await supabase.table("site_types").insert(site_type_data).execute()
        
        if not response.data:
            logger.error(f"Failed to create site type: {site_type_data}")
            raise HTTPException(status_code=400, detail="Failed to create site type")

        return response.data[0]
    except Exception as e:
        logger.error(f"Error creating site type: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")




# MARKET STATUSES MARKET STATUSES MARKET STATUSES MARKET STATUSES MARKET STATUSES MARKET STATUSES
@admin_router.post("/market_status")
async def create_market_status(
    market_status: MarketStatusCreate,
    supabase: Client = Depends(get_supabase_client)
):
    try:
        market_status_data = market_status.model_dump(exclude={"id", "created_at"})

        for key, value in market_status_data.items():
            if isinstance(value, UUID):
                market_status_data[key] = str(value)
                
        response = await supabase.table("market_status").insert(market_status_data).execute()

        if not response.data:
            logger.error(f"Failed to create market status: {market_status_data}")
            raise HTTPException(status_code=400, detail="Failed to create market status")

        return response.data[0]
    except Exception as e:
        logger.error(f"Error creating market status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

