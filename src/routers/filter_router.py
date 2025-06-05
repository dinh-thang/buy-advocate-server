from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from typing import List
from src.config import logger
from src.schemas.user_filter import UserFilterUpdate
from src.services.supabase_service import supabase_service


filter_router = APIRouter(prefix="/filters", tags=["filters"])



@filter_router.get("/default")
async def load_default_filters(
    site_type_id: UUID4,
    market_status_id: UUID4
):
    try:
        supabase = await supabase_service.client
        response = await supabase.table("site_type_market_status_filters").select(
            """
            *,
            filters(
                id,
                filter_type,
                filter_data,
                db_column_name,
                order,
                is_open,
                display_name
            )
            """
        ).eq("site_type_id", str(site_type_id)).eq("market_status_id", str(market_status_id)).execute()

        if not response.data:
            logger.info(f"No default filters found for site_type_id: {site_type_id} and market_status_id: {market_status_id}")
            return []

        # Extract filters and sort them by order
        filters = []
        for item in response.data:
            if item["filters"]:
                filters.append(item["filters"])
        
        sorted_filters = sorted(filters, key=lambda x: x["order"])
        return sorted_filters
    except Exception as e:
        logger.error(f"Error loading default filters: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@filter_router.patch("/batch")
async def update_filters_batch(updates: List[dict]):
    """
    Update multiple filters in a single request.
    Expected input format:
    [
        {
            "id": "uuid-of-filter-1",
            "filter_data": { ... }
        },
        {
            "id": "uuid-of-filter-2",
            "filter_data": { ... }
        }
    ]
    """
    try:
        supabase = await supabase_service.client
        results = []
        for update in updates:
            filter_id = update.get("id")
            if not filter_id:
                raise HTTPException(status_code=400, detail=f"Missing 'id' in update: {update}")
                
            # Convert the filter data to a dictionary
            update_data = {k: v for k, v in update.items() if k != "id"}
                
            logger.info(f"Updating filter {filter_id} with data: {update_data}")
            response = await supabase.table("user_filters").update(update_data).eq("id", str(filter_id)).execute()
            
            if not response.data:
                logger.error(f"No data returned from update operation for filter {filter_id}")
                raise HTTPException(status_code=404, detail=f"Filter not found or update failed for id: {filter_id}")
                
            results.append(response.data[0])
            
        return results
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating filters batch: {str(e)}")
        logger.error(f"Update data was: {updates}")
        raise HTTPException(status_code=500, detail=str(e))


@filter_router.patch("/{filter_id}")
async def update_filter(filter_id: UUID4, filter: UserFilterUpdate):
    try:
        supabase = await supabase_service.client
        # Convert the filter data to a dictionary
        update_data = filter.model_dump(exclude_unset=True)
            
        logger.info(f"Updating filter with data: {update_data}")
        response = await supabase.table("user_filters").update(update_data).eq("id", str(filter_id)).execute()
        
        if not response.data:
            logger.error(f"No data returned from update operation for filter {filter_id}")
            raise HTTPException(status_code=404, detail="Filter not found or update failed")
            
        return response.data[0]
    except Exception as e:
        logger.error(f"Error updating filter {filter_id}: {str(e)}")
        logger.error(f"Update data was: {update_data}")
        raise HTTPException(status_code=500, detail=str(e))
