from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import settings
from app.core.logger import logger
from app.api.v1.router import api_v1_router


app = FastAPI(
    title=settings.app.PROJECT_NAME,
    description=settings.app.DESCRIPTION,
    version=settings.app.VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],                
    allow_credentials=True, 
    allow_methods=["*"],             
    allow_headers=["*"],            
)


app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/")
async def root():
    logger.info("FintexAI API root endpoint accessed.")
    return {
        "project_name": settings.app.PROJECT_NAME,
        "version": settings.app.VERSION,
        "status": "healthy"
    }