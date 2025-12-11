"""Aggregated time series data models."""

from datetime import date as date_type
from enum import Enum

from pydantic import BaseModel, Field


class AggregationType(str, Enum):
    """Enumeration of supported aggregation types."""

    DAILY_AVERAGE = "daily_average"
    DAILY_MAX = "daily_max"
    DAILY_MIN = "daily_min"
    DAILY_SUM = "daily_sum"
    MONTHLY_AVERAGE = "monthly_average"


class AggregatedDataPoint(BaseModel):
    """A single aggregated data point for a time period.

    Represents a computed summary (average, max, min, sum) for a specific
    time period (day or month) for a well and metric combination.
    """

    date: date_type = Field(
        ...,
        description="Date for the time period (YYYY-MM-DD)",
    )
    time_period: str = Field(
        ...,
        description=(
            "Human-readable time period label (e.g., '2024-01-01' for daily, '2024-01' for monthly)"
        ),
    )
    well_id: str = Field(
        ...,
        pattern=r"^WELL-\d{3}$",
        description="Well identifier",
    )
    metric_name: str = Field(..., description="Metric identifier")
    aggregated_value: float = Field(
        ...,
        description="Computed aggregated value",
    )
    aggregation_type: AggregationType = Field(
        ...,
        description="Type of aggregation performed",
    )
    unit: str = Field(..., description="Unit of measurement")
    data_point_count: int = Field(
        ...,
        ge=0,
        description="Number of raw data points used in aggregation",
    )
    min_value: float = Field(..., description="Minimum value in the period")
    max_value: float = Field(..., description="Maximum value in the period")
    data_completeness: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Percentage of expected data points present",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "date": "2024-01-01",
                    "time_period": "2024-01-01",
                    "well_id": "WELL-001",
                    "metric_name": "oil_production_rate",
                    "aggregated_value": 248.3,
                    "aggregation_type": "daily_average",
                    "unit": "bbl/day",
                    "data_point_count": 1440,
                    "min_value": 230.1,
                    "max_value": 265.8,
                    "data_completeness": 100.0,
                }
            ]
        }
    }
