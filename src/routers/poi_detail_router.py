from fastapi import APIRouter, HTTPException, Body
from typing import List

from src.services.supabase_service import supabase_service
from src.config import logger
from src.schemas.poi_detail import PoiDetailRequest, PoiDetailResponse

poi_detail_router = APIRouter(
    prefix="/poi-detail",
    tags=["poi-detail"]
)


# List of allowed tables for security (you should adjust this based on your needs)
ALLOWED_TABLES = [
    "mcdonalds",
]


@poi_detail_router.post("/query",
    response_model=PoiDetailResponse,
    tags=["poi-detail"],
    operation_id="query_poi_detail",
    summary="Query any table with pagination",
    description="Query any allowed table with pagination support"
)
async def query_poi_detail(
    request: PoiDetailRequest = Body(..., description="Query parameters for poi detail")
) -> PoiDetailResponse:
    """
    Query any allowed table with pagination.
    
    - **table_name**: The name of the table to query
    - **columns**: Optional list of specific columns to select
    - **page**: Page number (1-based)
    - **page_size**: Number of records per page (max 1000)
    """
    try:
        # Security check: only allow querying specific tables
        if request.table_name not in ALLOWED_TABLES:
            logger.warning(f"Attempted to query unauthorized table: {request.table_name}")
            raise HTTPException(
                status_code=403, 
                detail=f"Access to table '{request.table_name}' is not allowed. Allowed tables: {', '.join(ALLOWED_TABLES)}"
            )

        supabase = await supabase_service.client
        
        # Calculate pagination parameters
        start = (request.page - 1) * request.page_size
        end = start + request.page_size - 1

        # Build select columns
        if request.columns:
            # Validate column names to prevent injection
            for col in request.columns:
                if not col.replace('_', '').replace('.', '').replace('(', '').replace(')', '').replace('*', '').isalnum() and col != "*":
                    raise HTTPException(status_code=400, detail=f"Invalid column name: {col}")
            columns = ",".join(request.columns)
        else:
            columns = "*"

        # Create base query for data and count
        data_query = supabase.table(request.table_name).select(columns)
        count_query = supabase.table(request.table_name).select("*", count="exact")

        # Get total count first
        count_response = await count_query.execute()
        total_count = count_response.count if count_response.count is not None else 0

        # Apply pagination to data query
        data_query = data_query.range(start, end)

        # Execute the data query
        data_response = await data_query.execute()

        # Calculate total pages
        total_pages = (total_count + request.page_size - 1) // request.page_size

        logger.info(
            f"Poi detail query executed: table={request.table_name}, "
            f"page={request.page}, page_size={request.page_size}, "
            f"total_count={total_count}, results={len(data_response.data) if data_response.data else 0}"
        )

        return PoiDetailResponse(
            data=data_response.data or [],
            total_count=total_count,
            page=request.page,
            page_size=request.page_size,
            total_pages=total_pages
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing poi detail query: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@poi_detail_router.get("/allowed-tables",
    response_model=List[str],
    tags=["poi-detail"],
    operation_id="get_allowed_tables",
    summary="Get list of allowed tables",
    description="Returns the list of tables that can be queried through the poi detail endpoint"
)
async def get_allowed_tables():
    """Get the list of tables that are allowed to be queried."""
    return ALLOWED_TABLES
