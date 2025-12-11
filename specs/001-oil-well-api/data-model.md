# Data Model: Oil Well Time Series API

**Feature**: 001-oil-well-api  
**Date**: 2025-12-09  
**Purpose**: Define data structures, database schema, and Pydantic models

## Domain Models

### 1. Well

Represents an individual oil well with metadata and operational characteristics.

**Attributes**:
- `well_id` (str, PK): Unique identifier, format "WELL-XXX" (e.g., "WELL-001")
- `well_name` (str): Human-readable name (e.g., "North Field Alpha 1")
- `latitude` (float): Geographic latitude (-90 to 90)
- `longitude` (float): Geographic longitude (-180 to 180)
- `operator` (str): Operating company name
- `field_name` (str): Field where well is located
- `well_type` (str, enum): "producer", "injector", or "observation"
- `spud_date` (date): Date when drilling started
- `data_start_date` (date): First date with available time-series data
- `data_end_date` (date): Last date with available time-series data

**Example**:
```json
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
  "data_end_date": "2024-12-31"
}
```

---

### 2. Metric

Represents a measurable oilfield KPI or operational parameter.

**Attributes**:
- `metric_name` (str, PK): Unique identifier (e.g., "oil_production_rate")
- `display_name` (str): User-friendly label (e.g., "Oil Production Rate")
- `description` (str): Explanation of what the metric measures
- `unit_of_measurement` (str): Unit abbreviation (e.g., "bbl/day")
- `data_type` (str, enum): "numeric", "boolean", or "categorical"
- `typical_min` (float, optional): Typical minimum value for context
- `typical_max` (float, optional): Typical maximum value for context

**Example**:
```json
{
  "metric_name": "oil_production_rate",
  "display_name": "Oil Production Rate",
  "description": "Daily oil production volume from the well",
  "unit_of_measurement": "bbl/day",
  "data_type": "numeric",
  "typical_min": 0,
  "typical_max": 500
}
```

**Supported Metrics** (as per FR-008):
1. `oil_production_rate` (bbl/day)
2. `gas_production_rate` (mcf/day)
3. `wellhead_pressure` (psi)
4. `tubing_pressure` (psi)
5. `gas_injection_rate` (mcf/day)

---

### 3. TimeSeriesDataPoint

Represents a single timestamped measurement from a well sensor.

**Attributes**:
- `timestamp` (datetime): ISO 8601 UTC timestamp (e.g., "2024-01-01T00:00:00Z")
- `well_id` (str, FK): Reference to Well
- `metric_name` (str, FK): Reference to Metric
- `value` (float): Measured value
- `unit` (str): Unit of measurement (denormalized for convenience)
- `quality_flag` (str, enum): "good", "suspect", or "bad" (default: "good")

**Example**:
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "well_id": "WELL-001",
  "metric_name": "oil_production_rate",
  "value": 245.7,
  "unit": "bbl/day",
  "quality_flag": "good"
}
```

---

### 4. AggregatedDataPoint

Represents a computed summary over a time period (day or month).

**Attributes**:
- `date` (date): Date or start of time period
- `time_period` (str): Period label (e.g., "2024-01-01" for daily, "2024-01" for monthly)
- `well_id` (str, FK): Reference to Well
- `metric_name` (str, FK): Reference to Metric
- `aggregated_value` (float): Computed aggregate value (avg, sum, min, max)
- `aggregation_type` (str, enum): "daily_average", "daily_max", "daily_min", "daily_sum", "monthly_average"
- `unit` (str): Unit of measurement
- `data_point_count` (int): Number of raw data points used in calculation
- `min_value` (float): Minimum value in the period
- `max_value` (float): Maximum value in the period
- `data_completeness` (float): Percentage of expected data points present (0-100)

**Example**:
```json
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
  "data_completeness": 100.0
}
```

---

## Database Schema (SQLite)

### Table: `wells`

```sql
CREATE TABLE wells (
    well_id TEXT PRIMARY KEY,
    well_name TEXT NOT NULL,
    latitude REAL NOT NULL CHECK(latitude BETWEEN -90 AND 90),
    longitude REAL NOT NULL CHECK(longitude BETWEEN -180 AND 180),
    operator TEXT NOT NULL,
    field_name TEXT NOT NULL,
    well_type TEXT NOT NULL CHECK(well_type IN ('producer', 'injector', 'observation')),
    spud_date TEXT NOT NULL,  -- ISO 8601 date
    data_start_date TEXT NOT NULL,
    data_end_date TEXT NOT NULL
);
```

### Table: `metrics`

```sql
CREATE TABLE metrics (
    metric_name TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    description TEXT NOT NULL,
    unit_of_measurement TEXT NOT NULL,
    data_type TEXT NOT NULL CHECK(data_type IN ('numeric', 'boolean', 'categorical')),
    typical_min REAL,
    typical_max REAL
);
```

### Table: `timeseries_data`

```sql
CREATE TABLE timeseries_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,  -- ISO 8601 UTC
    well_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    value REAL NOT NULL,
    quality_flag TEXT DEFAULT 'good' CHECK(quality_flag IN ('good', 'suspect', 'bad')),
    FOREIGN KEY (well_id) REFERENCES wells(well_id),
    FOREIGN KEY (metric_name) REFERENCES metrics(metric_name)
);

