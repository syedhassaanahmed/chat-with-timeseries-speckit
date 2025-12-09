"""FastAPI application for Oil Well Time Series API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import metrics, timeseries, wells
from src.config import (
    API_DESCRIPTION,
    API_TITLE,
    API_VERSION,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_HEADERS,
    CORS_ALLOW_METHODS,
    CORS_ORIGINS,
)

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)

# Register routers
app.include_router(wells.router)
app.include_router(metrics.router)
app.include_router(timeseries.router)


@app.get("/", tags=["Root"])
def root() -> dict:
    """Root endpoint with API information.

    Returns:
        Dictionary with API metadata
    """
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
    }


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """Health check endpoint.

    Returns:
        Dictionary with health status
    """
    return {"status": "healthy"}
