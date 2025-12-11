"""Unit tests for aggregation service."""

import sqlite3
from datetime import date

import pytest

from src import config
from src.models.aggregated import AggregationType
from src.services.aggregation import AggregationService


@pytest.fixture
def db_connection() -> sqlite3.Connection:
    """Get connection to the test database."""
    conn = sqlite3.connect(config.DATABASE_PATH)
    yield conn
    conn.close()


@pytest.fixture
def agg_service(db_connection: sqlite3.Connection) -> AggregationService:
    """Create aggregation service instance."""
    return AggregationService(db_connection)


def test_compute_daily_average(agg_service: AggregationService) -> None:
    """Test daily average aggregation computation."""
    results = agg_service.compute_daily_average(
        well_id="WELL-001",
        metric_name="oil_production_rate",
        start_date=date(2024, 12, 9),
        end_date=date(2024, 12, 11),
        unit="bbl/day",
    )

    # Should have 3 days of data
    assert len(results) == 3

    # Verify each result structure
    for result in results:
        assert result.well_id == "WELL-001"
        assert result.metric_name == "oil_production_rate"
        assert result.aggregation_type == AggregationType.DAILY_AVERAGE
        assert result.unit == "bbl/day"
        assert result.data_point_count > 0
        assert result.min_value <= result.aggregated_value <= result.max_value
        assert 0 <= result.data_completeness <= 100


def test_compute_daily_max(agg_service: AggregationService) -> None:
    """Test daily maximum aggregation computation."""
    results = agg_service.compute_daily_max(
        well_id="WELL-002",
        metric_name="wellhead_pressure",
        start_date=date(2024, 12, 9),
        end_date=date(2024, 12, 9),
        unit="psi",
    )

    assert len(results) == 1
    result = results[0]

    # For MAX aggregation, aggregated_value should equal max_value
    assert result.aggregated_value == result.max_value
    assert result.aggregation_type == AggregationType.DAILY_MAX


def test_compute_daily_min(agg_service: AggregationService) -> None:
    """Test daily minimum aggregation computation."""
    results = agg_service.compute_daily_min(
        well_id="WELL-003",
        metric_name="gas_production_rate",
        start_date=date(2024, 12, 9),
        end_date=date(2024, 12, 9),
        unit="mcf/day",
    )

    assert len(results) == 1
    result = results[0]

    # For MIN aggregation, aggregated_value should equal min_value
    assert result.aggregated_value == result.min_value
    assert result.aggregation_type == AggregationType.DAILY_MIN


def test_compute_daily_sum(agg_service: AggregationService) -> None:
    """Test daily sum aggregation computation."""
    results = agg_service.compute_daily_sum(
        well_id="WELL-001",
        metric_name="oil_production_rate",
        start_date=date(2024, 12, 9),
        end_date=date(2024, 12, 9),
        unit="bbl/day",
    )

    assert len(results) == 1
    result = results[0]

    # Sum should be much larger than individual max value
    assert result.aggregated_value >= result.max_value
    assert result.aggregation_type == AggregationType.DAILY_SUM


def test_compute_monthly_average(agg_service: AggregationService) -> None:
    """Test monthly average aggregation computation."""
    results = agg_service.compute_monthly_average(
        well_id="WELL-001",
        metric_name="oil_production_rate",
        start_date=date(2024, 12, 1),
        end_date=date(2024, 12, 31),
        unit="bbl/day",
    )

    # Should have 1 month (December)
    assert len(results) == 1
    result = results[0]

    # Verify monthly aggregation properties
    assert result.aggregation_type == AggregationType.MONTHLY_AVERAGE
    assert result.time_period == "2024-12"
    assert result.data_point_count > 0
    assert result.min_value <= result.aggregated_value <= result.max_value


def test_empty_date_range(agg_service: AggregationService) -> None:
    """Test aggregation with no data in date range."""
    results = agg_service.compute_daily_average(
        well_id="WELL-001",
        metric_name="oil_production_rate",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 5),
        unit="bbl/day",
    )

    # Should return empty list for dates outside seeded range
    assert len(results) == 0


def test_multiple_months(agg_service: AggregationService) -> None:
    """Test monthly aggregation across multiple months."""
    results = agg_service.compute_monthly_average(
        well_id="WELL-002",
        metric_name="wellhead_pressure",
        start_date=date(2024, 11, 1),
        end_date=date(2025, 1, 31),
        unit="psi",
    )

    # Should have results for November, December, January (if data exists)
    assert len(results) >= 1

    # Verify months are in order
    time_periods = [r.time_period for r in results]
    assert time_periods == sorted(time_periods)


def test_data_completeness_calculation(agg_service: AggregationService) -> None:
    """Test that data completeness is calculated correctly."""
    results = agg_service.compute_daily_average(
        well_id="WELL-001",
        metric_name="oil_production_rate",
        start_date=date(2024, 12, 9),
        end_date=date(2024, 12, 9),
        unit="bbl/day",
    )

    assert len(results) == 1
    result = results[0]

    # For a full day with minute-level data, should have close to 1440 points
    # Data completeness should be high
    assert result.data_point_count > 1000  # Should be close to 1440
    assert result.data_completeness > 90.0  # Should be > 90%


def test_aggregated_value_within_min_max(agg_service: AggregationService) -> None:
    """Test that aggregated values are within min/max bounds."""
    results = agg_service.compute_daily_average(
        well_id="WELL-003",
        metric_name="gas_production_rate",
        start_date=date(2024, 12, 9),
        end_date=date(2024, 12, 15),
        unit="mcf/day",
    )

    for result in results:
        # Average should be between min and max
        assert result.min_value <= result.aggregated_value <= result.max_value


def test_date_ordering(agg_service: AggregationService) -> None:
    """Test that results are ordered by date."""
    results = agg_service.compute_daily_average(
        well_id="WELL-001",
        metric_name="oil_production_rate",
        start_date=date(2024, 12, 9),
        end_date=date(2024, 12, 20),
        unit="bbl/day",
    )

    # Dates should be in ascending order
    dates = [r.date for r in results]
    assert dates == sorted(dates)


def test_different_wells_different_results(agg_service: AggregationService) -> None:
    """Test that different wells produce different aggregated results."""
    results_well1 = agg_service.compute_daily_average(
        well_id="WELL-001",
        metric_name="oil_production_rate",
        start_date=date(2024, 12, 9),
        end_date=date(2024, 12, 9),
        unit="bbl/day",
    )

    results_well2 = agg_service.compute_daily_average(
        well_id="WELL-002",
        metric_name="oil_production_rate",
        start_date=date(2024, 12, 9),
        end_date=date(2024, 12, 9),
        unit="bbl/day",
    )

    assert len(results_well1) == 1
    assert len(results_well2) == 1

    # Different wells should have different aggregated values
    assert results_well1[0].aggregated_value != results_well2[0].aggregated_value
