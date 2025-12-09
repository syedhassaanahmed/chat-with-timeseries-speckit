# Quick Start Guide: Oil Well Time Series API

**Feature**: 001-oil-well-api  
**Last Updated**: 2025-12-09

## Overview

This guide walks you through setting up and running the Oil Well Time Series API locally. The API serves synthetic oil well time-series data through a FastAPI-based REST interface.

## Prerequisites

> **Constitution Principle VII**: Dev Containers are non-negotiable for this project.

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or [Docker Engine](https://docs.docker.com/engine/install/)
- [VS Code](https://code.visualstudio.com/)
- [Dev Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

## Setup

### 1. Clone Repository

```bash
git clone https://github.com/syedhassaanahmed/chat-with-timeseries-speckit.git
cd chat-with-timeseries-speckit
git checkout 001-oil-well-api
```

### 2. Open in Dev Container

- Open the repository in VS Code
- Press `F1` and select **"Dev Containers: Reopen in Container"**
- Wait for container to build (~2-3 minutes on first run)

**What's included in the container**:
- Python 3.14
- uv package manager
- All project dependencies (FastAPI, uvicorn, pydantic, numpy, pandas, pytest, ruff)
- VS Code extensions (Python, Ruff, TOML)
- SQLite database initialized automatically with 2 years of synthetic data

### 3. Verify Setup

```bash
# Check Python version
python --version  # Should show Python 3.14.x

# Check uv installation
uv --version

# Verify database was created
ls -lh data/timeseries.db  # Should exist with ~1.26 GB
```

### 4. Start API Server

```bash
uvicorn src.api.main:app --reload --port 8000
```

**Expected output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 5. Access API Documentation

VS Code will automatically forward port 8000. Open your browser to:

- **Interactive API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative API Docs (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON Schema**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## API Usage Examples

### List All Wells

```bash
curl http://localhost:8000/wells | jq
```

**Expected Response**:
```json
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
      "spud_date": "2023-12-09",
      "data_start_date": "2024-12-09",
      "data_end_date": "2025-12-09"
    }
  ],
  "total_count": 3,
  "metadata": {"generated_at": "2024-12-09T10:30:00Z"}
}
```

---

### Get Well Details

```bash
curl http://localhost:8000/wells/WELL-001 | jq
```

---

### List All Metrics

```bash
curl http://localhost:8000/metrics | jq
```

**Expected Response**:
```json
{
  "metrics": [
    {
      "metric_name": "oil_production_rate",
      "display_name": "Oil Production Rate",
      "description": "Daily oil production volume from the well",
      "unit_of_measurement": "bbl/day",
      "data_type": "numeric",
      "typical_min": 0,
      "typical_max": 500
    }
  ],
  "total_count": 8,
  "metadata": {"generated_at": "2024-12-09T10:30:00Z"}
}
```

---

### Query Raw Time Series Data

```bash
curl "http://localhost:8000/wells/WELL-001/data/raw?\
metric_name=oil_production_rate&\
start_timestamp=2024-01-01T00:00:00Z&\
end_timestamp=2024-01-01T01:00:00Z" | jq
```

**Expected Response** (abbreviated):
```json
{
  "data": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "well_id": "WELL-001",
      "metric_name": "oil_production_rate",
      "value": 245.7,
      "unit": "bbl/day",
      "quality_flag": "good"
    },
    {
      "timestamp": "2024-01-01T00:01:00Z",
      "well_id": "WELL-001",
      "metric_name": "oil_production_rate",
      "value": 246.1,
      "unit": "bbl/day",
      "quality_flag": "good"
    }
  ],
  "metadata": {
    "well_id": "WELL-001",
    "metric_name": "oil_production_rate",
    "start_timestamp": "2024-01-01T00:00:00Z",
    "end_timestamp": "2024-01-01T01:00:00Z",
    "total_points": 61,
    "data_completeness": 100.0
  }
}
```

---

### Query Aggregated Time Series Data

```bash
curl "http://localhost:8000/wells/WELL-001/data/aggregated?\
metric_name=oil_production_rate&\
start_date=2024-01-01&\
end_date=2024-01-31&\
aggregation_type=daily_average" | jq
```

**Expected Response** (abbreviated):
```json
{
  "data": [
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
  ],
  "metadata": {
    "well_id": "WELL-001",
    "metric_name": "oil_production_rate",
    "aggregation_type": "daily_average",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "total_periods": 31,
    "average_data_completeness": 99.5
  }
}
```

---

## Running Tests

### Unit Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/test_aggregation.py -v

# Run with coverage report
pytest tests/unit/ --cov=src --cov-report=html
```

### Integration Tests

```bash
# Start API server first (in separate terminal)
uvicorn src.api.main:app --reload

# Run integration tests (in another terminal)
pytest tests/integration/ -v
```

### Contract Tests

```bash
# Validate OpenAPI spec compliance
pytest tests/contract/test_openapi_compliance.py -v
```

---

## Code Quality

### Linting

```bash
# Check for linting issues
ruff check src/ tests/

# Auto-fix fixable issues
ruff check --fix src/ tests/
```

### Formatting

```bash
# Check formatting
ruff format --check src/ tests/

# Apply formatting
ruff format src/ tests/
```

---

## Project Structure

```
src/
├── models/           # Pydantic models (Well, Metric, TimeSeriesDataPoint, etc.)
├── services/         # Business logic (data generation, query service, aggregation)
├── api/              # FastAPI routes (wells, metrics, timeseries endpoints)
├── db/               # Database layer (SQLite connection, schema, seed script)
└── config.py         # Configuration (environment variables, constants)

tests/
├── contract/         # OpenAPI schema validation tests
├── integration/      # API endpoint integration tests
└── unit/             # Unit tests for services and models

specs/001-oil-well-api/
├── spec.md           # Feature specification
├── plan.md           # Implementation plan (this feature)
├── research.md       # Technical research and decisions
├── data-model.md     # Data structures and database schema
├── contracts/        # OpenAPI specification
└── quickstart.md     # This guide
```

---

## Troubleshooting

### Issue: Dev Container fails to build

**Solution**: Ensure Docker is running and you have internet connectivity. Check Docker Desktop or run:
```bash
docker ps
```

### Issue: Database file not found after container setup

**Solution**: The postCreateCommand should run automatically. If not, manually initialize:
```bash
python src/db/seed.py
```

### Issue: Port 8000 already in use

**Solution**: Either stop the conflicting process or use a different port:
```bash
uvicorn src.api.main:app --reload --port 8001
```

### Issue: Extensions not loading in VS Code

**Solution**: Reload the window (`F1` → "Developer: Reload Window") or check that the Dev Container rebuilt successfully.

### Issue: Slow query performance

**Solution**: Verify database indexes were created:
```bash
sqlite3 data/timeseries.db "PRAGMA index_list('timeseries_data');"
```
Expected output should show `idx_well_metric_time` and `idx_timestamp`.

---

## Next Steps

1. **Explore API**: Use Swagger UI at [http://localhost:8000/docs](http://localhost:8000/docs) to try all endpoints
2. **Read Specification**: Review [spec.md](./spec.md) for detailed functional requirements
3. **Review Implementation Plan**: See [plan.md](./plan.md) for architecture and technical decisions
4. **Contribute**: (Future) See CONTRIBUTING.md for contribution guidelines
5. **Deploy**: (Future) See deployment guide for production setup

---

## Support

For issues or questions:
- Open an issue on [GitHub](https://github.com/syedhassaanahmed/chat-with-timeseries-speckit/issues)
- Review [data-model.md](./data-model.md) for data structure details
- Check [research.md](./research.md) for technical decisions and alternatives considered
