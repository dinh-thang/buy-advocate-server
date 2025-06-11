from fastapi import APIRouter, Depends, HTTPException, Security, Request
from uuid import UUID
from fastapi.security import APIKeyHeader
from typing import Optional

from src.middleware.auth import get_current_user
from src.schemas.user_profile import UserProfileCreate, UserProfileUpdate, UserProfileResponse
from src.services.user_profile_service import user_profile_service
from src.config import settings

user_profile_router = APIRouter(
    prefix="/user-profiles",
    tags=["user-profiles"]
)

# Create a header requirement for internal API calls
INTERNAL_API_KEY = APIKeyHeader(name="X-Internal-API-Key", auto_error=False)

@user_profile_router.post("/sign-up", response_model=UserProfileResponse)
async def create_profile_on_signup(
    profile: UserProfileCreate,
    request: Request,
    api_key: Optional[str] = Security(INTERNAL_API_KEY)
) -> UserProfileResponse:
    """Create a new user profile during sign-up process"""
    # Check if API key was provided or inject it for sign-up endpoint
    if not api_key:
        # For the sign-up endpoint, inject the API key internally
        api_key = settings.X_API_KEY
    
    if api_key != settings.X_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return await user_profile_service.create_profile(profile)

@user_profile_router.post("", response_model=UserProfileResponse, dependencies=[Depends(get_current_user)])
async def create_profile(
    profile: UserProfileCreate,
    current_user_id: str = Depends(get_current_user)
) -> UserProfileResponse:
    """Create a new user profile"""
    # Ensure the user can only create a profile for themselves
    if str(profile.user_id) != current_user_id:
        raise HTTPException(status_code=403, detail="Cannot create profile for another user")
    return await user_profile_service.create_profile(profile)

@user_profile_router.get("/me", response_model=UserProfileResponse, dependencies=[Depends(get_current_user)])
async def get_my_profile(
    current_user_id: str = Depends(get_current_user)
) -> UserProfileResponse:
    """Get the current user's profile"""
    profile = await user_profile_service.get_profile_by_user_id(UUID(current_user_id))
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@user_profile_router.get("/{profile_id}", response_model=UserProfileResponse, dependencies=[Depends(get_current_user)])
async def get_profile(
    profile_id: UUID,
    current_user_id: str = Depends(get_current_user)
) -> UserProfileResponse:
    """Get a user profile by ID"""
    profile = await user_profile_service.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@user_profile_router.put("/{profile_id}", response_model=UserProfileResponse, dependencies=[Depends(get_current_user)])
async def update_profile(
    profile_id: UUID,
    profile_update: UserProfileUpdate,
    current_user_id: str = Depends(get_current_user)
) -> UserProfileResponse:
    """Update a user profile"""
    # Get the existing profile
    existing_profile = await user_profile_service.get_profile(profile_id)
    if not existing_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Ensure the user can only update their own profile
    if str(existing_profile.user_id) != current_user_id:
        raise HTTPException(status_code=403, detail="Cannot update another user's profile")
    
    return await user_profile_service.update_profile(profile_id, profile_update)

# @user_profile_router.delete("/{profile_id}")
# async def delete_profile(
#     profile_id: UUID,
#     current_user_id: str = Depends(get_current_user)
# ) -> dict:
#     """Delete a user profile"""
#     # Get the existing profile
#     existing_profile = await user_profile_service.get_profile(profile_id)
#     if not existing_profile:
#         raise HTTPException(status_code=404, detail="Profile not found")
    
#     # Ensure the user can only delete their own profile
#     if str(existing_profile.user_id) != current_user_id:
#         raise HTTPException(status_code=403, detail="Cannot delete another user's profile")
    
#     await user_profile_service.delete_profile(profile_id)
#     return {"message": "Profile deleted successfully"} 