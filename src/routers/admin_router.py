from typing import List
from fastapi import APIRouter, Body, HTTPException, Path, UploadFile, File, Form
from pydantic import UUID4
from uuid import UUID

from src.schemas.filter import FilterCreate, FilterUpdate
from src.schemas.market_status import MarketStatusCreate
from src.schemas.order import BatchOrderUpdate
from src.schemas.poi import POI, POICreate, POIUpdate
from src.schemas.site_type import SiteTypeCreate
from src.services.admin_service import admin_service
from src.config import logger


admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


# TEMPLATE FILTERS TEMPLATE FILTERS TEMPLATE FILTERS TEMPLATE FILTERS TEMPLATE FILTERS TEMPLATE FILTERS

@admin_router.get("/template-filters",
    tags=["admin/template-filters"],
    operation_id="get_template_filters",
    summary="Get all template filters",
    description="Retrieves all template filters from the database"
)
async def get_template_filters():
    try:
        return await admin_service.get_template_filters()
    except Exception as e:
        logger.error(f"Error fetching template filters: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")




# FILTERS FILTERS FILTERS FILTERS FILTERS FILTERS FILTERS FILTERS FILTERS FILTERS FILTERS FILTERS

@admin_router.post("/filters", 
    tags=["admin/filters"],
    operation_id="create_filter",
    summary="Create a new filter",
    description="Creates a new filter and associates it with a site type and market status"
)
async def create_filter(
    filter: FilterCreate,
    market_status_id: UUID4,
    site_type_id: UUID4
):
    try:
        return await admin_service.create_filter(filter, market_status_id, site_type_id)
    except Exception as e:
        logger.error(f"Error creating filter: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    


@admin_router.post("/site-type-market-status-filters",
    tags=["admin/filters"],
    operation_id="assign_filters",
    summary="Assign filters to site type and market status",
    description="Assigns multiple filters to a specific site type and market status combination"
)
async def assign_filters_to_site_type_market_status(
    site_type_id: UUID4,
    market_status_id: UUID4,
    filter_ids: List[UUID4] = Body(..., embed=True)
):
    try:
        return await admin_service.assign_filters_to_site_type_market_status(site_type_id, market_status_id, filter_ids)
    except Exception as e:
        logger.error(f"Error assigning filters: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@admin_router.get("/filters",
    tags=["admin/filters"],
    operation_id="get_all_filters",
    summary="Get all filters",
    description="Retrieves all filters from the database"
)
async def get_all_filters():
    try:
        return await admin_service.get_all_filters()
    except Exception as e:
        logger.error(f"Error fetching filters: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@admin_router.patch("/filters/{filter_id}",
    tags=["admin/filters"],
    operation_id="update_filter",
    summary="Update a filter",
    description="Updates a filter with only the provided fields"
)
async def update_filter(
    filter_id: UUID4,
    filter_update: FilterUpdate
):
    try:
        return await admin_service.update_filter(filter_id, filter_update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating filter: {str(e)}")
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(status_code=404, detail="Filter not found")
        raise HTTPException(status_code=500, detail="Internal server error")


@admin_router.delete("/filters/{filter_id}",
    tags=["admin/filters"],
    operation_id="delete_filter",
    summary="Delete a filter",
    description="Deletes a filter and its associated assignments"
)
async def delete_filter(filter_id: UUID4):
    try:
        return await admin_service.delete_filter(filter_id)
    except Exception as e:
        logger.error(f"Error deleting filter: {str(e)}")
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(status_code=404, detail="Filter not found")
        raise HTTPException(status_code=500, detail="Internal server error")


@admin_router.post("/filters/batch-order",
    tags=["admin/filters"],
    operation_id="update_filters_order",
    summary="Update orders of multiple filters",
    description="Updates the order of multiple filters for a specific site type and market status"
)
async def update_filters_order(
    site_type_id: UUID4,
    market_status_id: UUID4,
    updates: BatchOrderUpdate
):
    try:
        return await admin_service.update_filters_order(site_type_id, market_status_id, updates)
    except Exception as e:
        logger.error(f"Error updating filters order: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")




# SITE TYPES SITE TYPES SITE TYPES SITE TYPES SITE TYPES SITE TYPES SITE TYPES SITE TYPES

@admin_router.post("/site-types",
    tags=["admin/site-types"],
    operation_id="create_site_type",
    summary="Create a new site type",
    description="Creates a new site type in the database"
)
async def create_site_type(site_type: SiteTypeCreate):
    try:
        return await admin_service.create_site_type(site_type)
    except Exception as e:
        logger.error(f"Error creating site type: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")



@admin_router.patch("/site-types/{site_type_id}",
    tags=["admin/site-types"],
    operation_id="update_site_type",
    summary="Update a site type",
    description="Updates the name of an existing site type"
)
async def update_site_type_name(site_type_id: UUID4, name: str = Body(..., embed=True)):
    try:
        return await admin_service.update_site_type_name(site_type_id, name)
    except Exception as e:
        logger.error(f"Error updating site type: {str(e)}")
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(status_code=404, detail="Site type not found")
        raise HTTPException(status_code=500, detail="Internal server error")


@admin_router.delete("/site-types/{site_type_id}",
    tags=["admin/site-types"],
    operation_id="delete_site_type",
    summary="Delete a site type",
    description="Deletes a site type and its associated filter assignments"
)
async def delete_site_type(site_type_id: UUID4):
    try:
        return await admin_service.delete_site_type(site_type_id)
    except Exception as e:
        logger.error(f"Error deleting site type: {str(e)}")
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(status_code=404, detail="Site type not found")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@admin_router.post("/site-types/batch-order",
    tags=["admin/site-types"],
    operation_id="update_site_types_order",
    summary="Update orders of multiple site types",
    description="Updates the order of multiple site types in a single operation"
)
async def update_site_types_order(updates: BatchOrderUpdate):
    try:
        return await admin_service.update_site_types_order(updates)
    except Exception as e:
        logger.error(f"Error updating site types order: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")





# MARKET STATUSES MARKET STATUSES MARKET STATUSES MARKET STATUSES MARKET STATUSES MARKET STATUSES

@admin_router.post("/market-status",
    tags=["admin/market-status"],
    operation_id="create_market_status",
    summary="Create a new market status",
    description="Creates a new market status in the database"
)
async def create_market_status(market_status: MarketStatusCreate):
    try:
        return await admin_service.create_market_status(market_status)
    except Exception as e:
        logger.error(f"Error creating market status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")



@admin_router.patch("/market-status/{market_status_id}",
    tags=["admin/market-status"],
    operation_id="update_market_status",
    summary="Update a market status",
    description="Updates the name of an existing market status"
)
async def update_market_status_name(market_status_id: UUID4, name: str = Body(..., embed=True)):
    try:
        return await admin_service.update_market_status_name(market_status_id, name)
    except Exception as e:
        logger.error(f"Error updating market status: {str(e)}")
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(status_code=404, detail="Market status not found")
        raise HTTPException(status_code=500, detail="Internal server error")


@admin_router.delete("/market-status/{market_status_id}",
    tags=["admin/market-status"],
    operation_id="delete_market_status",
    summary="Delete a market status",
    description="Deletes a market status and its associated filter assignments"
)
async def delete_market_status(market_status_id: UUID4):
    try:
        return await admin_service.delete_market_status(market_status_id)
    except Exception as e:
        logger.error(f"Error deleting market status: {str(e)}")
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(status_code=404, detail="Market status not found")
        raise HTTPException(status_code=500, detail="Internal server error")





    
# POI POI POI POI POI POI POI POI POI POI POI POI POI POI   
  
@admin_router.post("/poi/{site_type_id}",
response_model=POI,
tags=["admin/poi"],
operation_id="create_poi",
summary="Create a new POI",
description="Creates a new point of interest for the specified site type"
)
async def create_poi(
    site_type_id: UUID4 = Path(..., description="Site type ID to associate the POI with"),
    poi: POICreate = Body(..., description="POI data to create")
):
    try:
        return await admin_service.create_poi(site_type_id, poi)
    except Exception as e:
        logger.error(f"Error creating POI: {str(e)}")
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(status_code=404, detail="Site type not found")
        raise HTTPException(status_code=500, detail="Internal server error")


@admin_router.patch("/poi/{poi_id}",
    response_model=POI,
    tags=["admin/poi"],
    operation_id="update_poi",
    summary="Update a POI",
    description="Updates an existing point of interest"
)
async def update_poi(
    poi_id: UUID4 = Path(..., description="POI ID to update"),
    poi: POIUpdate = Body(..., description="POI data to update")
):
    try:
        return await admin_service.update_poi(poi_id, poi)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating POI {poi_id}: {str(e)}")
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(status_code=404, detail="POI not found")
        raise HTTPException(status_code=500, detail="Internal server error")


@admin_router.delete("/poi/{poi_id}",
    tags=["admin/poi"],
    operation_id="delete_poi",
    summary="Delete a POI",
    description="Deletes an existing point of interest"
)
async def delete_poi(
    poi_id: UUID4 = Path(..., description="POI ID to delete")
):
    try:
        return await admin_service.delete_poi(poi_id)
    except Exception as e:
        logger.error(f"Error deleting POI {poi_id}: {str(e)}")
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(status_code=404, detail="POI not found")
        raise HTTPException(status_code=500, detail="Internal server error")


@admin_router.post("/poi/batch-order",
    tags=["admin/poi"],
    operation_id="update_pois_order",
    summary="Update orders of multiple POIs",
    description="Updates the order of multiple POIs in a single operation"
)
async def update_pois_order(updates: BatchOrderUpdate):
    try:
        return await admin_service.update_pois_order(updates)
    except Exception as e:
        logger.error(f"Error updating POIs order: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")



# CSV TABLE UPLOAD CSV TABLE UPLOAD CSV TABLE UPLOAD CSV TABLE UPLOAD CSV TABLE UPLOAD

@admin_router.post("/upload-csv-table",
    tags=["admin/csv-upload"],
    operation_id="upload_csv_table",
    summary="Create table from CSV upload",
    description="Creates a new table in Supabase and populates it with CSV data"
)
async def upload_csv_table(
    file: UploadFile = File(..., description="CSV file to upload"),
    table_name: str = Form(..., description="Name for the new table")
):
    try:
        # Read the file content
        content = await file.read()
        filename = file.filename
        
        return await admin_service.upload_csv_table(content, table_name, filename)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading CSV table: {str(e)}")
        error_message = str(e)
        if "already exists" in error_message.lower():
            raise HTTPException(status_code=400, detail=error_message)
        raise HTTPException(status_code=500, detail="Internal server error")


# USER MANAGEMENT USER MANAGEMENT USER MANAGEMENT USER MANAGEMENT USER MANAGEMENT USER MANAGEMENT

@admin_router.delete("/users/{user_id}",
    tags=["admin/users"],
    operation_id="delete_user",
    summary="Delete a user",
    description="Deletes a user from the auth.users table"
)
async def delete_user(
    user_id: UUID = Path(..., description="ID of the user to delete")
):
    try:
        return await admin_service.delete_user(user_id)
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")
    
@admin_router.post("/send-invitation-email",
    tags=["admin/users"],
    operation_id="send_invitation_email",
    summary="Send an invitation email to a user",
    description="Sends an invitation email to a user",
    status_code=200
)
async def send_invitation_email(
    email: str = Form(..., description="Email of the user to send the invitation to")
):
    try:
        return await admin_service.send_invitation_email(email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error sending invitation email to {email}: {str(e)}")
        error_message = str(e)
        if "not configured" in error_message.lower():
            raise HTTPException(status_code=500, detail="Email service not configured")
        raise HTTPException(status_code=500, detail="Internal server error while sending email")

    