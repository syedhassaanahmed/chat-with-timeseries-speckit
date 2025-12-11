"""Unit tests for QueryService with mock database."""

from datetime import UTC, datetime

import pytest

from src.services.query_service import QueryService


@pytest.fixture
def query_service() -> QueryService:
    """Create QueryService instance."""
    return QueryService()


def test_validate_timestamp_range_success(query_service: QueryService) -> None:
    """Test that valid timestamp range passes validation."""
    start = datetime(2024, 1, 1, tzinfo=UTC)
    end = datetime(2024, 1, 2, tzinfo=UTC)

    # Should not raise
    query_service._validate_timestamp_range(start, end)


def test_validate_timestamp_range_invalid_order(query_service: QueryService) -> None:
    """Test that start > end raises ValueError."""
    start = datetime(2024, 1, 2, tzinfo=UTC)
    end = datetime(2024, 1, 1, tzinfo=UTC)

    with pytest.raises(ValueError, match="start_timestamp must be before end_timestamp"):
        query_service._validate_timestamp_range(start, end)


def test_calculate_raw_data_metadata_with_data(query_service: QueryService) -> None:
    """Test metadata calculation with actual data points."""
    from src.models.timeseries import TimeSeriesDataPoint

    start = datetime(2024, 12, 9, 0, 0, 0, tzinfo=UTC)
    end = datetime(2024, 12, 9, 0, 10, 0, tzinfo=UTC)  # 11 expected points

    # Create 10 data points (90.9% completeness)
    data_points = [
        TimeSeriesDataPoint(
            timestamp=datetime(2024, 12, 9, 0, i, 0, tzinfo=UTC),
            well_id="WELL-001",
            metric_name="oil_production_rate",
            value=245.0 + i,
            unit="bbl/day",
            quality_flag="good",
        )
        for i in range(10)
    ]

    metadata = query_service._calculate_raw_data_metadata(
        "WELL-001", "oil_production_rate", start, end, data_points
    )

    assert metadata["well_id"] == "WELL-001"
    assert metadata["metric_name"] == "oil_production_rate"
    assert metadata["total_points"] == 10
    assert 90.0 <= metadata["data_completeness"] <= 91.0


def test_calculate_raw_data_metadata_empty(query_service: QueryService) -> None:
    """Test metadata calculation with no data points."""
    start = datetime(2024, 12, 9, 0, 0, 0, tzinfo=UTC)
    end = datetime(2024, 12, 9, 1, 0, 0, tzinfo=UTC)

    metadata = query_service._calculate_raw_data_metadata(
        "WELL-001", "oil_production_rate", start, end, []
    )

    assert metadata["total_points"] == 0
    assert metadata["data_completeness"] == 0.0


def test_calculate_raw_data_metadata_full_completeness(query_service: QueryService) -> None:
    """Test metadata calculation with 100% data completeness."""
    from src.models.timeseries import TimeSeriesDataPoint

    start = datetime(2024, 12, 9, 0, 0, 0, tzinfo=UTC)
    end = datetime(2024, 12, 9, 0, 10, 0, tzinfo=UTC)  # 11 expected points

    # Create all 11 expected data points
    data_points = [
        TimeSeriesDataPoint(
            timestamp=datetime(2024, 12, 9, 0, i, 0, tzinfo=UTC),
            well_id="WELL-001",
            metric_name="oil_production_rate",
            value=245.0 + i,
            unit="bbl/day",
            quality_flag="good",
        )
        for i in range(11)
    ]

    metadata = query_service._calculate_raw_data_metadata(
        "WELL-001", "oil_production_rate", start, end, data_points
    )

    assert metadata["total_points"] == 11
    assert metadata["data_completeness"] == 100.0


def test_validate_date_range_success(query_service: QueryService) -> None:
    """Test that valid date range passes validation."""
    from datetime import date

    start = date(2024, 1, 1)
    end = date(2024, 1, 31)

    # Should not raise
    query_service._validate_date_range(start, end)


def test_validate_date_range_invalid_order(query_service: QueryService) -> None:
    """Test that start > end raises ValueError."""
    from datetime import date

    start = date(2024, 1, 31)
    end = date(2024, 1, 1)

    with pytest.raises(ValueError, match="start_date must be before or equal to end_date"):
        query_service._validate_date_range(start, end)
