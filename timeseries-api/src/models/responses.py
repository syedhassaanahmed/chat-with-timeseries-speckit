"""Response models for API endpoints."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from src.models.metric import Metric
from src.models.timeseries import TimeSeriesDataPoint
from src.models.well import Well


class WellListResponse(BaseModel):
    """Response model for listing all wells.

    Attributes:
        wells: List of well metadata
        total_count: Total number of wells
        metadata: Additional context (e.g., generated_at timestamp)
    """

    wells: list[Well]
    total_count: int = Field(..., description="Total number of wells")
    metadata: dict = Field(
        default_factory=lambda: {"generated_at": datetime.now(UTC).isoformat()},
        description="Additional context",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "wells": [
                        {
                            "well_id": "WELL-001",
                            "well_name": "North Field Alpha 1",
                            "latitude": 29.5,
                            "longitude": -95.2,
                            "operator": "Demo Energy Corp",
                            "field_name": "North Field",
                            "well_type": "producer",
                            "spud_date": "2022-01-15",
                            "data_start_date": "2023-01-01",
                            "data_end_date": "2024-12-31",
                        }
                    ],
                    "total_count": 5,
                    "metadata": {"generated_at": "2024-12-09T10:30:00Z"},
                }
            ]
        }
    }


class MetricListResponse(BaseModel):
    """Response model for listing all metrics.

    Attributes:
        metrics: List of metric definitions
        total_count: Total number of metrics
        metadata: Additional context
    """

    metrics: list[Metric]
    total_count: int
    metadata: dict = Field(
        default_factory=lambda: {"generated_at": datetime.now(UTC).isoformat()},
        description="Additional context",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "metrics": [
                        {
                            "metric_name": "oil_production_rate",
                            "display_name": "Oil Production Rate",
                            "description": "Daily oil production volume from the well",
                            "unit_of_measurement": "bbl/day",
                            "data_type": "numeric",
                            "typical_min": 0,
                            "typical_max": 500,
                        }
                    ],
                    "total_count": 8,
                    "metadata": {"generated_at": "2024-12-09T10:30:00Z"},
                }
            ]
        }
    }


class RawDataResponse(BaseModel):
    """Response model for raw time-series data queries.

    Attributes:
        data: List of timestamped data points
        metadata: Query context and statistics (well_id, metric_name,
                  start/end timestamps, total_points, data_completeness)
    """

    data: list[TimeSeriesDataPoint]
    metadata: dict = Field(..., description="Query context and statistics")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "data": [
                        {
                            "timestamp": "2024-01-01T00:00:00Z",
                            "well_id": "WELL-001",
                            "metric_name": "oil_production_rate",
                            "value": 245.7,
                            "unit": "bbl/day",
                            "quality_flag": "good",
                        }
                    ],
                    "metadata": {
                        "well_id": "WELL-001",
                        "metric_name": "oil_production_rate",
                        "start_timestamp": "2024-01-01T00:00:00Z",
                        "end_timestamp": "2024-01-31T23:59:59Z",
                        "total_points": 44640,
                        "data_completeness": 99.8,
                    },
                }
            ]
        }
    }
