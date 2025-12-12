# Chat with Timeseries

A monorepo demonstration project showcasing AI-powered chat interfaces for time-series data analysis.

## 🎯 Overview

This repository contains multiple interconnected projects:

### 📊 [Time Series API](timeseries-api/)
REST API serving synthetic oil well time-series data for demonstration and testing purposes. Provides access to 1 year of realistic synthetic operational data for 3 sample oil wells.

**Features:**
- Query raw timestamped data at minute-level granularity
- Retrieve aggregated summaries (daily/monthly averages, sums, min, max)
- Discover available wells and metrics
- Built with Python 3.14, FastAPI, and SQLite

### 💬 AI Chat Frontend *(Coming Soon)*
Natural language interface for querying and analyzing time-series data.

## 🚀 Quick Start

See [timeseries-api/README.md](timeseries-api/README.md) for API-specific documentation.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [VS Code](https://code.visualstudio.com/)
- [Dev Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Setup (Dev Container)

1. Clone the repository:
   ```bash
   git clone https://github.com/syedhassaanahmed/chat-with-timeseries-speckit.git
   cd chat-with-timeseries-speckit
   ```

2. Open in VS Code and reopen in Dev Container:
   - Press `F1` → **"Dev Containers: Reopen in Container"**
   - Wait for container build (~2-3 minutes on first run)

3. Start the API server:
   ```bash
   source timeseries-api/.venv/bin/activate
   uvicorn timeseries-api.src.api.main:app --reload --port 8000
   ```

4. Access API documentation:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🔧 Code Quality

```bash
# Lint code
ruff check src/ tests/

# Format code
ruff format src/ tests/

# Auto-fix issues
ruff check --fix src/ tests/
```

## 🛠️ Development

From the repository root:

```bash
# Run tests
make test

# Lint code
make lint

# Fix linting issues and format
make fix
```

## 📁 Project Structure

```
chat-with-timeseries-speckit/
├── timeseries-api/          # Time Series API (Python/FastAPI)
│   ├── src/                 # Source code
│   ├── tests/               # Unit/integration tests
│   ├── data/                # SQLite database
│   ├── pyproject.toml       # Python dependencies
│   └── README.md            # API documentation
├── specs/                   # Project specifications
│   └── 001-oil-well-api/    # API specification
├── .devcontainer/           # Dev Container config
├── .githooks/               # Git hooks
├── Makefile                 # Build commands
├── ruff.toml                # Shared linter config
└── README.md                # This file (monorepo overview)
```

## 📚 Documentation

### Time Series API
- [API README](timeseries-api/README.md) - API-specific documentation

## 🏗️ Tech Stack

### Time Series API
- **Python 3.14** - Latest Python version
- **FastAPI** - Modern async web framework
- **SQLite** - Embedded database (~2.5 GB for 7.9M data points)
- **uv** - Fast Python package manager
- **ruff** - Fast Python linter and formatter
- **pytest** - Testing framework
- **Pydantic v2** - Data validation

## 📝 License

MIT

## 🤝 Contributing

This project follows the [Speckit Constitution](docs/constitution/v1.0.0.md) principles. CONTRIBUTING.md and CODE_OF_CONDUCT.md will be added in a future release.
