# Technical Research: Oil Well Time Series API

**Feature**: 001-oil-well-api  
**Date**: 2025-12-09  
**Purpose**: Resolve technical unknowns and document decisions for implementation planning

## Research Questions

### 1. How should we generate realistic synthetic oil well time-series data?

**Decision**: Use numpy and pandas for synthetic data generation with domain-specific patterns

**Rationale**:
- Oil well production follows predictable patterns: baseline production, exponential/hyperbolic decline curves, seasonal variations, and maintenance shutdowns
- Numpy provides efficient random number generation and mathematical functions for decline curves
- Pandas allows easy time-series manipulation and resampling
- Libraries like `faker` are insufficient for domain-specific physics-based data

**Implementation Approach**:
- Define production profiles per well (initial rate, decline rate, decline exponent)
- Generate minute-level timestamps for 2 years using `pd.date_range()`
- Apply decline curves: `production(t) = initial_rate * exp(-decline_rate * t)`
- Add seasonal variations: `seasonal_factor = 1 + 0.1 * sin(2π * day_of_year / 365)`
- Add random noise: `±5%` using `np.random.normal()`
- Simulate maintenance periods: set production to near-zero for random 2-7 day windows
- Generate correlated metrics: gas production correlates with oil, pressure decreases with depletion

**Alternatives Considered**:
- ❌ Random data: Would not exhibit realistic oilfield behavior (decline, correlations)
- ❌ CSV file uploads: Requires finding real public data (rare), and still synthetic is better for demo
- ❌ Real-time generation per query: Too slow, inconsistent data across queries

**Data Volume Estimate**:
- 3 wells × 5 metrics × 1 year × 525,600 min/year = ~7.9M data points
- Estimated storage: ~2.5 GB (30 bytes per row × 7.9M rows)

---

### 2. What storage mechanism is appropriate for SQLite time-series queries?

**Decision**: SQLite with indexed timestamp columns and on-the-fly aggregation

**Rationale**:
- SQLite is embedded (no external database server required), lightweight, and sufficient for ~1.26 GB of data
- Performance requirements are moderate (50 concurrent users, <2s for 90-day queries)
- Indexed queries on `(well_id, metric_name, timestamp)` provide fast range scans
- SQLite's `datetime()` and `strftime()` functions enable SQL-based aggregation
- No need for specialized time-series databases (InfluxDB, TimescaleDB) for this demo scale

**Schema Design**:
```sql
CREATE TABLE timeseries_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,  -- ISO 8601 UTC (e.g., '2024-01-01T00:00:00Z')
    well_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    value REAL NOT NULL,
    quality_flag TEXT DEFAULT 'good'
);

CREATE INDEX idx_well_metric_time ON timeseries_data(well_id, metric_name, timestamp);
CREATE INDEX idx_timestamp ON timeseries_data(timestamp);
```

**Query Pattern for Raw Data**:
```sql
SELECT timestamp, well_id, metric_name, value
FROM timeseries_data
WHERE well_id = ? AND metric_name = ? 
  AND timestamp BETWEEN ? AND ?
ORDER BY timestamp;
```

**Query Pattern for Daily Aggregation**:
```sql
SELECT 
    DATE(timestamp) as date,
    AVG(value) as aggregated_value,
    COUNT(*) as data_point_count,
    MIN(value) as min_value,
    MAX(value) as max_value
FROM timeseries_data
WHERE well_id = ? AND metric_name = ?
  AND DATE(timestamp) BETWEEN ? AND ?
GROUP BY DATE(timestamp)
ORDER BY date;
```

**Alternatives Considered**:
- ❌ PostgreSQL with TimescaleDB: Overkill for demo, requires external database server
- ❌ InfluxDB: Specialized time-series DB, but adds deployment complexity
- ❌ In-memory (Redis): Loses data on restart, 1.26 GB may exceed memory limits
- ❌ Parquet files: Read-only, no SQL query support, harder to implement aggregations

---

### 3. What FastAPI patterns best support modular time-series queries?

**Decision**: Use dependency injection for database connections and service layer separation

**Rationale**:
- FastAPI's dependency injection (`Depends()`) allows clean separation of concerns
- Database connections can be managed as dependencies, ensuring proper lifecycle (open/close)
- Service layer (in `services/`) handles business logic, keeping routes thin
- Pydantic v2 models provide automatic validation and OpenAPI schema generation

**Implementation Pattern**:
```python
# src/db/database.py
def get_db_connection():
    conn = sqlite3.connect("data/timeseries.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# src/api/timeseries.py
from fastapi import APIRouter, Depends, Query
from src.services.query_service import QueryService

router = APIRouter()

@router.get("/wells/{well_id}/data/raw")
def get_raw_data(
    well_id: str,
    metric_name: str = Query(..., description="Metric identifier"),
    start_timestamp: datetime = Query(...),
    end_timestamp: datetime = Query(...),
    db: sqlite3.Connection = Depends(get_db_connection),
    query_service: QueryService = Depends()
):
    return query_service.get_raw_timeseries(
        db, well_id, metric_name, start_timestamp, end_timestamp
    )
```

**Testability Benefits**:
- Routes can be tested with mocked `QueryService`
- `QueryService` can be unit tested with mocked database connections
- Integration tests use real SQLite database with test data

**Alternatives Considered**:
- ❌ Direct SQL in routes: Violates separation of concerns, hard to test
- ❌ ORM (SQLAlchemy): Adds complexity for simple queries, overhead for time-series scans
- ❌ GraphQL: Overkill for simple REST API, FastAPI+REST is simpler

---

### 4. How should we set up uv for package management with Python 3.14?

