# Oil Well Time Series API

A REST API that serves synthetic oil well time-series data for demonstration and testing purposes. Built with Python 3.14, FastAPI, and SQLite.

## 🎯 Overview

This API provides access to 2 years of realistic synthetic operational data for 5 sample oil wells, including:
- Oil, gas, and water production rates
- Wellhead and tubing pressures  
- Gas injection rates
- Choke settings
- Well status indicators

**Key Features:**
- Query raw timestamped data at minute-level granularity
- Retrieve aggregated summaries (daily/monthly averages, sums, min, max)
- Discover available wells and metrics
- No authentication required (publicly accessible)
- All data is synthetic (no real oilfield information)

## 🚀 Quick Start

See [specs/001-oil-well-api/quickstart.md](specs/001-oil-well-api/quickstart.md) for detailed setup instructions using Dev Containers.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [VS Code](https://code.visualstudio.com/)
- [Dev Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Setup (Dev Container)

1. Clone the repository:
   ```bash
   git clone https://github.com/syedhassaanahmed/chat-with-timeseries-speckit.git
   cd chat-with-timeseries-speckit
   git checkout 001-oil-well-api
   ```

2. Open in VS Code and reopen in Dev Container:
   - Press `F1` → **"Dev Containers: Reopen in Container"**
   - Wait for container build (~2-3 minutes on first run)

3. Start the API server:
   ```bash
   uvicorn src.api.main:app --reload --port 8000
   ```

4. Access API documentation:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 📊 API Endpoints

### Discovery
- `GET /wells` - List all available wells
- `GET /wells/{well_id}` - Get details for a specific well
- `GET /metrics` - List all available metrics
- `GET /wells/{well_id}/metrics` - Get metrics for a specific well

### Time-Series Data
- `GET /wells/{well_id}/data/raw` - Query raw time-series data
  - Query params: `metric_name`, `start_timestamp`, `end_timestamp`
- `GET /wells/{well_id}/data/aggregated` - Query aggregated data
  - Query params: `metric_name`, `start_date`, `end_date`, `aggregation_type`

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test suites
pytest tests/unit/
pytest tests/integration/
pytest tests/contract/
```

## 🔧 Code Quality

```bash
# Lint code
ruff check src/ tests/

# Format code
ruff format src/ tests/

# Auto-fix issues
ruff check --fix src/ tests/
```

## 📚 Documentation

- [Feature Specification](specs/001-oil-well-api/spec.md) - Requirements and user stories
- [Implementation Plan](specs/001-oil-well-api/plan.md) - Architecture and technical decisions
- [Data Model](specs/001-oil-well-api/data-model.md) - Database schema and Pydantic models
- [API Contract](specs/001-oil-well-api/contracts/openapi.yaml) - OpenAPI specification
- [Quick Start Guide](specs/001-oil-well-api/quickstart.md) - Setup and usage examples

## 🏗️ Tech Stack

- **Python 3.14** - Latest Python version
- **FastAPI** - Modern async web framework
- **SQLite** - Embedded database (~1.26 GB for 42M data points)
- **uv** - Fast Python package manager
- **ruff** - Fast Python linter and formatter
- **pytest** - Testing framework
- **Pydantic v2** - Data validation

## 📝 License

MIT

## 🤝 Contributing

This project follows the [Speckit Constitution](docs/constitution/v1.0.0.md) principles. CONTRIBUTING.md and CODE_OF_CONDUCT.md will be added in a future release.
