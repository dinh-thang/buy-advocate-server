from fastapi import APIRouter, Depends, Body
from supabase import Client
from typing import List, Optional

from src.services.supabase_service import get_supabase_client
from src.config import settings, logger
from src.schemas.filter import FilterBase
from src.services.filter_service import apply_min_max_filter


property_router = APIRouter(prefix="/properties", tags=["properties"])

TABLE_NAME = settings.PROPERTY_TABLE_NAME


# FILTERS=[
#     'Zones',
#     'Price',
#     'Land Size',
#     'Traffic',
#     'Overlays',
#     'Frontage',
#     'Corner',
#     'Yield',
#     'Lease Term',
#     'Supply Demand Ratio',
#     'Land Size Rent Per Annum',
#     'POI: Primary schools, Parks, Public Transport',
#     'POI: Hospitals, Pharmacies,Public Transport',
#     'POI: Hospitals, Pharmacies',
#     'POI: Hardware, Shopping Centres, Petrol Stations',
#     'Shopping Centres, Fast Food',
#     'POI: Schools, Shopping centres',
#     'POI: Uni, Public transport, Schools, Shopping',
#     'POI: Public transport, Residential',
#     'POI: Arterial road, Port Ferry, Public Trans',
# ]


@property_router.post("/")
async def get_properties(
    filters: Optional[List[FilterBase]] = Body(default=None, description="List of filters to apply"),
    supabase: Client = Depends(get_supabase_client)
):
    logger.info(f"Received filters: {filters}")
    query = supabase.table(TABLE_NAME).select("*")
    
    if not filters:
        response = await query.execute()
        logger.info(f"Returning all properties, count: {len(response.data) if response.data else 0}")
        return response.data
    
    for filter_obj in filters:
        logger.info(f"Applying filter: {filter_obj}")
        if 'min' in filter_obj.filter_data or 'max' in filter_obj.filter_data:
            query = apply_min_max_filter(query, filter_obj.db_column_name, filter_obj.filter_data)
    
    response = await query.execute()
    logger.info(f"Filtered properties count: {len(response.data) if response.data else 0}")

    return response.data