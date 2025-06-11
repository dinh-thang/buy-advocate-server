from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.services.supabase_service import supabase_service
from src.config import logger, settings
from datetime import datetime
from starlette.datastructures import MutableHeaders

security = HTTPBearer()

# Cache for storing validated tokens
token_cache = {}
TOKEN_CACHE_TTL = 300  # 5 minutes in seconds

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Validate the JWT token from the Authorization header and return the user ID
    """
    try:
        token = credentials.credentials
        
        # Check cache first
        cached_user = token_cache.get(token)
        if cached_user:
            if datetime.now().timestamp() - cached_user['timestamp'] < TOKEN_CACHE_TTL:
                return cached_user['user_id']
            else:
                del token_cache[token]

        # Validate with Supabase
        user = await supabase_service.get_user(token)
        user_id = user.user.id
        
        # Cache the result
        token_cache[token] = {
            'user_id': user_id,
            'timestamp': datetime.now().timestamp()
        }
        
        return user_id
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

# Clean up expired tokens periodically
def cleanup_expired_tokens():
    current_time = datetime.now().timestamp()
    expired_tokens = [
        token for token, data in token_cache.items()
        if current_time - data['timestamp'] > TOKEN_CACHE_TTL
    ]
    for token in expired_tokens:
        del token_cache[token]

async def inject_api_key(request: Request):
    """Inject the internal API key for specific endpoints"""
    logger.info(f"Checking path: {request.url.path}")
    if request.url.path.endswith('/sign-up'):
        logger.info("Sign-up endpoint detected, injecting API key")
        # Create mutable headers and add the API key
        mutable_headers = MutableHeaders(request.headers)
        mutable_headers["x-internal-api-key"] = settings.X_API_KEY
        request._headers = mutable_headers
        logger.info(f"API key injected: {settings.X_API_KEY[:10]}...")
    else:
        logger.info("Not a sign-up endpoint, skipping API key injection")
