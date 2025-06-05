from typing import List
from fastapi import APIRouter, Body, HTTPException, Path, UploadFile, File, Form
from pydantic import UUID4
from uuid import UUID
import csv
import io
import re

from src.schemas.filter import FilterCreate, FilterUpdate
from src.schemas.market_status import MarketStatusCreate
from src.schemas.order import BatchOrderUpdate
from src.schemas.poi import POI, POICreate, POIUpdate
from src.schemas.site_type import SiteTypeCreate
from src.services.supabase_service import supabase_service
from src.config import logger


admin_router = APIRouter(
    prefix="/admin",
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
        supabase = await supabase_service.client
        response = await supabase.table("template_filters").select("*").order("order").execute()
        
        if not response.data:
            return []
            
        return response.data
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
        supabase = await supabase_service.client
        # Convert filter data and ensure UUIDs are strings
        filter_data = filter.model_dump(exclude={"id", "created_at"})
        
        for key, value in filter_data.items():
            if isinstance(value, UUID):
                filter_data[key] = str(value)

        # Create filter
        response = await supabase.table("filters").insert(filter_data).execute()
        
        if not response.data:
            logger.error(f"Failed to create filter: {filter_data}")
            raise HTTPException(status_code=400, detail="Failed to create filter")

        # Create association
        response_join = await supabase.table("site_type_market_status_filters").insert({
            "site_type_id": str(site_type_id),
            "market_status_id": str(market_status_id),
            "filter_id": response.data[0]["id"]
        }).execute()

        if not response_join.data:
            # Cleanup if association fails
            await supabase.table("filters").delete().eq("id", response.data[0]["id"]).execute()
            logger.error(f"Failed to create filter association: {filter_data}")
            raise HTTPException(status_code=400, detail="Failed to create filter association")

        return response.data[0]

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
        supabase = await supabase_service.client
        
        # Prepare the data for bulk insert
        filter_assignments = [
            {
                "site_type_id": str(site_type_id),
                "market_status_id": str(market_status_id),
                "filter_id": str(filter_id)
            }
            for filter_id in filter_ids
        ]
        
        # Insert the filter assignments
        response = await supabase.table("site_type_market_status_filters").insert(filter_assignments).execute()
        
        if not response.data:
            logger.error(f"Failed to assign filters for site_type_id: {site_type_id} and market_status_id: {market_status_id}")
            raise HTTPException(status_code=400, detail="Failed to assign filters")
        
        return response.data
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
        supabase = await supabase_service.client
        response = await supabase.table("filters").select("*").execute()
        
        if not response.data:
            return []
            
        return response.data
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
        supabase = await supabase_service.client
        
        # Convert to dict and exclude None values to only update provided fields
        update_data = filter_update.model_dump(exclude_unset=True, exclude_none=True)
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields provided for update")
        
        # Convert UUIDs to strings if present
        for key, value in update_data.items():
            if isinstance(value, UUID):
                update_data[key] = str(value)
        
        response = await supabase.table("filters").update(update_data).eq("id", str(filter_id)).execute()
        
        if not response.data:
            logger.error(f"Failed to update filter: {filter_id}")
            raise HTTPException(status_code=404, detail="Filter not found")
            
        return response.data[0]
    except Exception as e:
        logger.error(f"Error updating filter: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@admin_router.delete("/filters/{filter_id}",
    tags=["admin/filters"],
    operation_id="delete_filter",
    summary="Delete a filter",
    description="Deletes a filter and its associated assignments"
)
async def delete_filter(filter_id: UUID4):
    try:
        supabase = await supabase_service.client
        
        # First delete associated filter assignments
        await supabase.table("site_type_market_status_filters").delete().eq("filter_id", str(filter_id)).execute()
        
        # Then delete the filter
        response = await supabase.table("filters").delete().eq("id", str(filter_id)).execute()
        
        if not response.data:
            logger.error(f"Failed to delete filter: {filter_id}")
            raise HTTPException(status_code=404, detail="Filter not found")
            
        return {"message": "Filter deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting filter: {str(e)}")
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
        supabase = await supabase_service.client
        
        # Create a list of updates
        update_operations = []
        for item in updates.updates:
            update_operations.append(
                supabase.table("filters")
                .update({"order": item.order})
                .eq("id", item.id)
                .execute()
            )
        
        # Execute all updates in parallel
        import asyncio
        results = await asyncio.gather(*update_operations, return_exceptions=True)
        
        # Check for errors
        errors = [r for r in results if isinstance(r, Exception)]
        if errors:
            logger.error(f"Errors updating filters order: {errors}")
            raise HTTPException(status_code=500, detail="Failed to update some filters")
            
        return {"message": "Orders updated successfully"}
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
        supabase = await supabase_service.client
        site_type_data = site_type.model_dump(exclude={"id", "created_at"})

        for key, value in site_type_data.items():
            if isinstance(value, UUID):
                site_type_data[key] = str(value)

        response = await supabase.table("site_types").insert(site_type_data).execute()
        
        if not response.data:
            logger.error(f"Failed to create site type: {site_type_data}")
            raise HTTPException(status_code=400, detail="Failed to create site type")

        return response.data[0]
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
        supabase = await supabase_service.client
        response = await supabase.table("site_types").update({"name": name}).eq("id", str(site_type_id)).execute()
        
        if not response.data:
            logger.error(f"Failed to update site type: {site_type_id}")
            raise HTTPException(status_code=404, detail="Site type not found")
            
        return response.data[0]
    except Exception as e:
        logger.error(f"Error updating site type: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@admin_router.delete("/site-types/{site_type_id}",
    tags=["admin/site-types"],
    operation_id="delete_site_type",
    summary="Delete a site type",
    description="Deletes a site type and its associated filter assignments"
)
async def delete_site_type(site_type_id: UUID4):
    try:
        supabase = await supabase_service.client
        
        # First delete associated filter assignments
        await supabase.table("site_type_market_status_filters").delete().eq("site_type_id", str(site_type_id)).execute()
        
        # Then delete the site type
        response = await supabase.table("site_types").delete().eq("id", str(site_type_id)).execute()
        
        if not response.data:
            logger.error(f"Failed to delete site type: {site_type_id}")
            raise HTTPException(status_code=404, detail="Site type not found")
            
        return {"message": "Site type deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting site type: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@admin_router.post("/site-types/batch-order",
    tags=["admin/site-types"],
    operation_id="update_site_types_order",
    summary="Update orders of multiple site types",
    description="Updates the order of multiple site types in a single operation"
)
async def update_site_types_order(updates: BatchOrderUpdate):
    try:
        supabase = await supabase_service.client
        
        # Create a list of updates
        update_operations = []
        for item in updates.updates:
            update_operations.append(
                supabase.table("site_types")
                .update({"order": item.order})
                .eq("id", item.id)
                .execute()
            )
        
        # Execute all updates in parallel
        import asyncio
        results = await asyncio.gather(*update_operations, return_exceptions=True)
        
        # Check for errors
        errors = [r for r in results if isinstance(r, Exception)]
        if errors:
            logger.error(f"Errors updating site types order: {errors}")
            raise HTTPException(status_code=500, detail="Failed to update some site types")
            
        return {"message": "Orders updated successfully"}
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
        supabase = await supabase_service.client
        market_status_data = market_status.model_dump(exclude={"id", "created_at"})

        for key, value in market_status_data.items():
            if isinstance(value, UUID):
                market_status_data[key] = str(value)
                
        response = await supabase.table("market_status").insert(market_status_data).execute()

        if not response.data:
            logger.error(f"Failed to create market status: {market_status_data}")
            raise HTTPException(status_code=400, detail="Failed to create market status")

        return response.data[0]
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
        supabase = await supabase_service.client
        response = await supabase.table("market_status").update({"name": name}).eq("id", str(market_status_id)).execute()
        
        if not response.data:
            logger.error(f"Failed to update market status: {market_status_id}")
            raise HTTPException(status_code=404, detail="Market status not found")
            
        return response.data[0]
    except Exception as e:
        logger.error(f"Error updating market status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@admin_router.delete("/market-status/{market_status_id}",
    tags=["admin/market-status"],
    operation_id="delete_market_status",
    summary="Delete a market status",
    description="Deletes a market status and its associated filter assignments"
)
async def delete_market_status(market_status_id: UUID4):
    try:
        supabase = await supabase_service.client
        
        # First delete associated filter assignments
        await supabase.table("site_type_market_status_filters").delete().eq("market_status_id", str(market_status_id)).execute()
        
        # Then delete the market status
        response = await supabase.table("market_status").delete().eq("id", str(market_status_id)).execute()
        
        if not response.data:
            logger.error(f"Failed to delete market status: {market_status_id}")
            raise HTTPException(status_code=404, detail="Market status not found")
            
        return {"message": "Market status deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting market status: {str(e)}")
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
            details_table_name,
            icon_svg,
            order,
            site_type_id,
            site_types(name)
            """
        ).eq("id", poi_id).execute()
        
        return final_response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating POI: {str(e)}")
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
            details_table_name,
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


@admin_router.post("/poi/batch-order",
    tags=["admin/poi"],
    operation_id="update_pois_order",
    summary="Update orders of multiple POIs",
    description="Updates the order of multiple POIs in a single operation"
)
async def update_pois_order(updates: BatchOrderUpdate):
    try:
        supabase = await supabase_service.client
        
        # Create a list of updates
        update_operations = []
        for item in updates.updates:
            update_operations.append(
                supabase.table("poi")
                .update({"order": item.order})
                .eq("id", item.id)
                .execute()
            )
        
        # Execute all updates in parallel
        import asyncio
        results = await asyncio.gather(*update_operations, return_exceptions=True)
        
        # Check for errors
        errors = [r for r in results if isinstance(r, Exception)]
        if errors:
            logger.error(f"Errors updating POIs order: {errors}")
            raise HTTPException(status_code=500, detail="Failed to update some POIs")
            
        return {"message": "Orders updated successfully"}
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
        # Validate table name (alphanumeric and underscores only)
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
            raise HTTPException(
                status_code=400, 
                detail="Table name must start with a letter or underscore and contain only letters, numbers, and underscores"
            )
        
        # Check if file is CSV
        if not (file.filename and file.filename.endswith('.csv')):
            raise HTTPException(status_code=400, detail="File must be a CSV file")
        
        # Read and decode the CSV file
        content = await file.read()
        csv_content = content.decode('utf-8-sig')  # Handle BOM if present
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        # Expected column names
        expected_columns = {'id', 'latitude', 'longitude', 'business_name'}
        
        # Validate column headers
        if not csv_reader.fieldnames:
            raise HTTPException(status_code=400, detail="CSV file appears to be empty or invalid")
        
        csv_columns = set(csv_reader.fieldnames)
        if csv_columns != expected_columns:
            missing_columns = expected_columns - csv_columns
            extra_columns = csv_columns - expected_columns
            
            error_parts = []
            if missing_columns:
                error_parts.append(f"Missing columns: {', '.join(missing_columns)}")
            if extra_columns:
                error_parts.append(f"Extra columns: {', '.join(extra_columns)}")
            
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid CSV columns. Expected: {', '.join(sorted(expected_columns))}. {' | '.join(error_parts)}"
            )
        
        # Read all rows into memory (since we're not validating data types, this should be fast)
        rows = list(csv_reader)
        if not rows:
            raise HTTPException(status_code=400, detail="CSV file contains no data rows")
        
        supabase = await supabase_service.client
        
        # Check if table already exists
        try:
            table_check = await supabase.table(table_name).select("*").limit(1).execute()
            if table_check.data is not None:  # Table exists and query succeeded
                raise HTTPException(status_code=400, detail=f"Table '{table_name}' already exists")
        except Exception as e:
            # If the error is "relation does not exist" or similar, the table doesn't exist, which is what we want
            if "does not exist" not in str(e).lower():
                # Some other error occurred
                logger.error(f"Error checking table existence: {str(e)}")
                raise HTTPException(status_code=500, detail="Error checking if table exists")
        
        # Create the table using a custom Supabase function
        # First, call the RPC function to create the table with the required schema
        try:
            create_result = await supabase.rpc('create_csv_table', {
                'p_table_name': table_name
            }).execute()
            
            if not create_result.data:
                logger.error(f"Failed to create table {table_name}")
                raise HTTPException(status_code=500, detail="Failed to create table")
                
        except Exception as e:
            error_message = str(e).lower()
            if "already exists" in error_message or "duplicate" in error_message:
                raise HTTPException(status_code=400, detail=f"Table '{table_name}' already exists")
            else:
                logger.error(f"Error creating table {table_name}: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to create table: {str(e)}")
        
        # Prepare data for batch insert
        insert_data = []
        for row in rows:
            insert_data.append({
                'id': row['id'],
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'business_name': row['business_name']
            })
        
        # Insert data in batches to handle large files
        batch_size = 1000
        total_rows = len(insert_data)
        inserted_rows = 0
        
        for i in range(0, total_rows, batch_size):
            batch = insert_data[i:i + batch_size]
            
            try:
                insert_result = await supabase.table(table_name).insert(batch).execute()
                if not insert_result.data:
                    logger.error(f"Failed to insert batch {i//batch_size + 1} for table {table_name}")
                    # If this is not the first batch, we have a partially created table
                    if i > 0:
                        try:
                            await supabase.rpc('drop_table', {'p_table_name': table_name}).execute()
                        except:
                            pass  # Table cleanup failed, but we still need to report the original error
                    raise HTTPException(status_code=500, detail=f"Failed to insert data at batch {i//batch_size + 1}")
                
                inserted_rows += len(batch)
                logger.info(f"Inserted batch {i//batch_size + 1}/{(total_rows + batch_size - 1)//batch_size} for table {table_name}")
                
            except Exception as e:
                logger.error(f"Error inserting batch {i//batch_size + 1}: {str(e)}")
                # Clean up by dropping the table if we've partially inserted data
                if i > 0:
                    try:
                        await supabase.rpc('drop_table', {'p_table_name': table_name}).execute()
                    except:
                        pass  # Table cleanup failed, but we still need to report the original error
                raise HTTPException(status_code=500, detail=f"Failed to insert data: {str(e)}")
        
        logger.info(f"Successfully created table {table_name} with {inserted_rows} rows")
        return {
            "message": f"Table '{table_name}' created successfully",
            "table_name": table_name,
            "rows_processed": inserted_rows
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading CSV table: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")