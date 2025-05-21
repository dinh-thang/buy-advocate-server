import uvicorn

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.routers.project_router import project_router
from src.routers.admin_router import admin_router


app = FastAPI()
api_router = APIRouter()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

app.include_router(api_router, prefix="/api")
app.include_router(project_router, prefix="/api")
app.include_router(admin_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)




