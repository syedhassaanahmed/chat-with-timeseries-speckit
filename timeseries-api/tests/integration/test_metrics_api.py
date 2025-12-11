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


def test_get_well_metrics(client: TestClient, db_connection: sqlite3.Connection) -> None:
    """Test GET /wells/{well_id}/metrics returns only metrics for that well."""
    response = client.get("/wells/WELL-001/metrics")

    assert response.status_code == 200
    data = response.json()

    assert "metrics" in data
    assert "total_count" in data

    # Should have metrics (all metrics should be available for all wells)
    assert data["total_count"] > 0
    assert len(data["metrics"]) > 0
