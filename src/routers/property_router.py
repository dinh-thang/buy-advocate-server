from fastapi import APIRouter, Depends, Body, Query
from typing import List, Optional

from src.services.supabase_service import supabase_service
from src.config import settings, logger
from src.schemas.filter import FilterBase
from src.services.filter_service import apply_min_max_filter, apply_zone_filter, filter_by_zones

TABLE_NAME = settings.PROPERTY_TABLE_NAME


property_router = APIRouter(prefix="/properties", tags=["properties"])

RANGE_FILTERS = [
    "price",
    "land size",
    "traffic",
    "childcare demand ratio" 
] 

ZONE_FILTERS = [
    "zone",
    # permits can go here (single select filter)
] 



@property_router.post("/")
async def get_properties(
    filters: Optional[List[FilterBase]] = Body(default=None, description="List of filters to apply"),
    page: int = Body(default=1, description="Page number (1-based)"),
    page_size: int = Body(default=100, description="Number of records per page")
):
    logger.info(f"Received filters: {filters}, page: {page}, page_size: {page_size}")
    
    supabase = await supabase_service.client
    
    # Calculate range for pagination
    start = (page - 1) * page_size
    end = start + page_size - 1
    
    query = supabase.table(TABLE_NAME).select(
        # PROPERTY LISTING DETAILS
        "id",
        "building_area_m2",
        "days_on_market",
        "listing_date",
        "agent_name",
        "agent_phone_number",
        "description",
        "property_images",
        "asking_price",
        "address",
        "net_income",
        "yield_percentage",
        "sold_price",
        "sold_on",
        "lease_terms",

        # TESTING DATA
        "latitude",  # use for testing now
        "longitude", # use for testing now

        # FILTERS 
        "category",
        "area",
        "zones",
        "traffic_total",
        "overlays",
        "min_dist_to_kfc",
        "min_dist_to_mcdonalds",
        "distance_to_hj",
        "distance_to_gyg",
        "distance_to_grilld",
        "distance_to_cbd",
        "distance_to_redrooster",
        "distance_to_tram",
        "distance_to_train",
        "distance_to_primary",
        "distance_to_secondary",
    ).range(start, end)
    
    # Return all properties if no filters are applied
    if not filters:
        response = await query.execute()
        logger.info(f"Returning paginated properties, count: {len(response.data) if response.data else 0}")
        
        return response.data
    
    # Check for filters and apply them
    for filter_obj in filters:
        filter_name = filter_obj.filter_type.lower()
        
        if filter_name in RANGE_FILTERS:
            query = apply_min_max_filter(query, filter_obj.db_column_name, filter_obj.filter_data)
        elif filter_name in ZONE_FILTERS:
            # query = apply_zone_filter(query, filter_obj.db_column_name, filter_obj.filter_data)
            query = await filter_by_zones(query, filter_obj.db_column_name, filter_obj.filter_data)
    
    response = await query.execute()
    logger.info(f"Filtered and paginated properties count: {len(response.data) if response.data else 0}")

    return response.data