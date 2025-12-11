"""Time series data models for Oil Well Time Series API."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class TimeSeriesDataPoint(BaseModel):
    """Represents a single timestamped measurement from a well sensor.

    Attributes:
        timestamp: ISO 8601 UTC timestamp
        well_id: Reference to Well
        metric_name: Reference to Metric
        value: Measured value
        unit: Unit of measurement (denormalized for convenience)
        quality_flag: Data quality indicator (good, suspect, or bad)
    """

    timestamp: datetime = Field(..., description="ISO 8601 UTC timestamp")
    well_id: str = Field(..., pattern=r"^WELL-\d{3}$")
    metric_name: str
    value: float
    unit: str
    quality_flag: Literal["good", "suspect", "bad"] = "good"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "timestamp": "2024-01-01T00:00:00Z",
                    "well_id": "WELL-001",
                    "metric_name": "oil_production_rate",
                    "value": 245.7,
                    "unit": "bbl/day",
                    "quality_flag": "good",
                }
            ]
        }
    }
