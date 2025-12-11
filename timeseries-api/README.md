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

## Development

From the repository root:

```bash
# Run tests
make test

# Lint code
make lint

# Fix linting issues and format code
make fix
```

## Tech Stack

- **Python 3.14** - Latest Python version
- **FastAPI** - Modern async web framework
- **SQLite** - Embedded database (~2.5 GB for 7.9M data points)
- **uv** - Fast Python package manager
- **ruff** - Fast Python linter and formatter
- **pytest** - Testing framework
- **Pydantic v2** - Data validation

## Documentation

See the [main repository documentation](../README.md) for complete setup instructions and API details.

## License

MIT
