from fastapi import APIRouter, HTTPException
from src.services.supabase_service import supabase_service
from src.config import logger

market_status_router = APIRouter(
    prefix="/market-status",
    tags=["market-status"]
)


@market_status_router.get("/",
    tags=["market-status"],
    operation_id="get_all_market_statuses",
    summary="Get all market statuses",
    description="Retrieves all market statuses with their IDs and names"
)
async def get_all_market_statuses():
    try:
        supabase = await supabase_service.client
        response = await supabase.table("market_status").select("id, name").execute()
        
        if not response.data:
            return []
            
        return response.data
    except Exception as e:
        logger.error(f"Error fetching market statuses: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")