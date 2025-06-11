import logging
import os
import sys
from dotenv import load_dotenv


# Load environment variables
ENV = os.getenv('ENV', 'local')
if ENV == 'production':
    load_dotenv('.env.production')
else:
    load_dotenv('.env')


logging.basicConfig(
        level=logging.INFO,  # Change to DEBUG for more detailed logs
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
logger = logging.getLogger('buy-advocate')


class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    PROPERTY_TABLE_NAME: str = os.getenv("PROPERTY_TABLE_NAME")
    X_API_KEY: str = os.getenv("X_API_KEY")
    
settings = Settings()