-- Critical index for time-range queries
CREATE INDEX idx_well_metric_time ON timeseries_data(well_id, metric_name, timestamp);
CREATE INDEX idx_timestamp ON timeseries_data(timestamp);
```

**Query Performance**:
- Index on `(well_id, metric_name, timestamp)` enables fast range scans
- For 90-day query: ~130,000 rows (1 well × 1 metric × 90 days × 1440 min/day)
- Expected query time: <2s (as per SC-001)

---

## Pydantic Models (for API validation)

### `Well` Model

```python
from pydantic import BaseModel, Field
from datetime import date
from typing import Literal

class Well(BaseModel):
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

    model_config = {"json_schema_extra": {"example": {
        "well_id": "WELL-001",
        "well_name": "North Field Alpha 1",
        "latitude": 29.5,
        "longitude": -95.2,
        "operator": "Demo Energy Corp",
        "field_name": "North Field",
        "well_type": "producer",
        "spud_date": "2022-01-15",
        "data_start_date": "2023-01-01",
        "data_end_date": "2024-12-31"
    }}}
```

### `Metric` Model

```python
from typing import Optional

class Metric(BaseModel):
    metric_name: str = Field(..., pattern=r"^[a-z_]+$", description="Snake_case identifier")
    display_name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    unit_of_measurement: str = Field(..., min_length=1, max_length=20)
    data_type: Literal["numeric", "boolean", "categorical"]
    typical_min: Optional[float] = None
    typical_max: Optional[float] = None

    model_config = {"json_schema_extra": {"example": {
        "metric_name": "oil_production_rate",
        "display_name": "Oil Production Rate",
        "description": "Daily oil production volume from the well",
        "unit_of_measurement": "bbl/day",
        "data_type": "numeric",
        "typical_min": 0,
        "typical_max": 500
    }}}
```

### `TimeSeriesDataPoint` Model

```python
from datetime import datetime

class TimeSeriesDataPoint(BaseModel):
    timestamp: datetime = Field(..., description="ISO 8601 UTC timestamp")
    well_id: str = Field(..., pattern=r"^WELL-\d{3}$")
    metric_name: str
    value: float
    unit: str
    quality_flag: Literal["good", "suspect", "bad"] = "good"

    model_config = {"json_schema_extra": {"example": {
        "timestamp": "2024-01-01T00:00:00Z",
        "well_id": "WELL-001",
        "metric_name": "oil_production_rate",
        "value": 245.7,
        "unit": "bbl/day",
        "quality_flag": "good"
    }}}
