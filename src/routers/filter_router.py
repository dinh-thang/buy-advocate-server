from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from supabase import Client
from typing import List
from src.config import logger
from src.schemas.user_filter import UserFilterUpdate
from src.services.supabase_service import get_supabase_client


filter_router = APIRouter(prefix="/filters", tags=["filters"])


# Works well
@filter_router.patch("/batch")
async def update_filters_batch(
    updates: List[dict],
    supabase: Client = Depends(get_supabase_client)
):
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


# Works well
@filter_router.patch("/{filter_id}")
async def update_filter(
    filter_id: UUID4,
    filter: UserFilterUpdate,
    supabase: Client = Depends(get_supabase_client)
):
    try:
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
