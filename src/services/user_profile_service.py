from uuid import UUID
from src.schemas.user_profile import UserProfileCreate, UserProfileUpdate, UserProfileResponse
from src.services.supabase_service import supabase_service
from src.config import logger

class UserProfileService:
    def _convert_uuids_to_strings(self, data: dict) -> dict:
        """Convert UUID objects to strings in a dictionary"""
        converted_data = {}
        for key, value in data.items():
            if isinstance(value, UUID):
                converted_data[key] = str(value)
            else:
                converted_data[key] = value
        return converted_data

    async def create_profile(self, profile: UserProfileCreate) -> UserProfileResponse:
        """Create a new user profile"""
        client = await supabase_service.client
        try:
            # Check if profile already exists
            existing_result = await client.table('user_profile').select("id").eq('user_id', str(profile.user_id)).execute()
            if existing_result.data:
                logger.warning(f"Profile already exists for user_id: {profile.user_id}")
                return UserProfileResponse(**existing_result.data[0])
            
            # Convert UUIDs to strings for Supabase
            profile_data = self._convert_uuids_to_strings(profile.model_dump())
            
            result = await client.table('user_profile').insert(profile_data).execute()
            return UserProfileResponse(**result.data[0])
        except Exception as e:
            logger.error(f"Error creating user profile: {str(e)}")
            raise

    async def get_profile_by_user_id(self, user_id: UUID) -> UserProfileResponse:
        """Get a user profile by user_id"""
        client = await supabase_service.client
        try:
            # Get user profile data
            result = await client.table('user_profile').select("*").eq('user_id', str(user_id)).execute()
            
            if not result.data:
                return None
            
            profile_data = result.data[0]
            
            # Get auth user data using admin client
            try:
                admin_client = await supabase_service.get_service_role_client()
                auth_result = await admin_client.auth.admin.get_user_by_id(str(user_id))
                
                if auth_result.user:
                    profile_data['email'] = auth_result.user.email
                    # Check for image_url in user_metadata (common with OAuth providers)
                    user_metadata = auth_result.user.user_metadata or {}
                    profile_data['image_url'] = user_metadata.get('avatar_url') or user_metadata.get('picture')
            except Exception as auth_e:
                logger.warning(f"Could not fetch auth user data for user {user_id}: {str(auth_e)}")
                profile_data['email'] = None
                profile_data['image_url'] = None
            
            return UserProfileResponse(**profile_data)
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            raise

    async def get_profile(self, profile_id: UUID) -> UserProfileResponse:
        """Get a user profile by profile id"""
        client = await supabase_service.client
        try:
            # Get user profile data
            result = await client.table('user_profile').select("*").eq('id', str(profile_id)).execute()
            
            if not result.data:
                return None
            
            profile_data = result.data[0]
            user_id = profile_data['user_id']
            
            # Get auth user data using admin client
            try:
                admin_client = await supabase_service.get_service_role_client()
                auth_result = await admin_client.auth.admin.get_user_by_id(str(user_id))
                
                if auth_result.user:
                    profile_data['email'] = auth_result.user.email
                    # Check for image_url in user_metadata (common with OAuth providers)
                    user_metadata = auth_result.user.user_metadata or {}
                    profile_data['image_url'] = user_metadata.get('avatar_url') or user_metadata.get('picture')
            except Exception as auth_e:
                logger.warning(f"Could not fetch auth user data for user {user_id}: {str(auth_e)}")
                profile_data['email'] = None
                profile_data['image_url'] = None
            
            return UserProfileResponse(**profile_data)
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            raise

    async def update_profile(self, profile_id: UUID, profile: UserProfileUpdate) -> UserProfileResponse:
        """Update a user profile"""
        client = await supabase_service.client
        try:
            # Convert UUIDs to strings for Supabase
            profile_data = self._convert_uuids_to_strings(profile.model_dump(exclude_unset=True))
            
            result = await client.table('user_profile').update(profile_data).eq('id', str(profile_id)).execute()
            return UserProfileResponse(**result.data[0])
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            raise

    async def delete_profile(self, profile_id: UUID) -> bool:
        """Delete a user profile"""
        client = await supabase_service.client
        try:
            await client.table('user_profile').delete().eq('id', str(profile_id)).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting user profile: {str(e)}")
            raise

# Create a singleton instance
user_profile_service = UserProfileService() 