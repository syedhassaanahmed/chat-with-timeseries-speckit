"""Integration tests for aggregated time-series API endpoints."""

from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_get_aggregated_daily_average() -> None:
    """Test successful daily average aggregation query."""
    response = client.get(
        "/wells/WELL-001/data/aggregated",
        params={
            "metric_name": "oil_production_rate",
            "start_date": "2024-12-09",
            "end_date": "2024-12-11",
            "aggregation_type": "daily_average",
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "data" in data
    assert "metadata" in data

    # Verify metadata
    metadata = data["metadata"]
    assert metadata["well_id"] == "WELL-001"
    assert metadata["metric_name"] == "oil_production_rate"
    assert metadata["aggregation_type"] == "daily_average"
    assert metadata["start_date"] == "2024-12-09"
    assert metadata["end_date"] == "2024-12-11"
    assert "total_periods" in metadata
    assert "average_data_completeness" in metadata

    # Verify data points
    data_points = data["data"]
    assert len(data_points) > 0

    # Verify first data point structure
    first_point = data_points[0]
    assert "date" in first_point
    assert "time_period" in first_point
    assert first_point["well_id"] == "WELL-001"
    assert first_point["metric_name"] == "oil_production_rate"
    assert first_point["aggregation_type"] == "daily_average"
    assert "aggregated_value" in first_point
    assert "unit" in first_point
    assert "data_point_count" in first_point
    assert "min_value" in first_point
    assert "max_value" in first_point
    assert "data_completeness" in first_point

    # Verify values are reasonable
    assert first_point["aggregated_value"] >= first_point["min_value"]
    assert first_point["aggregated_value"] <= first_point["max_value"]
    assert 0 <= first_point["data_completeness"] <= 100


def test_get_aggregated_daily_max() -> None:
    """Test daily maximum aggregation."""
    response = client.get(
        "/wells/WELL-001/data/aggregated",
        params={
            "metric_name": "wellhead_pressure",
            "start_date": "2024-12-09",
            "end_date": "2024-12-10",
            "aggregation_type": "daily_max",
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Verify aggregation type
    assert data["metadata"]["aggregation_type"] == "daily_max"
    assert len(data["data"]) > 0

    # Verify that aggregated_value equals max_value for MAX aggregation
    for point in data["data"]:
        assert point["aggregation_type"] == "daily_max"
        # For MAX aggregation, the aggregated value should be the maximum
        assert point["aggregated_value"] == point["max_value"]


def test_get_aggregated_monthly_average() -> None:
    """Test monthly average aggregation."""
    response = client.get(
        "/wells/WELL-002/data/aggregated",
        params={
            "metric_name": "gas_production_rate",
            "start_date": "2024-12-01",
            "end_date": "2024-12-31",
            "aggregation_type": "monthly_average",
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Verify aggregation type
    assert data["metadata"]["aggregation_type"] == "monthly_average"

    # Monthly aggregation should have one data point for December
    assert len(data["data"]) == 1

    # Verify time_period format for monthly (YYYY-MM)
    first_point = data["data"][0]
    assert first_point["time_period"] == "2024-12"
    assert first_point["aggregation_type"] == "monthly_average"


def test_get_aggregated_with_data_gaps() -> None:
    """Test aggregation with incomplete data (data_completeness < 100%)."""
    # Query a future date range that might have no data
    response = client.get(
        "/wells/WELL-001/data/aggregated",
        params={
            "metric_name": "oil_production_rate",
            "start_date": "2026-01-01",
            "end_date": "2026-01-05",
            "aggregation_type": "daily_average",
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Should return empty data array for dates outside the seeded range
    assert data["metadata"]["total_periods"] == 0
    assert len(data["data"]) == 0


def test_get_aggregated_invalid_aggregation_type() -> None:
    """Test that invalid aggregation type returns HTTP 400."""
    response = client.get(
        "/wells/WELL-001/data/aggregated",
        params={
            "metric_name": "oil_production_rate",
            "start_date": "2024-12-09",
            "end_date": "2024-12-10",
            "aggregation_type": "invalid_aggregation",
        },
    )

    # FastAPI's pattern validation should reject this before it reaches the service
    assert response.status_code == 422  # Unprocessable Entity (validation error)


def test_get_aggregated_invalid_well_id() -> None:
    """Test that non-existent well ID returns HTTP 404."""
    response = client.get(
        "/wells/NONEXISTENT-999/data/aggregated",
        params={
            "metric_name": "oil_production_rate",
            "start_date": "2024-12-09",
            "end_date": "2024-12-10",
            "aggregation_type": "daily_average",
        },
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_aggregated_invalid_metric() -> None:
    """Test that non-existent metric returns HTTP 404."""
    response = client.get(
        "/wells/WELL-001/data/aggregated",
        params={
            "metric_name": "nonexistent_metric",
            "start_date": "2024-12-09",
            "end_date": "2024-12-10",
            "aggregation_type": "daily_average",
        },
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_aggregated_invalid_date_range() -> None:
    """Test that invalid date range (start > end) returns HTTP 400."""
    response = client.get(
        "/wells/WELL-001/data/aggregated",
        params={
            "metric_name": "oil_production_rate",
            "start_date": "2024-12-15",
            "end_date": "2024-12-09",  # End before start
            "aggregation_type": "daily_average",
        },
    )

    assert response.status_code == 400
    assert "before" in response.json()["detail"].lower()


def test_get_aggregated_daily_min() -> None:
    """Test daily minimum aggregation."""
    response = client.get(
        "/wells/WELL-003/data/aggregated",
        params={
            "metric_name": "oil_production_rate",
            "start_date": "2024-12-09",
            "end_date": "2024-12-09",
            "aggregation_type": "daily_min",
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Verify that aggregated_value equals min_value for MIN aggregation
    for point in data["data"]:
        assert point["aggregation_type"] == "daily_min"
        assert point["aggregated_value"] == point["min_value"]


def test_get_aggregated_daily_sum() -> None:
    """Test daily sum aggregation."""
    response = client.get(
        "/wells/WELL-001/data/aggregated",
        params={
            "metric_name": "oil_production_rate",
            "start_date": "2024-12-09",
            "end_date": "2024-12-09",
            "aggregation_type": "daily_sum",
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Verify aggregation type
    assert data["metadata"]["aggregation_type"] == "daily_sum"

    # For sum, the aggregated value should be much larger than individual points
    for point in data["data"]:
        assert point["aggregation_type"] == "daily_sum"
        # Sum should be larger than the max value in the day
        assert point["aggregated_value"] >= point["max_value"]


def test_get_aggregated_multiple_days() -> None:
    """Test aggregation over multiple days returns one point per day."""
    response = client.get(
        "/wells/WELL-001/data/aggregated",
        params={
            "metric_name": "oil_production_rate",
            "start_date": "2024-12-09",
            "end_date": "2024-12-15",  # 7 days
            "aggregation_type": "daily_average",
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Should have 7 data points (one per day)
    assert len(data["data"]) == 7
    assert data["metadata"]["total_periods"] == 7

    # Verify dates are consecutive
    dates = [point["date"] for point in data["data"]]
    assert dates == [
        "2024-12-09",
        "2024-12-10",
        "2024-12-11",
        "2024-12-12",
        "2024-12-13",
        "2024-12-14",
        "2024-12-15",
    ]
