from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List
from pydantic import UUID4
from uuid import UUID

from src.services.supabase_service import supabase_service
from src.schemas.project import Project, ProjectCreate, ProjectBase, ProjectUpdate
from src.config import logger
from src.middleware.auth import get_current_user
 
project_router = APIRouter(
    prefix="/projects",
    tags=["projects"]
)


# THIS RETURN THE SAVED FILTER CONFIG, NOT THE DEFAULT CONFIGS
@project_router.get("/{project_id}")
async def get_project(project_id: UUID4):
    supabase = await supabase_service.client
    response = await supabase.table("projects").select(
        """
        id,
        created_at,
        title,
        market_status(*),
        site_types(*),
        user_filters(*)
        """
    ).eq("id", project_id).execute()

    if not response.data:
        logger.error(f"Project not found with id: {project_id}")
        raise HTTPException(status_code=404, detail="Project not found")
    
    return response.data[0]


@project_router.get("/")
async def get_all_projects(
    user_id: str = Depends(get_current_user)
):
    try:
        supabase = await supabase_service.client
        query = supabase.table("projects").select(
        """
        id,
        created_at,
        title,
        market_status(*),
        site_types(*),
        user_filters(*)
        """
        ).eq("user_id", user_id)
        response = await query.execute()

        return response.data
    except Exception as e:
        logger.error(f"Error fetching projects: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@project_router.post("/")
async def create_project(project: ProjectCreate):
    try:
        supabase = await supabase_service.client
        # Convert the project data to a dictionary and ensure UUIDs are strings
        project_data = project.model_dump(exclude={"id", "created_at"})
        
        for key, value in project_data.items():
            if isinstance(value, UUID):
                project_data[key] = str(value)
        
        # Let Supabase handle id and created_at
        response = await supabase.table("projects").insert(project_data).execute()
        
        if not response.data:
            logger.error(f"Failed to create project: {project_data}")
            raise HTTPException(status_code=400, detail="Failed to create project")
        
        # Get the created project data
        project_result = response.data[0]
        
        # Fetch the matching filters for this site type and market status
        filters_response = await supabase.table("site_type_market_status_filters").select(
            """
            *,
            filters(*)
            """
        ).eq("site_type_id", str(project.site_type_id)).eq("market_status_id", str(project.market_status_id)).execute()
        
        if filters_response.data:
            # Create user_filters entries for each filter
            user_filters = []
            for filter_association in filters_response.data:
                filter_data = filter_association["filters"]
                user_filter = {
                    "project_id": str(project_result["id"]),
                    "filter_type": filter_data["filter_type"],
                    "filter_data": filter_data["filter_data"],
                    "db_column_name": filter_data["db_column_name"]
                }
                user_filters.append(user_filter)
                
            if user_filters:
                await supabase.table("user_filters").insert(user_filters).execute()
        
        # Get the final project data with all relations
        final_response = await supabase.table("projects").select(
            """
            id,
            created_at,
            title,
            market_status!inner(
                id,
                name
            ),
            site_types!inner(
                id,
                name
            ),
            user_filters(
                id,
                filter_type,
                filter_data,
                db_column_name
            )
            """
        ).eq("id", project_result["id"]).execute()
        
        return final_response.data[0]
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@project_router.patch("/{project_id}")
async def update_project(project_id: UUID4, project: ProjectUpdate):
    try:
        supabase = await supabase_service.client
        # Convert the project data to a dictionary and ensure UUIDs are strings
        project_data = project.model_dump(exclude_unset=True)
        
        if not project_data:
            raise HTTPException(status_code=400, detail="No valid fields to update")
            
        for key, value in project_data.items():
            if isinstance(value, UUID):
                project_data[key] = str(value)
        
        response = await supabase.table("projects").update(project_data).eq("id", str(project_id)).execute()
        
        if not response.data:
            logger.error(f"Project not found for update with id: {project_id}")
            raise HTTPException(status_code=404, detail="Project not found")
        return response.data[0]
    except Exception as e:
        logger.error(f"Error updating project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@project_router.delete("/{project_id}")
async def delete_project(project_id: UUID4):
    try:
        supabase = await supabase_service.client
        response = await supabase.table("projects").delete().eq("id", str(project_id)).execute()
        
        if not response.data:
            logger.error(f"Project not found for deletion with id: {project_id}")
            raise HTTPException(status_code=404, detail="Project not found")
        return {"message": "Project deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
