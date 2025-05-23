from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from functools import wraps
from src.services.supabase_service import supabase_service

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Validate the JWT token from the Authorization header and return the user ID
    """
    try:
        # Get the token from the Authorization header
        token = credentials.credentials
        
        # Verify the token with Supabase
        user = await supabase_service.get_user(token)
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials"
            )
            
        return user.user.id
        
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )
