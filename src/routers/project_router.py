from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from pydantic import UUID4
from supabase import Client
from uuid import UUID

from src.services.supabase_service import get_supabase_client
from src.schemas.project import Project, ProjectCreate, ProjectBase, ProjectUpdate
from src.config import logger


project_router = APIRouter(
    prefix="/projects",
    tags=["projects"]
)


# get a project by id, this should be t
@project_router.get("/{project_id}")
async def get_project(
    project_id: UUID4,
    supabase: Client = Depends(get_supabase_client)
):
    response = await supabase.table("projects").select(
        """
        *,
        site_types(
            *,
            site_type_market_status_filters(
                *,
                filters(*)
            )
        ),
        market_status(*),
        user_filters(*)
        """
    ).eq("id", project_id).execute()

    if not response.data:
        logger.error(f"Project not found with id: {project_id}")
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_data = response.data[0]
    
    # Filter the site_type_market_status_filters to only include those matching the project's market_status_id
    if project_data.get("site_types", {}).get("site_type_market_status_filters"):
        project_data["site_types"]["site_type_market_status_filters"] = [
            filter_data for filter_data in project_data["site_types"]["site_type_market_status_filters"]
            if filter_data.get("market_status_id") == str(project_data["market_status_id"])
        ]
    
    return project_data


# get all projects of a user
@project_router.get("/")
async def get_all_projects(
    user_id: UUID4 = Query(None, description="Filter by user ID"),
    supabase: Client = Depends(get_supabase_client)
):
    try:
        query = supabase.table("projects").select("*")
        
        if user_id:
            query = query.eq("user_id", str(user_id))
        
        response = await query.execute()

        return response.data
    except Exception as e:
        logger.error(f"Error fetching projects: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@project_router.post("/")
async def create_project(
    project: ProjectCreate,
    supabase: Client = Depends(get_supabase_client)
):
    try:
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
        return response.data[0]
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@project_router.patch("/{project_id}")
async def update_project(
    project_id: UUID4,
    project: ProjectUpdate,
    supabase: Client = Depends(get_supabase_client)
):
    try:
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
async def delete_project(
    project_id: UUID4,
    supabase: Client = Depends(get_supabase_client)
):
    try:
        response = await supabase.table("projects").delete().eq("id", str(project_id)).execute()
        
        if not response.data:
            logger.error(f"Project not found for deletion with id: {project_id}")
            raise HTTPException(status_code=404, detail="Project not found")
        return {"message": "Project deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
