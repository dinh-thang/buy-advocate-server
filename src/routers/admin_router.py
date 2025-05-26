from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import UUID4
from uuid import UUID

from src.schemas.filter import FilterCreate
from src.schemas.market_status import MarketStatusCreate
from src.schemas.site_type import SiteTypeCreate
from src.services.supabase_service import supabase_service
from src.config import logger


admin_router = APIRouter(
    prefix="/admin",
)


# FILTERS FILTERS FILTERS FILTERS FILTERS FILTERS FILTERS FILTERS FILTERS FILTERS FILTERS FILTERS
@admin_router.post("/filters", 
    tags=["admin/filters"],
    operation_id="create_filter",
    summary="Create a new filter",
    description="Creates a new filter and associates it with a site type and market status"
)
async def create_filter(
    filter: FilterCreate,
    market_status_id: UUID4,
    site_type_id: UUID4
):
    try:
        supabase = await supabase_service.client
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
    


@admin_router.post("/site_type_market_status_filters",
    tags=["admin/filters"],
    operation_id="assign_filters",
    summary="Assign filters to site type and market status",
    description="Assigns multiple filters to a specific site type and market status combination"
)
async def assign_filters_to_site_type_market_status(
    site_type_id: UUID4,
    market_status_id: UUID4,
    filter_ids: List[UUID4] = Body(..., embed=True)
):
    try:
        supabase = await supabase_service.client
        
        # Prepare the data for bulk insert
        filter_assignments = [
            {
                "site_type_id": str(site_type_id),
                "market_status_id": str(market_status_id),
                "filter_id": str(filter_id)
            }
            for filter_id in filter_ids
        ]
        
        # Insert the filter assignments
        response = await supabase.table("site_type_market_status_filters").insert(filter_assignments).execute()
        
        if not response.data:
            logger.error(f"Failed to assign filters for site_type_id: {site_type_id} and market_status_id: {market_status_id}")
            raise HTTPException(status_code=400, detail="Failed to assign filters")
        
        return response.data
    except Exception as e:
        logger.error(f"Error assigning filters: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@admin_router.get("/filters",
    tags=["admin/filters"],
    operation_id="get_all_filters",
    summary="Get all filters",
    description="Retrieves all filters from the database"
)
async def get_all_filters():
    try:
        supabase = await supabase_service.client
        response = await supabase.table("filters").select("*").execute()
        
        if not response.data:
            return []
            
        return response.data
    except Exception as e:
        logger.error(f"Error fetching filters: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@admin_router.patch("/filters/{filter_id}",
    tags=["admin/filters"],
    operation_id="update_filter",
    summary="Update a filter",
    description="Updates the name and filter data of an existing filter"
)
async def update_filter(
    filter_id: UUID4,
    filter_name: str = Body(..., embed=True),
    filter_data: dict = Body(..., embed=True)
):
    try:
        supabase = await supabase_service.client
        
        # Prepare update data
        update_data = {
            "name": filter_name,
            "filter_data": filter_data
        }
        
        response = await supabase.table("filters").update(update_data).eq("id", str(filter_id)).execute()
        
        if not response.data:
            logger.error(f"Failed to update filter: {filter_id}")
            raise HTTPException(status_code=404, detail="Filter not found")
            
        return response.data[0]
    except Exception as e:
        logger.error(f"Error updating filter: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@admin_router.delete("/filters/{filter_id}",
    tags=["admin/filters"],
    operation_id="delete_filter",
    summary="Delete a filter",
    description="Deletes a filter and its associated assignments"
)
async def delete_filter(filter_id: UUID4):
    try:
        supabase = await supabase_service.client
        
        # First delete associated filter assignments
        await supabase.table("site_type_market_status_filters").delete().eq("filter_id", str(filter_id)).execute()
        
        # Then delete the filter
        response = await supabase.table("filters").delete().eq("id", str(filter_id)).execute()
        
        if not response.data:
            logger.error(f"Failed to delete filter: {filter_id}")
            raise HTTPException(status_code=404, detail="Filter not found")
            
        return {"message": "Filter deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting filter: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# SITE TYPES SITE TYPES SITE TYPES SITE TYPES SITE TYPES SITE TYPES SITE TYPES SITE TYPES
@admin_router.post("/site_types",
    tags=["admin/site-types"],
    operation_id="create_site_type",
    summary="Create a new site type",
    description="Creates a new site type in the database"
)
async def create_site_type(site_type: SiteTypeCreate):
    try:
        supabase = await supabase_service.client
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



@admin_router.patch("/site_types/{site_type_id}",
    tags=["admin/site-types"],
    operation_id="update_site_type",
    summary="Update a site type",
    description="Updates the name of an existing site type"
)
async def update_site_type_name(site_type_id: UUID4, name: str = Body(..., embed=True)):
    try:
        supabase = await supabase_service.client
        response = await supabase.table("site_types").update({"name": name}).eq("id", str(site_type_id)).execute()
        
        if not response.data:
            logger.error(f"Failed to update site type: {site_type_id}")
            raise HTTPException(status_code=404, detail="Site type not found")
            
        return response.data[0]
    except Exception as e:
        logger.error(f"Error updating site type: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@admin_router.delete("/site_types/{site_type_id}",
    tags=["admin/site-types"],
    operation_id="delete_site_type",
    summary="Delete a site type",
    description="Deletes a site type and its associated filter assignments"
)
async def delete_site_type(site_type_id: UUID4):
    try:
        supabase = await supabase_service.client
        
        # First delete associated filter assignments
        await supabase.table("site_type_market_status_filters").delete().eq("site_type_id", str(site_type_id)).execute()
        
        # Then delete the site type
        response = await supabase.table("site_types").delete().eq("id", str(site_type_id)).execute()
        
        if not response.data:
            logger.error(f"Failed to delete site type: {site_type_id}")
            raise HTTPException(status_code=404, detail="Site type not found")
            
        return {"message": "Site type deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting site type: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# MARKET STATUSES MARKET STATUSES MARKET STATUSES MARKET STATUSES MARKET STATUSES MARKET STATUSES
@admin_router.post("/market_status",
    tags=["admin/market-status"],
    operation_id="create_market_status",
    summary="Create a new market status",
    description="Creates a new market status in the database"
)
async def create_market_status(market_status: MarketStatusCreate):
    try:
        supabase = await supabase_service.client
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



@admin_router.patch("/market_status/{market_status_id}",
    tags=["admin/market-status"],
    operation_id="update_market_status",
    summary="Update a market status",
    description="Updates the name of an existing market status"
)
async def update_market_status_name(market_status_id: UUID4, name: str = Body(..., embed=True)):
    try:
        supabase = await supabase_service.client
        response = await supabase.table("market_status").update({"name": name}).eq("id", str(market_status_id)).execute()
        
        if not response.data:
            logger.error(f"Failed to update market status: {market_status_id}")
            raise HTTPException(status_code=404, detail="Market status not found")
            
        return response.data[0]
    except Exception as e:
        logger.error(f"Error updating market status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@admin_router.delete("/market_status/{market_status_id}",
    tags=["admin/market-status"],
    operation_id="delete_market_status",
    summary="Delete a market status",
    description="Deletes a market status and its associated filter assignments"
)
async def delete_market_status(market_status_id: UUID4):
    try:
        supabase = await supabase_service.client
        
        # First delete associated filter assignments
        await supabase.table("site_type_market_status_filters").delete().eq("market_status_id", str(market_status_id)).execute()
        
        # Then delete the market status
        response = await supabase.table("market_status").delete().eq("id", str(market_status_id)).execute()
        
        if not response.data:
            logger.error(f"Failed to delete market status: {market_status_id}")
            raise HTTPException(status_code=404, detail="Market status not found")
            
        return {"message": "Market status deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting market status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")