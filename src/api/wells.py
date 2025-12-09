"""Wells endpoints for Oil Well Time Series API."""

import sqlite3
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from src.db.database import get_db_connection_for_fastapi
from src.models.responses import WellListResponse
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
            metadata={"generated_at": datetime.utcnow().isoformat() + "Z"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
