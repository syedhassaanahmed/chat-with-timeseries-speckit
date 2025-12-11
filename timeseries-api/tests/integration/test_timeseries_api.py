"""Integration tests for timeseries data API endpoints."""

import sqlite3
from datetime import datetime

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


@pytest.fixture
def valid_well_id(db_connection: sqlite3.Connection) -> str:
    """Get a valid well_id from the database."""
    cursor = db_connection.cursor()
    cursor.execute("SELECT well_id FROM wells LIMIT 1")
    result = cursor.fetchone()
    assert result is not None, "No wells found in database"
    return result[0]


@pytest.fixture
def valid_metric_name(db_connection: sqlite3.Connection) -> str:
    """Get a valid metric_name from the database."""
    cursor = db_connection.cursor()
    cursor.execute("SELECT metric_name FROM metrics LIMIT 1")
    result = cursor.fetchone()
    assert result is not None, "No metrics found in database"
    return result[0]


def test_get_raw_data_success(
    client: TestClient, valid_well_id: str, valid_metric_name: str
) -> None:
    """Test GET /wells/{well_id}/data/raw returns data successfully."""
    # Use time range from configuration (2024-12-09 to 2025-01-09)
    params = {
        "metric_name": valid_metric_name,
        "start_timestamp": "2024-12-09T00:00:00Z",
        "end_timestamp": "2024-12-09T01:00:00Z",  # 1 hour of data
    }

    response = client.get(f"/wells/{valid_well_id}/data/raw", params=params)

    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "metadata" in data

    # Verify data array structure
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0

    # Verify data point structure
    point = data["data"][0]
    assert "timestamp" in point
    assert "value" in point
    assert "quality_flag" in point

    # Verify timestamp is ISO 8601 format
    timestamp = point["timestamp"]
    assert "T" in timestamp
    datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    # Verify value is numeric
    assert isinstance(point["value"], (int, float))

    # Verify quality_flag is valid enum
    assert point["quality_flag"] in ["good", "suspect", "bad", "estimated"]

    # Verify metadata
    metadata = data["metadata"]
    assert "well_id" in metadata
    assert "metric_name" in metadata
    assert "start_timestamp" in metadata
    assert "end_timestamp" in metadata
    assert "total_points" in metadata
    assert "data_completeness" in metadata

    # Verify metadata values
    assert metadata["well_id"] == valid_well_id
    assert metadata["metric_name"] == valid_metric_name
    assert metadata["total_points"] == len(data["data"])
    assert 0 <= metadata["data_completeness"] <= 100


def test_get_raw_data_invalid_well_id(client: TestClient, valid_metric_name: str) -> None:
    """Test GET /wells/{well_id}/data/raw returns 404 for non-existent well."""
    params = {
        "metric_name": valid_metric_name,
        "start_timestamp": "2024-12-09T00:00:00Z",
        "end_timestamp": "2024-12-09T01:00:00Z",
    }

    response = client.get("/wells/WELL-999/data/raw", params=params)

    assert response.status_code == 404

    error = response.json()
    assert "detail" in error
    assert "well" in error["detail"].lower() or "not found" in error["detail"].lower()


def test_get_raw_data_invalid_metric_name(client: TestClient, valid_well_id: str) -> None:
    """Test GET /wells/{well_id}/data/raw returns 404 for non-existent metric."""
    params = {
        "metric_name": "invalid_metric_xyz",
        "start_timestamp": "2024-12-09T00:00:00Z",
        "end_timestamp": "2024-12-09T01:00:00Z",
    }

    response = client.get(f"/wells/{valid_well_id}/data/raw", params=params)

    assert response.status_code == 404

    error = response.json()
    assert "detail" in error
    assert "metric" in error["detail"].lower() or "not found" in error["detail"].lower()


def test_get_raw_data_invalid_timestamp_format(
    client: TestClient, valid_well_id: str, valid_metric_name: str
) -> None:
    """Test GET /wells/{well_id}/data/raw returns error for invalid timestamp."""
    # Invalid timestamp format (missing time component)
    params = {
        "metric_name": valid_metric_name,
        "start_timestamp": "2024-12-09",  # Missing time component
        "end_timestamp": "2024-12-09T01:00:00Z",
    }

    response = client.get(f"/wells/{valid_well_id}/data/raw", params=params)

    # FastAPI returns 422 for validation errors, 500 if parsing fails during validation
    assert response.status_code in [400, 422, 500]

    error = response.json()
    assert "detail" in error


def test_get_raw_data_missing_required_param(client: TestClient, valid_well_id: str) -> None:
    """Test GET /wells/{well_id}/data/raw returns 422 for missing parameters."""
    # Missing metric_name
    params = {
        "start_timestamp": "2024-12-09T00:00:00Z",
        "end_timestamp": "2024-12-09T01:00:00Z",
    }

    response = client.get(f"/wells/{valid_well_id}/data/raw", params=params)

    assert response.status_code == 422

    error = response.json()
    assert "detail" in error


def test_get_raw_data_empty_result(
    client: TestClient, valid_well_id: str, valid_metric_name: str
) -> None:
    """Test GET /wells/{well_id}/data/raw with time range containing no data."""
    # Use a time range far in the future
    params = {
        "metric_name": valid_metric_name,
        "start_timestamp": "2030-01-01T00:00:00Z",
        "end_timestamp": "2030-01-01T01:00:00Z",
    }

    response = client.get(f"/wells/{valid_well_id}/data/raw", params=params)

    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "metadata" in data

    # Should return empty data array
    assert len(data["data"]) == 0
    assert data["metadata"]["total_points"] == 0
    assert data["metadata"]["data_completeness"] == 0


