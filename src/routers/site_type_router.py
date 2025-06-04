from fastapi import APIRouter, HTTPException
from src.services.supabase_service import supabase_service
from src.config import logger

site_type_router = APIRouter(prefix="/site-types", tags=["site-types"])


@site_type_router.get("/",
    tags=["site-types"],
    operation_id="get_all_site_types",
    summary="Get all site types",
    description="Retrieves all site types with their IDs and names"
)
async def get_all_site_types():
    try:
        supabase = await supabase_service.client
        response = await supabase.table("site_types").select("id, name, icon, order").order("order").execute()
        
        if not response.data:
            return []
            
        return response.data
    except Exception as e:
        logger.error(f"Error fetching site types: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")