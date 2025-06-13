import uvicorn

from dotenv import load_dotenv

from typing import Any

from fastapi import APIRouter as FastAPIRouter
from fastapi import APIRouter, FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.middleware.auth import get_current_user

from src.routers.poi_detail_router import poi_detail_router
from src.routers.filter_router import filter_router
from src.routers.project_router import project_router
from src.routers.admin_router import admin_router
from src.routers.property_router import property_router
from src.routers.site_type_router import site_type_router
from src.routers.market_status_router import market_status_router
from src.routers.poi_router import poi_router
from src.routers.user_profile_router import user_profile_router
from src.routers.agent_router import agent_router


app = FastAPI(
    swagger_ui_parameters={},
    trust_env=True,
    redirect_slashes=False
)

api_router = APIRouter()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://172.29.144.1:3000",
    "https://buy-advocate-mauve.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

@api_router.get("/ping")
async def ping():
    return JSONResponse(
        content={
            "message": "pong",
            "status": "success",
        },
        status_code=200
    )

# Protected routes
app.include_router(project_router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(filter_router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(property_router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(site_type_router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(market_status_router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(poi_router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(poi_detail_router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(agent_router, prefix="/api", dependencies=[Depends(get_current_user)])

# User profile routes (mixed auth requirements)
app.include_router(user_profile_router, prefix="/api")

# Admin routes (you might want to add additional admin role checks)
app.include_router(admin_router, prefix="/api", dependencies=[Depends(get_current_user)])

# Public routes
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)




