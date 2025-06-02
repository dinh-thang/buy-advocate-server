from fastapi import APIRouter, HTTPException, Path, Body
from typing import List
from pydantic import UUID4
from uuid import UUID

from src.services.supabase_service import supabase_service
from src.schemas.poi import POI, POICreate, POIUpdate
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
            icon_svg,
            order,
            site_type_id,
            site_types(name)
            """
        ).order("order").execute()
        
        if not response.data:
            return []
            
        return response.data
    except Exception as e:
        logger.error(f"Error fetching POI: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@poi_router.post("/{site_type_id}",
    response_model=POI,
    tags=["poi"],
    operation_id="create_poi",
    summary="Create a new POI",
    description="Creates a new point of interest for the specified site type"
)
async def create_poi(
    site_type_id: UUID4 = Path(..., description="Site type ID to associate the POI with"),
    poi: POICreate = Body(..., description="POI data to create")
):
    try:
        supabase = await supabase_service.client
        
        # First check if site_type_id exists
        site_type_check = await supabase.table("site_types").select("id").eq("id", str(site_type_id)).execute()
        if not site_type_check.data:
            raise HTTPException(status_code=404, detail="Site type not found")
        
        # Convert the POI data to a dictionary and add site_type_id
        poi_data = poi.model_dump(exclude={"id", "created_at"})
        poi_data["site_type_id"] = str(site_type_id)
        
        # Convert UUIDs to strings
        for key, value in poi_data.items():
            if isinstance(value, UUID):
                poi_data[key] = str(value)
        
        # Let Supabase handle id and created_at
        response = await supabase.table("poi").insert(poi_data).execute()
        
        if not response.data:
            logger.error(f"Failed to create POI: {poi_data}")
            raise HTTPException(status_code=400, detail="Failed to create POI")
        
        # Get the created POI with site type data
        poi_id = response.data[0]["id"]
        final_response = await supabase.table("poi").select(
            """
            id,
            created_at,
            name,
            db_column_name,
            icon_svg,
            order,
            site_type_id,
            site_types(*)
            """
        ).eq("id", poi_id).execute()
        
        return final_response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating POI: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@poi_router.patch("/{poi_id}",
    response_model=POI,
    tags=["poi"],
    operation_id="update_poi",
    summary="Update a POI",
    description="Updates an existing point of interest"
)
async def update_poi(
    poi_id: UUID4 = Path(..., description="POI ID to update"),
    poi: POIUpdate = Body(..., description="POI data to update")
):
    try:
        supabase = await supabase_service.client
        
        # Check if POI exists
        existing_poi = await supabase.table("poi").select("id").eq("id", str(poi_id)).execute()
        if not existing_poi.data:
            raise HTTPException(status_code=404, detail="POI not found")
        
        # Convert the POI data to a dictionary
        poi_data = poi.model_dump(exclude_unset=True)
        
        if not poi_data:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        # Convert UUIDs to strings
        for key, value in poi_data.items():
            if isinstance(value, UUID):
                poi_data[key] = str(value)
        
        # Update the POI
        response = await supabase.table("poi").update(poi_data).eq("id", str(poi_id)).execute()
        
        if not response.data:
            logger.error(f"Failed to update POI {poi_id}: {poi_data}")
            raise HTTPException(status_code=400, detail="Failed to update POI")
        
        # Get the updated POI with site type data
        final_response = await supabase.table("poi").select(
            """
            id,
            created_at,
            name,
            db_column_name,
            icon_svg,
            order,
            site_type_id,
            site_types(*)
            """
        ).eq("id", str(poi_id)).execute()
        
        return final_response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating POI {poi_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@poi_router.delete("/{poi_id}",
    tags=["poi"],
    operation_id="delete_poi",
    summary="Delete a POI",
    description="Deletes an existing point of interest"
)
async def delete_poi(
    poi_id: UUID4 = Path(..., description="POI ID to delete")
):
    try:
        supabase = await supabase_service.client
        
        # Check if POI exists
        existing_poi = await supabase.table("poi").select("id").eq("id", str(poi_id)).execute()
        if not existing_poi.data:
            raise HTTPException(status_code=404, detail="POI not found")
        
        # Delete the POI
        response = await supabase.table("poi").delete().eq("id", str(poi_id)).execute()
        
        if not response.data:
            logger.error(f"Failed to delete POI {poi_id}")
            raise HTTPException(status_code=400, detail="Failed to delete POI")
        
        return {"message": "POI deleted successfully", "id": str(poi_id)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting POI {poi_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 