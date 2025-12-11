"""Integration tests for wells API endpoints."""

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


def test_list_all_wells(client: TestClient) -> None:
    """Test GET /wells returns all wells with correct structure."""
    response = client.get("/wells")

    assert response.status_code == 200

    data = response.json()
    assert "wells" in data
    assert "total_count" in data
    assert "metadata" in data

    # Should have 3 wells (per configuration)
    assert data["total_count"] == 3
    assert len(data["wells"]) == 3

    # Verify well structure
    well = data["wells"][0]
    assert "well_id" in well
    assert "well_name" in well
    assert "latitude" in well
    assert "longitude" in well
    assert "operator" in well
    assert "field_name" in well
    assert "well_type" in well
    assert "spud_date" in well
    assert "data_start_date" in well
    assert "data_end_date" in well

    # Verify well_id format
    assert well["well_id"].startswith("WELL-")

    # Verify well_type is valid enum
    assert well["well_type"] in ["producer", "injector", "observation"]

    # Verify metadata
    assert "generated_at" in data["metadata"]


def test_get_well_by_id_success(client: TestClient, db_connection: sqlite3.Connection) -> None:
    """Test GET /wells/{well_id} returns specific well."""
    # Get a valid well_id from database
    cursor = db_connection.cursor()
    cursor.execute("SELECT well_id FROM wells LIMIT 1")
    result = cursor.fetchone()
    assert result is not None, "No wells found in database"

    well_id = result[0]

    response = client.get(f"/wells/{well_id}")

    assert response.status_code == 200

    well = response.json()
    assert well["well_id"] == well_id
    assert "well_name" in well
    assert "latitude" in well
    assert "longitude" in well


def test_get_well_by_id_not_found(client: TestClient) -> None:
    """Test GET /wells/{well_id} returns 404 for non-existent well."""
    response = client.get("/wells/WELL-999")

    assert response.status_code == 404

    error = response.json()
    assert "detail" in error
    assert "not found" in error["detail"].lower()


def test_get_well_by_id_invalid_format(client: TestClient) -> None:
    """Test GET /wells/{well_id} handles invalid well_id format."""
    # Invalid format (not matching WELL-XXX pattern)
    response = client.get("/wells/INVALID-ID")

    # Should return 404 since well doesn't exist
    assert response.status_code == 404


def test_get_well_metrics(client: TestClient, db_connection: sqlite3.Connection) -> None:
    """Test GET /wells/{well_id}/metrics returns metrics for specific well."""
    # Get a valid well_id
    cursor = db_connection.cursor()
    cursor.execute("SELECT well_id FROM wells LIMIT 1")
    result = cursor.fetchone()
    assert result is not None

    well_id = result[0]

    response = client.get(f"/wells/{well_id}/metrics")

    assert response.status_code == 200

    data = response.json()
    assert "metrics" in data
    assert "total_count" in data

    # Should have metrics (at least 1)
    assert data["total_count"] > 0
    assert len(data["metrics"]) > 0

    # Verify metric structure
    metric = data["metrics"][0]
    assert "metric_name" in metric
    assert "display_name" in metric
    assert "unit_of_measurement" in metric


def test_get_well_metrics_not_found(client: TestClient) -> None:
    """Test GET /wells/{well_id}/metrics returns 404 for non-existent well."""
    response = client.get("/wells/WELL-999/metrics")

    assert response.status_code == 404
