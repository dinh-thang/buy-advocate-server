from fastapi import APIRouter, Depends, Body, Query
from typing import List, Optional, Dict, Any

from src.services.supabase_service import supabase_service
from src.config import settings, logger
from src.schemas.filter import FilterBase
from src.services.filter_service import apply_min_max_filter, apply_single_value_filter, apply_exact_match_filter, apply_zone_filter

TABLE_NAME = settings.PROPERTY_TABLE_NAME


property_router = APIRouter(prefix="/properties", tags=["properties"])

RANGE_FILTERS = [
    "price",
    "land size",
    "traffic",
] 

ZONE_FILTERS = [
    "zone",
] 



@property_router.post("/")
async def get_properties(
    filters: Optional[List[FilterBase]] = Body(default=None, description="List of filters to apply"),
    market_status: Optional[str] = Body(default=None, description="Market status to filter by"),
    
    page: int = Body(default=1, description="Page number (1-based)"),
    page_size: int = Body(default=100, description="Number of records per page")
) -> Dict[str, Any]:
    logger.info(f"Received filters: {filters}, market_status: {market_status}, page: {page}, page_size: {page_size}")
    
    supabase = await supabase_service.client
    
    # Calculate range for pagination
    start = (page - 1) * page_size
    end = start + page_size - 1
    
    query = supabase.table(TABLE_NAME).select(
        # PROPERTY LISTING DETAILS
        "id",
        "land_area_m2",
        "days_on_market",
        "listing_date",
        "agent_name",
        "agent_phone_number",
        "description",
        "property_images",
        "asking_price",
        "max_price_range",
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
        "property_type",
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
    )

    # Create count query
    count_query = supabase.table(TABLE_NAME).select("*", count="exact")
    
    # Apply market status filter if provided (even when no other filters)
    if market_status:
        logger.info(f"Applying market status filter: {market_status}")
        query = apply_exact_match_filter(query, "category", market_status)
        count_query = apply_exact_match_filter(count_query, "category", market_status)
    
    # Apply filters if provided
    if filters:
        for filter_obj in filters:
            filter_name = filter_obj.filter_type.lower()
            
            logger.info(f"Processing filter: {filter_name}, column: {filter_obj.db_column_name}, data: {filter_obj.filter_data}")
            
            if filter_name in [f.lower() for f in RANGE_FILTERS]:
                query = apply_min_max_filter(query, filter_obj.db_column_name, filter_obj.filter_data)
                count_query = apply_min_max_filter(count_query, filter_obj.db_column_name, filter_obj.filter_data)
            elif filter_name in [f.lower() for f in ZONE_FILTERS]:
                query = apply_zone_filter(query, filter_obj.db_column_name, filter_obj.filter_data)
                count_query = apply_zone_filter(count_query, filter_obj.db_column_name, filter_obj.filter_data)
            else:
                query = apply_single_value_filter(query, filter_obj.db_column_name, filter_obj.filter_data)
                count_query = apply_single_value_filter(count_query, filter_obj.db_column_name, filter_obj.filter_data)

    # Get total count first
    count_response = await count_query.execute()
    total_count = count_response.count if count_response.count is not None else 0

    # Apply pagination to the data query
    query = query.range(start, end)
    
    # Get paginated data
    response = await query.execute()
    logger.info(f"Returning paginated properties, count: {len(response.data) if response.data else 0}, total: {total_count}")

    return {
        "data": response.data,
        "total_count": total_count
    }