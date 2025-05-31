from supabase import acreate_client, Client
from src.config import settings, logger
from functools import lru_cache


class SupabaseService:
    _instance = None
    _client: Client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseService, cls).__new__(cls)
        return cls._instance

    async def initialize(self):
        """Initialize the Supabase client"""
        if self._client is None:
            if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
            
            logger.info(f"Initializing Supabase client with URL: {settings.SUPABASE_URL}")
            try:
                self._client = await acreate_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {str(e)}")
                raise

    @property
    async def client(self) -> Client:
        """Get the Supabase client instance"""
        if self._client is None:
            await self.initialize()
        return self._client

    async def get_user(self, token: str):
        """Get user information from token"""
        client = await self.client
        return await client.auth.get_user(token)


# Create a singleton instance
supabase_service = SupabaseService()
