"""Integration tests for metrics API endpoints."""

import sqlite3

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def db_connection() -> sqlite3.Connection:
    """Get a database connection for test verification."""
    from src.config import DATABASE_PATH

    conn = sqlite3.connect(DATABASE_PATH)
    yield conn
    conn.close()


def test_list_all_metrics(client: TestClient) -> None:
    """Test GET /metrics returns all metrics with correct structure."""
    response = client.get("/metrics")

    assert response.status_code == 200

    data = response.json()
    assert "metrics" in data
    assert "total_count" in data
    assert "metadata" in data

    # Should have 5 metrics (per configuration)
    assert data["total_count"] == 5
    assert len(data["metrics"]) == 5

    # Verify metric structure
    metric = data["metrics"][0]
    assert "metric_name" in metric
    assert "display_name" in metric
    assert "description" in metric
    assert "unit_of_measurement" in metric
    assert "data_type" in metric
    assert "typical_min" in metric
    assert "typical_max" in metric

    # Verify data_type is valid enum
    assert metric["data_type"] in ["float", "integer", "boolean", "string", "numeric"]

    # Verify metadata
    assert "generated_at" in data["metadata"]


def test_metrics_response_format(client: TestClient) -> None:
    """Test that metrics response matches expected schema."""
    response = client.get("/metrics")

    assert response.status_code == 200
    data = response.json()

    # Verify all metrics have consistent structure
    for metric in data["metrics"]:
        # Check required fields are present and have correct types
        assert isinstance(metric["metric_name"], str)
        assert isinstance(metric["display_name"], str)
        assert isinstance(metric["description"], str)
        assert isinstance(metric["unit_of_measurement"], str)
        assert isinstance(metric["data_type"], str)

        # Numeric bounds should be numbers or None
        assert metric["typical_min"] is None or isinstance(metric["typical_min"], (int, float))
        assert metric["typical_max"] is None or isinstance(metric["typical_max"], (int, float))


def test_metrics_names_are_unique(client: TestClient) -> None:
    """Test that all metric names are unique."""
    response = client.get("/metrics")

    assert response.status_code == 200
    data = response.json()

    metric_names = [m["metric_name"] for m in data["metrics"]]

    # No duplicates
    assert len(metric_names) == len(set(metric_names))


def test_metrics_include_expected_types(
    client: TestClient, db_connection: sqlite3.Connection
) -> None:
    """Test that metrics include expected production and pressure types."""
    response = client.get("/metrics")

    assert response.status_code == 200
    data = response.json()

    metric_names = [m["metric_name"] for m in data["metrics"]]

    # Should include key oil field metrics
    expected_metrics = [
        "oil_production_rate",
        "gas_production_rate",
        "wellhead_pressure",
        "tubing_pressure",
        "gas_injection_rate",
    ]

    for expected in expected_metrics:
        assert expected in metric_names, f"Expected metric {expected} not found"


def test_metrics_metadata_includes_timestamp(client: TestClient) -> None:
    """Test that metadata includes a generated_at timestamp."""
    response = client.get("/metrics")

    assert response.status_code == 200
    data = response.json()

    assert "metadata" in data
    assert "generated_at" in data["metadata"]

    # Verify timestamp format (ISO 8601 with timezone)
    timestamp = data["metadata"]["generated_at"]
    assert "T" in timestamp
    assert timestamp.endswith("+00:00") or timestamp.endswith("Z")


def test_metrics_units_are_valid(client: TestClient) -> None:
    """Test that all metrics have valid unit of measurement."""
    response = client.get("/metrics")

    assert response.status_code == 200
    data = response.json()

    valid_units = [
        "bbl/day",  # barrels per day
        "Mcf/day",  # thousand cubic feet per day
        "mcf/day",  # lowercase variant
        "psi",  # pounds per square inch
        "kg/cm²",  # kilograms per square centimeter
    ]

    for metric in data["metrics"]:
        unit = metric["unit_of_measurement"]
        assert unit in valid_units, f"Unexpected unit: {unit}"


def test_metrics_typical_ranges_are_logical(client: TestClient) -> None:
    """Test that typical min/max ranges are logical (min <= max)."""
    response = client.get("/metrics")

    assert response.status_code == 200
    data = response.json()

    for metric in data["metrics"]:
        typical_min = metric["typical_min"]
        typical_max = metric["typical_max"]

        # If both are set, min should be less than or equal to max
        if typical_min is not None and typical_max is not None:
            assert typical_min <= typical_max, (
                f"Metric {metric['metric_name']} has invalid range: {typical_min} > {typical_max}"
            )
