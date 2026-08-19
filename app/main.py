from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware

from app.core.security.security_headers import security_headers_middleware
from app.core.settings import settings
from app.core.logger import logger
from app.api.v1.router import api_v1_router

from app.core.db.postgres.engine import engine
from app.core.db.redis.client import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await redis_client.ping()

    logger.info("FintexAI API startup.")

    yield

    # Shutdown
    await redis_client.aclose()
    await engine.dispose()

    logger.info("FintexAI API shutdown.")

app = FastAPI(
    title=settings.app.PROJECT_NAME,
    description=settings.app.DESCRIPTION,
    version=settings.app.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=list(
        settings.app.ALLOWED_HOSTS,
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.ALLOWED_ORIGINS,                
    allow_credentials=True, 
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-CSRF-Token",
    ],           
)

app.middleware("http")(
    security_headers_middleware,
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