"""Well model for Oil Well Time Series API."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class Well(BaseModel):
    """Represents an individual oil well with metadata and operational characteristics.

    Attributes:
        well_id: Unique identifier in format "WELL-XXX"
        well_name: Human-readable well name
        latitude: Geographic latitude (-90 to 90)
        longitude: Geographic longitude (-180 to 180)
        operator: Operating company name
        field_name: Field where well is located
        well_type: Type of well (producer, injector, or observation)
        spud_date: Date when drilling started
        data_start_date: First date with available time-series data
        data_end_date: Last date with available time-series data
    """

    well_id: str = Field(..., pattern=r"^WELL-\d{3}$", description="Unique well identifier")
    well_name: str = Field(..., min_length=1, max_length=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    operator: str = Field(..., min_length=1, max_length=100)
    field_name: str = Field(..., min_length=1, max_length=100)
    well_type: Literal["producer", "injector", "observation"]
    spud_date: date
    data_start_date: date
    data_end_date: date

    model_config = {
        "json_schema_extra": {
            "examples": [
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
            ]
        }
    }
