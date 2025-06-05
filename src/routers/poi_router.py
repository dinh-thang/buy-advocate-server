from fastapi import APIRouter, HTTPException
from typing import List

from src.services.supabase_service import supabase_service
from src.schemas.poi import POI
from src.config import logger

poi_router = APIRouter(
    prefix="/poi",
    tags=["poi"]
)


@poi_router.get("/",
    response_model=List[POI],
    tags=["poi"],
    operation_id="get_all_poi",
    summary="Get all POI",
    description="Retrieves all points of interest with their details"
)
async def get_all_poi():
    try:
        supabase = await supabase_service.client
        response = await supabase.table("poi").select(
            """
            id,
            created_at,
            name,
            db_column_name,
            details_table_name,
            icon_svg,
            order,
            site_type_id,
            site_types(name),
            details_table_name
            """
        ).order("order").execute()
        
        if not response.data:
            return []
            
        return response.data
    except Exception as e:
        logger.error(f"Error fetching POI: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