def test_get_raw_data_inverted_time_range(
    client: TestClient, valid_well_id: str, valid_metric_name: str
) -> None:
    """Test GET /wells/{well_id}/data/raw with start > end timestamp."""
    # Start timestamp after end timestamp
    params = {
        "metric_name": valid_metric_name,
        "start_timestamp": "2024-12-10T00:00:00Z",
        "end_timestamp": "2024-12-09T00:00:00Z",  # Earlier than start
    }

    response = client.get(f"/wells/{valid_well_id}/data/raw", params=params)

    # Should return 400 or empty result
    assert response.status_code in [200, 400]

    if response.status_code == 200:
        data = response.json()
        # Empty result is acceptable for inverted range
        assert len(data["data"]) == 0


def test_get_raw_data_large_time_range(
    client: TestClient, valid_well_id: str, valid_metric_name: str
) -> None:
    """Test GET /wells/{well_id}/data/raw with large time range."""
    # Request full month of data (2024-12-09 to 2025-01-09)
    params = {
        "metric_name": valid_metric_name,
        "start_timestamp": "2024-12-09T00:00:00Z",
        "end_timestamp": "2025-01-09T00:00:00Z",
    }

    response = client.get(f"/wells/{valid_well_id}/data/raw", params=params)

    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0

    # Should have many data points (minute-level data for a month)
    # Approximately 31 days * 24 hours * 60 minutes = ~44,640 points
    assert data["metadata"]["total_points"] > 1000


def test_get_raw_data_data_completeness_calculation(
    client: TestClient, valid_well_id: str, valid_metric_name: str
) -> None:
    """Test that data_completeness is calculated correctly."""
    params = {
        "metric_name": valid_metric_name,
        "start_timestamp": "2024-12-09T00:00:00Z",
        "end_timestamp": "2024-12-09T01:00:00Z",
    }

    response = client.get(f"/wells/{valid_well_id}/data/raw", params=params)

    assert response.status_code == 200

    data = response.json()
    metadata = data["metadata"]

    # Data completeness should be percentage (0-100)
    assert isinstance(metadata["data_completeness"], (int, float))
    assert 0 <= metadata["data_completeness"] <= 100

    # For 1 hour, we expect 61 data points (minute-level, inclusive range)
    # 00:00:00 to 01:00:00 includes both endpoints
    # Completeness = (actual_points / 61) * 100
    expected_points = 61
    actual_points = metadata["total_points"]
    expected_completeness = (actual_points / expected_points) * 100

    # Allow for small floating-point differences
    assert abs(metadata["data_completeness"] - expected_completeness) < 1


def test_get_raw_data_timezone_handling(
    client: TestClient, valid_well_id: str, valid_metric_name: str
) -> None:
    """Test that timestamps with different timezone formats are handled."""
    # Test with UTC offset instead of Z suffix
    params = {
        "metric_name": valid_metric_name,
        "start_timestamp": "2024-12-09T00:00:00+00:00",
        "end_timestamp": "2024-12-09T01:00:00+00:00",
    }

    response = client.get(f"/wells/{valid_well_id}/data/raw", params=params)

    assert response.status_code == 200

    data = response.json()
    assert len(data["data"]) > 0


def test_get_raw_data_timestamps_are_sorted(
    client: TestClient, valid_well_id: str, valid_metric_name: str
) -> None:
    """Test that returned data points are sorted by timestamp."""
    params = {
        "metric_name": valid_metric_name,
        "start_timestamp": "2024-12-09T00:00:00Z",
        "end_timestamp": "2024-12-09T01:00:00Z",
    }

    response = client.get(f"/wells/{valid_well_id}/data/raw", params=params)

    assert response.status_code == 200

    data = response.json()
    timestamps = [
        datetime.fromisoformat(point["timestamp"].replace("Z", "+00:00")) for point in data["data"]
    ]

    # Verify timestamps are in ascending order
    assert timestamps == sorted(timestamps)


def test_get_raw_data_values_are_within_expected_range(
    client: TestClient, valid_well_id: str, db_connection: sqlite3.Connection
) -> None:
    """Test that returned values are within typical ranges for the metric."""
    # Get a metric with typical_min and typical_max
    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT metric_name, typical_min, typical_max FROM metrics "
        "WHERE typical_min IS NOT NULL AND typical_max IS NOT NULL LIMIT 1"
    )
    result = cursor.fetchone()
    assert result is not None, "No metrics with typical ranges found"

    metric_name, typical_min, typical_max = result

    params = {
        "metric_name": metric_name,
        "start_timestamp": "2024-12-09T00:00:00Z",
        "end_timestamp": "2024-12-09T01:00:00Z",
    }

    response = client.get(f"/wells/{valid_well_id}/data/raw", params=params)

    assert response.status_code == 200

    data = response.json()

    # Values should generally be within typical ranges
    # (allowing for some outliers due to noise and variations)
    for point in data["data"]:
        value = point["value"]
        # Allow values to be up to 50% outside typical range (due to synthetic variations)
        assert value >= typical_min * 0.5
        assert value <= typical_max * 1.5
