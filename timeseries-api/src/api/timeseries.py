"""Time-series data endpoints for Oil Well Time Series API."""

import sqlite3
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from src.db.database import get_db_connection_for_fastapi
from src.models.responses import AggregatedDataResponse, RawDataResponse
from src.services.query_service import QueryService

router = APIRouter(prefix="/wells/{well_id}/data", tags=["Time-Series Data"])


@router.get("/raw", response_model=RawDataResponse)
def get_raw_data(
    well_id: str,
    metric_name: str = Query(..., description="Metric identifier (e.g., oil_production_rate)"),
    start_timestamp: datetime = Query(..., description="Start timestamp (ISO 8601 UTC)"),
    end_timestamp: datetime = Query(..., description="End timestamp (ISO 8601 UTC)"),
    db: sqlite3.Connection = Depends(get_db_connection_for_fastapi),
) -> RawDataResponse:
    """Query raw time-series data for a specific well and metric.

    Returns minute-level timestamped data points for the specified time range.

    Args:
        well_id: Well identifier (e.g., "WELL-001")
        metric_name: Metric identifier (e.g., "oil_production_rate")
        start_timestamp: Start of time range (ISO 8601 UTC format)
        end_timestamp: End of time range (ISO 8601 UTC format)
        db: Database connection (injected)

    Returns:
        RawDataResponse with data array and metadata

    Raises:
        HTTPException: 400 for invalid parameters, 404 for not found, 500 for server errors
    """
    query_service = QueryService()

    try:
        result = query_service.get_raw_timeseries(
            db, well_id, metric_name, start_timestamp, end_timestamp
        )
        return RawDataResponse(data=result["data"], metadata=result["metadata"])
    except ValueError as e:
        # Handle validation errors (well not found, metric not found, invalid range)
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg) from e
        else:
            raise HTTPException(status_code=400, detail=error_msg) from e
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


@router.get("/aggregated", response_model=AggregatedDataResponse)
def get_aggregated_data(
    well_id: str,
    metric_name: str = Query(..., description="Metric identifier (e.g., oil_production_rate)"),
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    aggregation_type: str = Query(
        ...,
        description="Aggregation type",
        pattern="^(daily_average|daily_max|daily_min|daily_sum|monthly_average)$",
    ),
    db: sqlite3.Connection = Depends(get_db_connection_for_fastapi),
) -> AggregatedDataResponse:
    """Query aggregated time-series data for a specific well and metric.

    Returns computed summaries (averages, max, min, sum) aggregated by day or month.

    Args:
        well_id: Well identifier (e.g., "WELL-001")
        metric_name: Metric identifier (e.g., "oil_production_rate")
        start_date: Start date (YYYY-MM-DD format)
        end_date: End date (YYYY-MM-DD format)
        aggregation_type: Type of aggregation (daily_average, daily_max, daily_min,
                          daily_sum, monthly_average)
        db: Database connection (injected)

    Returns:
        AggregatedDataResponse with aggregated data array and metadata

    Raises:
        HTTPException: 400 for invalid parameters, 404 for not found, 500 for server errors
    """
    query_service = QueryService()

    try:
        result = query_service.get_aggregated_timeseries(
            db, well_id, metric_name, start_date, end_date, aggregation_type
        )
        return AggregatedDataResponse(data=result["data"], metadata=result["metadata"])
    except ValueError as e:
        # Handle validation errors (well not found, metric not found, invalid range/type)
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg) from e
        else:
            raise HTTPException(status_code=400, detail=error_msg) from e
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e
