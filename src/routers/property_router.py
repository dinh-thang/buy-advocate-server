from fastapi import APIRouter, Body
from typing import List, Optional, Dict, Any
from postgrest.exceptions import APIError

from src.services.supabase_service import supabase_service
from src.config import settings, logger
from src.schemas.filter import FilterBase
from src.services.filter_service import (
    apply_distance_to_poi_filter, 
    apply_min_max_filter, 
    apply_exact_match_filter, 
    apply_supply_demand_ratio_filter, 
    apply_zone_filter,
    is_column_not_exist_error
)


property_router = APIRouter(prefix="/properties", tags=["properties"])


TABLE_NAME = settings.PROPERTY_TABLE_NAME


async def get_property_count(query):
    """Helper to get current query count for performance tracking"""
    try:
        count_response = await query.select("id", count="exact").execute()
        return count_response.count or 0
    except APIError as e:
        if is_column_not_exist_error(e):
            # If the error is due to a non-existent column, return None to indicate we should skip this count
            return None
        raise
    except Exception:
        return 0


@property_router.post("/")
async def get_properties(
    filters: Optional[List[FilterBase]] = Body(default=None, description="List of filters to apply"),
    market_status: Optional[str] = Body(default=None, description="Market status to filter by"),
    page: int = Body(default=1, ge=1, description="Page number (1-based)"),
    page_size: int = Body(default=50, ge=1, le=50, description="Number of records per page, fixed at 50")
) -> Dict[str, Any]:
    supabase = await supabase_service.client
    
    # Log pagination request
    logger.info(f"📄 Received request for page {page} with page size {page_size}")
    
    # Ensure page_size is always 50
    page_size = 50
    
    # Calculate range for pagination (0-based for Supabase)
    start = (page - 1) * page_size
    end = start + page_size - 1
    
    logger.info(f"📄 Fetching records {start} to {end}")
    
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

    # Create count query for performance tracking
    count_query = supabase.table(TABLE_NAME).select("*", count="exact")
    
    # Get initial count and start filter session
    initial_count = await get_property_count(supabase.table(TABLE_NAME).select("id", count="exact"))
    if initial_count is None:
        initial_count = 0
    logger.info(f"🚀 FILTER SESSION START - Initial properties: {initial_count:,}")
    
    current_count = initial_count
    
    # Apply market status filter if provided (even when no other filters)
    if market_status:
        logger.info(f"📥 INPUT: market_status | Value: {market_status}")
        query = apply_exact_match_filter(query, "category", market_status)
        count_query = apply_exact_match_filter(count_query, "category", market_status)
        
        # Track performance
        previous_count = current_count
        current_count = await get_property_count(count_query)
        if current_count is not None:  # Only log metrics if we got a valid count
            eliminated = previous_count - current_count
            logger.info(f"✅ APPLIED: market_status | Remaining: {current_count:,} | Eliminated: {eliminated:,}")
    
    # Apply filters if provided
    if filters:
        for filter_obj in filters:
            filter_type = filter_obj.filter_type.lower()
            
            # Log filter input
            logger.info(f"📥 INPUT: {filter_type} | Column: {filter_obj.db_column_name} | Data: {filter_obj.filter_data}")
            
            previous_count = current_count
            
            try:
                if filter_type.lower() == "range":
                    query = apply_min_max_filter(query, filter_obj.db_column_name, filter_obj.filter_data)
                    count_query = apply_min_max_filter(count_query, filter_obj.db_column_name, filter_obj.filter_data)
                elif filter_type.lower() == "zone":
                    query = apply_zone_filter(query, filter_obj.db_column_name, filter_obj.filter_data)
                    count_query = apply_zone_filter(count_query, filter_obj.db_column_name, filter_obj.filter_data)
                elif filter_type.lower() == "distance_to_poi":
                    query = await apply_distance_to_poi_filter(query, filter_obj.filter_data)
                    count_query = await apply_distance_to_poi_filter(count_query, filter_obj.filter_data)
                elif filter_type.lower() == "supply_demand_ratio":
                    query = await apply_supply_demand_ratio_filter(query, filter_obj.db_column_name, filter_obj.filter_data)
                    count_query = await apply_supply_demand_ratio_filter(count_query, filter_obj.db_column_name, filter_obj.filter_data)
                
                # Track performance after filter
                current_count = await get_property_count(count_query)
                if current_count is not None:  # Only log metrics if we got a valid count
                    eliminated = previous_count - current_count
                    logger.info(f"✅ APPLIED: {filter_type} | Remaining: {current_count:,} | Eliminated: {eliminated:,}")
            except APIError as e:
                if is_column_not_exist_error(e):
                    logger.warning(f"⚠️ Skipping filter due to non-existent column: {filter_obj.db_column_name}")
                    continue
                raise

    try:
        # Get total count for final response
        count_response = await count_query.execute()
        total_count = count_response.count if count_response.count is not None else 0
        
        # Ensure total_count is a valid number
        if not isinstance(total_count, (int, float)) or total_count < 0:
            total_count = 0

        # Calculate total pages
        total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0

        # Apply pagination to the data query
        query = query.range(start, end)
        
        # Get paginated data
        response = await query.execute()
        returned_count = len(response.data) if response.data else 0
        
        # Final session summary with pagination info
        logger.info(f"🏁 FILTER SESSION END - Final: {total_count:,} | Total Eliminated: {initial_count - total_count:,}")
        logger.info(f"📄 PAGINATION - Page: {page}/{total_pages} | Items: {returned_count}/{page_size}")

        return {
            "data": response.data or [],
            "pagination": {
                "total_count": total_count,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
        }
    except APIError as e:
        if is_column_not_exist_error(e):
            # If we hit a non-existent column error at the final execution,
            # return empty results rather than throwing an error
            logger.warning("⚠️ Final query failed due to non-existent column, returning empty results")
            return {
                "data": [],
                "pagination": {
                    "total_count": 0,
                    "total_pages": 0,
                    "current_page": page,
                    "page_size": page_size,
                    "has_next": False,
                    "has_previous": False
                }
            }
        raise