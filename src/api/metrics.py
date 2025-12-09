"""Metrics endpoints for Oil Well Time Series API."""

import sqlite3
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from src.db.database import get_db_connection_for_fastapi
from src.models.responses import MetricListResponse
from src.services.query_service import QueryService

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("", response_model=MetricListResponse)
def list_metrics(
    db: sqlite3.Connection = Depends(get_db_connection_for_fastapi),
) -> MetricListResponse:
    """List all available metrics.

    Returns metadata for all metric types (oil production, pressure, etc.).

    Args:
        db: Database connection (injected)

    Returns:
        MetricListResponse with metrics array, total count, and metadata
    """
    query_service = QueryService()

    try:
        metrics = query_service.get_all_metrics(db)
        return MetricListResponse(
            metrics=metrics,
            total_count=len(metrics),
            metadata={"generated_at": datetime.utcnow().isoformat() + "Z"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
