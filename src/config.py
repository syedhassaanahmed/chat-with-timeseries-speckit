"""Configuration module for Oil Well Time Series API."""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "timeseries.db"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Database configuration
DB_CONNECTION_STRING = f"sqlite:///{DATABASE_PATH}"

# Data generation constants
NUM_WELLS = 3
NUM_METRICS = 5
DATA_START_DATE = "2024-12-09"
DATA_END_DATE = "2025-12-09"
DATA_FREQUENCY_MINUTES = 1  # Minute-level granularity

# Well configuration
WELL_TYPES = ["producer", "injector", "observation"]
FIELDS = ["North Field", "South Field", "East Field"]
OPERATORS = ["Demo Energy Corp", "Example Oil LLC", "Test Petroleum Inc"]

# Metric definitions
METRIC_CONFIGS = {
    "oil_production_rate": {
        "display_name": "Oil Production Rate",
        "unit": "bbl/day",
        "typical_min": 0,
        "typical_max": 500,
        "data_type": "numeric",
    },
    "gas_production_rate": {
        "display_name": "Gas Production Rate",
        "unit": "mcf/day",
        "typical_min": 0,
        "typical_max": 2000,
        "data_type": "numeric",
    },
    "wellhead_pressure": {
        "display_name": "Wellhead Pressure",
        "unit": "psi",
        "typical_min": 100,
        "typical_max": 3000,
        "data_type": "numeric",
    },
    "tubing_pressure": {
        "display_name": "Tubing Pressure",
        "unit": "psi",
        "typical_min": 50,
        "typical_max": 2500,
        "data_type": "numeric",
    },
    "gas_injection_rate": {
        "display_name": "Gas Injection Rate",
        "unit": "mcf/day",
        "typical_min": 0,
        "typical_max": 1500,
        "data_type": "numeric",
    },
}

# Production profile defaults (for synthetic data generation)
INITIAL_PRODUCTION_MIN = 200
INITIAL_PRODUCTION_MAX = 500
DECLINE_RATE_MIN = 0.00015  # Per day
DECLINE_RATE_MAX = 0.00045
SEASONAL_AMPLITUDE = 0.1  # ±10% seasonal variation
NOISE_AMPLITUDE = 0.05  # ±5% random noise
MAINTENANCE_PROBABILITY = 0.015  # ~1.5% chance of maintenance per day
MAINTENANCE_DURATION_MIN = 2  # days
MAINTENANCE_DURATION_MAX = 7  # days

# API configuration
API_TITLE = "Oil Well Time Series API"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
A public REST API that serves synthetic oil well time-series data for demonstration and testing purposes.

This API provides access to 2 years of realistic synthetic operational data for 5 sample oil wells.
"""

# CORS settings
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["GET"]
CORS_ALLOW_HEADERS = ["*"]

# Environment variable overrides
if os.getenv("DATABASE_PATH"):
    DATABASE_PATH = Path(os.getenv("DATABASE_PATH"))
    DB_CONNECTION_STRING = f"sqlite:///{DATABASE_PATH}"