```

### `AggregatedDataPoint` Model

```python
class AggregatedDataPoint(BaseModel):
    date: date = Field(..., description="Date or start of time period")
    time_period: str = Field(..., description="Period label")
    well_id: str = Field(..., pattern=r"^WELL-\d{3}$")
    metric_name: str
    aggregated_value: float
    aggregation_type: Literal["daily_average", "daily_max", "daily_min", "daily_sum", "monthly_average"]
    unit: str
    data_point_count: int = Field(..., ge=1)
    min_value: float
    max_value: float
    data_completeness: float = Field(..., ge=0, le=100, description="Percentage")

    model_config = {"json_schema_extra": {"example": {
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
        "data_completeness": 100.0
    }}}
```

---

## API Response Structures

### `WellListResponse`

```python
class WellListResponse(BaseModel):
    wells: list[Well]
    total_count: int = Field(..., description="Total number of wells")
    metadata: dict = Field(default_factory=dict, description="Additional context")

    model_config = {"json_schema_extra": {"example": {
        "wells": [{"well_id": "WELL-001", "well_name": "North Field Alpha 1", ...}],
        "total_count": 5,
        "metadata": {"generated_at": "2024-12-09T10:30:00Z"}
    }}}
```

### `MetricListResponse`

```python
class MetricListResponse(BaseModel):
    metrics: list[Metric]
    total_count: int
    metadata: dict = Field(default_factory=dict)

    model_config = {"json_schema_extra": {"example": {
        "metrics": [{"metric_name": "oil_production_rate", ...}],
        "total_count": 8,
        "metadata": {"generated_at": "2024-12-09T10:30:00Z"}
    }}}
```

### `RawDataResponse`

```python
class RawDataResponse(BaseModel):
    data: list[TimeSeriesDataPoint]
    metadata: dict = Field(..., description="Query context and statistics")

    model_config = {"json_schema_extra": {"example": {
        "data": [{"timestamp": "2024-01-01T00:00:00Z", "value": 245.7, ...}],
        "metadata": {
            "well_id": "WELL-001",
            "metric_name": "oil_production_rate",
            "start_timestamp": "2024-01-01T00:00:00Z",
            "end_timestamp": "2024-01-31T23:59:59Z",
            "total_points": 44640,
            "data_completeness": 99.8
        }
    }}}
```

### `AggregatedDataResponse`

```python
class AggregatedDataResponse(BaseModel):
    data: list[AggregatedDataPoint]
    metadata: dict = Field(..., description="Query context and statistics")

    model_config = {"json_schema_extra": {"example": {
        "data": [{"date": "2024-01-01", "aggregated_value": 248.3, ...}],
        "metadata": {
            "well_id": "WELL-001",
            "metric_name": "oil_production_rate",
            "aggregation_type": "daily_average",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "total_periods": 31,
            "average_data_completeness": 99.5
        }
    }}}
```

---

## Data Volume Estimates

| Entity | Count | Storage per Row | Total Storage |
|--------|-------|-----------------|---------------|
| Wells | 5 | ~200 bytes | ~1 KB |
| Metrics | 8 | ~150 bytes | ~1.2 KB |
| TimeSeriesData | ~42,048,000 | ~30 bytes | ~1.26 GB |
| **Total** | | | **~1.26 GB** |

**Calculation**:
- 5 wells × 8 metrics × 2 years × 365.25 days/year × 1440 minutes/day = 42,048,000 rows
- Each row: 8 bytes (id) + 20 bytes (timestamp) + 10 bytes (well_id) + 20 bytes (metric_name) + 8 bytes (value) + 5 bytes (quality_flag) ≈ 71 bytes raw
- With SQLite overhead and indexes: ~30 bytes per row effective storage
- Total: 42,048,000 × 30 bytes ≈ 1.26 GB

**Index Storage**:
- `idx_well_metric_time`: ~15% of data size ≈ 190 MB
- `idx_timestamp`: ~10% of data size ≈ 126 MB
- Total with indexes: ~1.58 GB

---

## Next Steps

1. Create OpenAPI specification in `contracts/` directory
2. Implement Pydantic models in `src/models/`
3. Create database schema and seed script in `src/db/`
4. Implement service layer in `src/services/`
5. Implement API routes in `src/api/`
