"""Metric model for Oil Well Time Series API."""

from typing import Literal

from pydantic import BaseModel, Field


class Metric(BaseModel):
    """Represents a measurable oilfield KPI or operational parameter.

    Attributes:
        metric_name: Unique identifier in snake_case (e.g., "oil_production_rate")
        display_name: User-friendly label (e.g., "Oil Production Rate")
        description: Explanation of what the metric measures
        unit_of_measurement: Unit abbreviation (e.g., "bbl/day")
        data_type: Type of data (numeric, boolean, or categorical)
        typical_min: Typical minimum value for context (optional)
        typical_max: Typical maximum value for context (optional)
    """

    metric_name: str = Field(..., pattern=r"^[a-z_]+$", description="Snake_case identifier")
    display_name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    unit_of_measurement: str = Field(..., min_length=1, max_length=20)
    data_type: Literal["numeric", "boolean", "categorical"]
    typical_min: float | None = None
    typical_max: float | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "metric_name": "oil_production_rate",
                    "display_name": "Oil Production Rate",
                    "description": "Daily oil production volume from the well",
                    "unit_of_measurement": "bbl/day",
                    "data_type": "numeric",
                    "typical_min": 0,
                    "typical_max": 500,
                }
            ]
        }
    }
