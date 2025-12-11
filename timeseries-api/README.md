# Oil Well Time Series API

REST API serving synthetic oil well time-series data for demonstration and testing purposes.

## Overview

This API provides access to 1 year of realistic synthetic operational data for 3 sample oil wells, including:
- Oil and gas production rates
- Wellhead and tubing pressures
- Gas injection rates

**Key Features:**
- Query raw timestamped data at minute-level granularity
- Retrieve aggregated summaries (daily/monthly averages, sums, min, max)
- Discover available wells and metrics
- No authentication required (publicly accessible)
- All data is synthetic (no real oilfield information)

## API Endpoints

### Discovery Endpoints
- **GET /wells** - List all available wells
- **GET /wells/{well_id}** - Get details for a specific well
- **GET /wells/{well_id}/metrics** - List metrics available for a well
- **GET /metrics** - List all available metrics

### Data Query Endpoints
- **GET /wells/{well_id}/data/raw** - Query raw time-series data
  - Query parameters: `metric_name`, `start_timestamp`, `end_timestamp`
  - Returns minute-level timestamped data points
- **GET /wells/{well_id}/data/aggregated** - Query aggregated data
  - Query parameters: `metric_name`, `start_date`, `end_date`, `aggregation_type`
  - Aggregation types: `daily_average`, `daily_max`, `daily_min`, `daily_sum`, `monthly_average`
  - Returns one data point per period (day or month)

## Quick Start

From the repository root:

```bash
# Activate virtual environment
source timeseries-api/.venv/bin/activate

# Start API server
uvicorn timeseries-api.src.api.main:app --reload --port 8000
```

Access API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Example Usage

```bash
# List all wells
curl http://localhost:8000/wells

# Get raw data for oil production
curl "http://localhost:8000/wells/WELL-001/data/raw?metric_name=oil_production_rate&start_timestamp=2024-12-09T00:00:00Z&end_timestamp=2024-12-09T01:00:00Z"

# Get daily average aggregation
curl "http://localhost:8000/wells/WELL-001/data/aggregated?metric_name=wellhead_pressure&start_date=2024-12-09&end_date=2024-12-15&aggregation_type=daily_average"
```

## Development

From the repository root:

```bash
# Run all tests
make test

# Run tests with coverage report
make test-cov

# Lint code
make lint

# Fix linting issues and format code
make fix
```

## Test Coverage

Current test coverage: **66.4%**

- ✅ 78 tests passing
- ✅ 10 contract tests (OpenAPI compliance)
- ✅ 41 integration tests (API endpoints)
- ✅ 27 unit tests (services and data generation)

## Tech Stack

- **Python 3.14** - Latest Python version
- **FastAPI** - Modern async web framework
- **SQLite** - Embedded database (~2.5 GB for 7.9M data points)
- **uv** - Fast Python package manager
- **ruff** - Fast Python linter and formatter
- **pytest** - Testing framework
- **Pydantic v2** - Data validation

## Project Structure

```
timeseries-api/
├── src/
│   ├── api/            # FastAPI endpoints
│   ├── models/         # Pydantic data models
│   ├── services/       # Business logic
│   └── db/             # Database and seeding
├── tests/
│   ├── contract/       # OpenAPI schema tests
│   ├── integration/    # API endpoint tests
│   └── unit/           # Service layer tests
├── data/               # SQLite database
└── pyproject.toml      # Dependencies and config
```

## Documentation

For complete specifications and architecture details, see:
- [Specification](../specs/001-oil-well-api/spec.md)
- [Implementation Plan](../specs/001-oil-well-api/plan.md)
- [Quick Start Guide](../specs/001-oil-well-api/quickstart.md)
- [OpenAPI Contract](../specs/001-oil-well-api/contracts/openapi.yaml)

## License

MIT

