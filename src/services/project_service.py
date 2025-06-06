from uuid import UUID
from src.config import logger
from src.services.supabase_service import supabase_service

class ProjectService:
    _instance = None

    # Default IDs for new projects
    DEFAULT_SITE_TYPE_ID = UUID("91e77060-3db3-45e4-9248-3da050307495")
    DEFAULT_MARKET_STATUS_ID = UUID("1402b689-c389-499e-9039-79d4e0804117")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProjectService, cls).__new__(cls)
        return cls._instance

    async def create_default_project(self, user_id: str) -> dict:
        """Create a default project for a new user"""
        try:
            client = await supabase_service.get_service_role_client()
            
            # Create default project data
            project_data = {
                "title": "My First Project",
                "user_id": user_id,
                "site_type_id": str(self.DEFAULT_SITE_TYPE_ID),
                "market_status_id": str(self.DEFAULT_MARKET_STATUS_ID),
                "is_active": True
            }
            
            # Create the project
            response = await client.table("projects").insert(project_data).execute()
            
            if not response.data:
                logger.error(f"Failed to create default project for user: {user_id}")
                return None
            
            project_result = response.data[0]
            
            # Fetch default filters for this site type and market status combination
            filters_response = await client.table("site_type_market_status_filters").select(
                """
                *,
                filters(*)
                """
            ).eq("site_type_id", str(self.DEFAULT_SITE_TYPE_ID)).eq("market_status_id", str(self.DEFAULT_MARKET_STATUS_ID)).execute()
            
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
                        "is_open": filter_data["is_open"]
                    }
                    user_filters.append(user_filter)
                    
                if user_filters:
                    await client.table("user_filters").insert(user_filters).execute()
            
            logger.info(f"Successfully created default project for user: {user_id}")
            return project_result
            
        except Exception as e:
            logger.error(f"Error creating default project for user {user_id}: {str(e)}")
            return None

# Create a singleton instance
project_service = ProjectService()
