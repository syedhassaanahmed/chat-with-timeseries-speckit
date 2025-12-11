"""Wells endpoints for Oil Well Time Series API."""

import sqlite3
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException

from src.db.database import get_db_connection_for_fastapi
from src.models.responses import MetricListResponse, WellListResponse
from src.models.well import Well
from src.services.query_service import QueryService

router = APIRouter(prefix="/wells", tags=["Wells"])


@router.get("", response_model=WellListResponse)
def list_wells(
    db: sqlite3.Connection = Depends(get_db_connection_for_fastapi),
) -> WellListResponse:
    """List all available wells.

    Returns metadata for all sample wells in the system.

    Args:
        db: Database connection (injected)

    Returns:
        WellListResponse with wells array, total count, and metadata
    """
    query_service = QueryService()

    try:
        wells = query_service.get_all_wells(db)
        return WellListResponse(
            wells=wells,
            total_count=len(wells),
            metadata={"generated_at": datetime.now(UTC).isoformat()},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


@router.get("/{well_id}", response_model=Well)
def get_well(
    well_id: str,
    db: sqlite3.Connection = Depends(get_db_connection_for_fastapi),
) -> Well:
    """Get details for a specific well.

    Args:
        well_id: Well identifier (e.g., "WELL-001")
        db: Database connection (injected)

    Returns:
        Well object with metadata

    Raises:
        HTTPException: 404 if well not found, 500 for server errors
    """
    query_service = QueryService()

    try:
        well = query_service.get_well_by_id(db, well_id)
        if not well:
            raise HTTPException(status_code=404, detail=f"Well not found: {well_id}")
        return well
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


@router.get("/{well_id}/metrics", response_model=MetricListResponse)
def get_well_metrics(
    well_id: str,
    db: sqlite3.Connection = Depends(get_db_connection_for_fastapi),
) -> MetricListResponse:
    """Get all metrics available for a specific well.

    Returns only metrics that have data for the specified well.

    Args:
        well_id: Well identifier (e.g., "WELL-001")
        db: Database connection (injected)

    Returns:
        MetricListResponse with metrics array, total count, and metadata

    Raises:
        HTTPException: 404 if well not found, 500 for server errors
    """
    query_service = QueryService()

    try:
        # First verify well exists
        well = query_service.get_well_by_id(db, well_id)
        if not well:
            raise HTTPException(status_code=404, detail=f"Well not found: {well_id}")

        # Get metrics for this well
        metrics = query_service.get_metrics_for_well(db, well_id)
        return MetricListResponse(
            metrics=metrics,
            total_count=len(metrics),
            metadata={"generated_at": datetime.now(UTC).isoformat()},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e
