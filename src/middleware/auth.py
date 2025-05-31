from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from functools import wraps
from src.services.supabase_service import supabase_service
from src.config import logger

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Validate the JWT token from the Authorization header and return the user ID
    """
    try:
        # Get the token from the Authorization header
        token = credentials.credentials
        logger.info("Received token for authentication")
        
        # Verify the token with Supabase
        user = await supabase_service.get_user(token)
        logger.info(f"User authenticated successfully: {user.user.id}")
            
        return user.user.id
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )
