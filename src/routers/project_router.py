from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List
from pydantic import UUID4
from uuid import UUID

from src.services.supabase_service import supabase_service
from src.services.project_service import project_service
from src.schemas.project import ProjectCreate, ProjectUpdate
from src.config import logger
from src.middleware.auth import get_current_user
 
project_router = APIRouter(
    prefix="/projects",
    tags=["projects"]
)


# THIS RETURNS BOTH THE SAVED FILTER CONFIG AND THE DEFAULT CONFIGS
@project_router.get("/{project_id}")
async def get_project(project_id: UUID4):
    try:
        supabase = await supabase_service.client
        response = await supabase.table("projects").select(
            """
            id,
            created_at,
            title,
            site_type_id,
            market_status_id,
            market_status(*),
            site_types(*),
            user_filters(*)
            """
        ).eq("id", project_id).execute()

        if not response.data:
            logger.error(f"Project not found with id: {project_id}")
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = response.data[0]
        
        # Fetch default filters for this project's site type and market status
        default_filters_response = await supabase.table("site_type_market_status_filters").select(
            """
            *,
            filters(
                id,
                filter_type,
                filter_data,
                db_column_name,
                order,
                display_name,
                is_open
            )
            """
        ).eq("site_type_id", str(project["site_type_id"])).eq("market_status_id", str(project["market_status_id"])).execute()
        
        # Extract the default filters
        default_filters = [item["filters"] for item in default_filters_response.data] if default_filters_response.data else []
        
        # Add default filters to the project data
        project["default_filters"] = default_filters
        
        return project
    except Exception as e:
        logger.error(f"Error fetching project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@project_router.get("/")
async def get_all_projects(
    user_id: str = Depends(get_current_user)
):
    try:
        supabase = await supabase_service.client
        query = supabase.table("projects").select(
        """
        id,
        title,
        is_active
        """
        ).eq("user_id", user_id)
        response = await query.execute()

        return response.data
    except Exception as e:
        logger.error(f"Error fetching projects: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@project_router.post("/")
async def create_project(project: ProjectCreate, user_id: str = Depends(get_current_user)):
    try:
        supabase = await supabase_service.client
        # Convert the project data to a dictionary and ensure UUIDs are strings
        project_data = project.model_dump(exclude={"id", "created_at"})
        
        # Add user_id from authentication
        project_data["user_id"] = user_id
        
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
                    "db_column_name": filter_data["db_column_name"],
                    "order": filter_data["order"],
                    "display_name": filter_data["display_name"],
                    "is_open": filter_data["is_open"]
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
                db_column_name,
                display_name,
                order,
                is_open
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
        
        # First, get the current project data to check if site_type_id or market_status_id changed
        current_project_response = await supabase.table("projects").select(
            "id, site_type_id, market_status_id"
        ).eq("id", str(project_id)).execute()
        
        if not current_project_response.data:
            logger.error(f"Project not found for update with id: {project_id}")
            raise HTTPException(status_code=404, detail="Project not found")
        
        current_project = current_project_response.data[0]
        
        # Convert the project data to a dictionary and ensure UUIDs are strings
        project_data = project.model_dump(exclude_unset=True)
        
        if not project_data:
            raise HTTPException(status_code=400, detail="No valid fields to update")
            
        for key, value in project_data.items():
            if isinstance(value, UUID):
                project_data[key] = str(value)
        
        # Check if site_type_id or market_status_id is being changed
        site_type_changed = "site_type_id" in project_data and str(project_data["site_type_id"]) != str(current_project["site_type_id"])
        market_status_changed = "market_status_id" in project_data and str(project_data["market_status_id"]) != str(current_project["market_status_id"])
        
        # Update the project
        response = await supabase.table("projects").update(project_data).eq("id", str(project_id)).execute()
        
        if not response.data:
            logger.error(f"Project not found for update with id: {project_id}")
            raise HTTPException(status_code=404, detail="Project not found")
        
        updated_project = response.data[0]
        
        # If site_type_id or market_status_id changed, reset user filters to default
        if site_type_changed or market_status_changed:
            # Delete all existing user filters for this project
            await supabase.table("user_filters").delete().eq("project_id", str(project_id)).execute()
            
            # Get the new site_type_id and market_status_id (use updated values or current values)
            new_site_type_id = project_data.get("site_type_id", current_project["site_type_id"])
            new_market_status_id = project_data.get("market_status_id", current_project["market_status_id"])
            
            # Fetch the default filters for the new combination
            filters_response = await supabase.table("site_type_market_status_filters").select(
                """
                *,
                filters(*)
                """
            ).eq("site_type_id", str(new_site_type_id)).eq("market_status_id", str(new_market_status_id)).execute()
            
            if filters_response.data:
                # Create new user_filters entries based on default filters
                user_filters = []
                for filter_association in filters_response.data:
                    filter_data = filter_association["filters"]
                    user_filter = {
                        "project_id": str(project_id),
                        "filter_type": filter_data["filter_type"],
                        "filter_data": filter_data["filter_data"],
                        "display_name": filter_data["display_name"],
                        "db_column_name": filter_data["db_column_name"],
                        "order": filter_data["order"],
                        "is_open": filter_data["is_open"]
                    }
                    user_filters.append(user_filter)
                    
                if user_filters:
                    await supabase.table("user_filters").insert(user_filters).execute()
        
        return updated_project
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


@project_router.post("/post-signup/{user_id}")
async def handle_post_signup(user_id: str):
    """Handle post-signup actions for a new user"""
    try:
        # Create default project for the user
        project = await project_service.create_default_project(user_id)
        if not project:
            raise HTTPException(status_code=500, detail="Failed to create default project")
        
        return {"success": True, "project": project}
    except Exception as e:
        logger.error(f"Error in post-signup handling for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
