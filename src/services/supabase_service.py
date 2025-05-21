from supabase import acreate_client, Client
from src.config import settings


async def get_supabase_client() -> Client:    
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    
    return await acreate_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
