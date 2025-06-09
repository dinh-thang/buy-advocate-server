from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from functools import wraps, lru_cache
from src.services.supabase_service import supabase_service
from src.config import logger
from datetime import datetime, timedelta

security = HTTPBearer()

# Cache for storing validated tokens
token_cache = {}
TOKEN_CACHE_TTL = 300  # 5 minutes in seconds

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Validate the JWT token from the Authorization header and return the user ID
    with caching to prevent redundant validations
    """
    try:
        token = credentials.credentials
        
        # Check cache first
        if token in token_cache:
            cached_data = token_cache[token]
            if datetime.now().timestamp() - cached_data['timestamp'] < TOKEN_CACHE_TTL:
                logger.debug("Using cached authentication")
                return cached_data['user_id']
            else:
                # Remove expired cache entry
                del token_cache[token]
        
        logger.info("Received token for authentication")
        
        # Verify the token with Supabase
        user = await supabase_service.get_user(token)
        user_id = user.user.id
        logger.info(f"User authenticated successfully: {user_id}")
        
        # Cache the successful validation
        token_cache[token] = {
            'user_id': user_id,
            'timestamp': datetime.now().timestamp()
        }
            
        return user_id
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

# Cleanup function for expired cache entries
def cleanup_token_cache():
    current_time = datetime.now().timestamp()
    expired_tokens = [
        token for token, data in token_cache.items()
        if current_time - data['timestamp'] >= TOKEN_CACHE_TTL
    ]
    for token in expired_tokens:
        del token_cache[token]