**Decision**: Use `uv` with `pyproject.toml` for dependency management and virtual environment handling

**Rationale**:
- `uv` is a fast Python package installer (10-100x faster than pip) written in Rust
- Supports `pyproject.toml` standard (PEP 621) for declaring dependencies
- Handles virtual environments automatically (`uv venv`, `uv pip install`)
- Compatible with Python 3.14 (as of December 2025)
- Integrates with `ruff` for linting/formatting

**Setup Steps**:
1. Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Initialize project: `uv init` (creates `pyproject.toml`)
3. Add dependencies:
   ```toml
   [project]
   name = "oil-well-timeseries-api"
   version = "0.1.0"
   requires-python = ">=3.14"
   dependencies = [
       "fastapi>=0.115.0",
       "uvicorn[standard]>=0.32.0",
       "pydantic>=2.10.0",
       "numpy>=2.2.0",
       "pandas>=2.2.0",
       "httpx>=0.28.0",
       "pytest>=8.3.0",
       "pytest-asyncio>=0.24.0",
   ]
   ```
4. Install dependencies: `uv pip install -e .`
5. Run server: `uv run uvicorn src.api.main:app --reload`

**Alternatives Considered**:
- ❌ Poetry: Slower than uv, more complex dependency resolution
- ❌ pip + requirements.txt: Less structured, no lock file, slower installs
- ❌ Conda: Overkill for simple Python project, not optimized for speed

---

### 5. How should we configure ruff for linting and formatting?

**Decision**: Use `ruff` for both linting and formatting with opinionated defaults

**Rationale**:
- `ruff` is 10-100x faster than alternatives (black, flake8, isort combined)
- Single tool for linting and formatting reduces configuration complexity
- Built-in Python 3.14 support
- Enforces consistent code style across contributors (Constitution Principle V)
- Compatible with Black formatting style (industry standard)

**Configuration** (`ruff.toml`):
```toml
[lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "ANN", # flake8-annotations
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "SIM", # flake8-simplify
]
ignore = [
    "ANN101", # Missing type annotation for self
    "ANN102", # Missing type annotation for cls
]

[format]
quote-style = "double"
indent-style = "space"
line-ending = "lf"

[lint.per-file-ignores]
"tests/**/*.py" = ["ANN"]  # No type annotations required in tests
```

**Usage**:
- Check: `ruff check src/ tests/`
- Format: `ruff format src/ tests/`
- Fix auto-fixable issues: `ruff check --fix src/ tests/`

**CI Integration**:
```yaml
# .github/workflows/ci.yml
- name: Lint with ruff
  run: |
    uv pip install ruff
    ruff check src/ tests/
    ruff format --check src/ tests/
```

**Alternatives Considered**:
- ❌ Black + flake8 + isort: Multiple tools, slower, more config files
- ❌ Pylint: Comprehensive but very slow, many false positives
- ❌ No linting: Violates Constitution Principle V (code style enforcement)

---

### 6. What Dev Container configuration is required for Python 3.14 + FastAPI + uv?

**Decision**: Create `.devcontainer/devcontainer.json` with Python 3.14 base image, uv installation, and automated setup

**Rationale**:
- Constitution Principle VII mandates Dev Containers (non-negotiable)
- Eliminates "works on my machine" problems
- New contributors can start development in <5 minutes
- Consistent environment across all developers
- VS Code extensions (Python, Ruff) pre-configured

**Configuration Specification**:

```json
{
  "name": "Oil Well Time Series API",
  "image": "mcr.microsoft.com/devcontainers/python:3.14",
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {}
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "charliermarsh.ruff",
        "tamasfe.even-better-toml"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/usr/local/bin/python",
        "python.linting.enabled": true,
        "python.formatting.provider": "none",
        "[python]": {
          "editor.defaultFormatter": "charliermarsh.ruff",
          "editor.formatOnSave": true,
          "editor.codeActionsOnSave": {
            "source.organizeImports": true
          }
        }
      }
    }
  },
  "postCreateCommand": "bash .devcontainer/postCreate.sh",
  "forwardPorts": [8000]
}
```

**postCreate.sh Script**:
```bash
#!/bin/bash
set -e

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"

# Install dependencies
uv pip install -e .

# Create data directory
mkdir -p data

# Initialize database with synthetic data
python src/db/seed.py

echo "✓ Dev Container setup complete!"
echo "Run: uvicorn src.api.main:app --reload"
```

**Benefits**:
- One-click setup for new contributors
- Guaranteed Python 3.14 environment
- Automatic database initialization
- Pre-configured linting and formatting
- Port forwarding for API access

**Alternatives Considered**:
- ❌ Dockerfile only: Requires manual Docker commands, less integrated with VS Code
- ❌ docker-compose.yml: Overkill for single-service application
- ❌ No containerization: Violates Constitution Principle VII (non-negotiable)

---

## Summary of Decisions

| Category | Decision | Key Benefit |
|----------|----------|-------------|
| **Synthetic Data** | Numpy + Pandas with physics-based models | Realistic oilfield behavior (decline, correlations) |
| **Storage** | SQLite with indexed timestamps | Embedded, sufficient for 1.26 GB, SQL aggregations |
| **API Patterns** | FastAPI dependency injection + service layer | Clean separation, testability, automatic docs |
| **Package Mgmt** | uv with pyproject.toml | 10-100x faster than pip, modern Python standards |
| **Linting/Format** | ruff for both linting and formatting | Single fast tool, enforces consistency |
| **Dev Container** | Python 3.14 + uv + automated setup | One-click environment (Constitution VII requirement) |

**Next Steps**: Proceed to Phase 1 (Design) to define data models, API contracts, and quickstart guide.
