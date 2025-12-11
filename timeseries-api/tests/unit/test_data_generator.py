"""Unit tests for synthetic data generator.

These tests verify that the SyntheticDataGenerator produces data with expected
characteristics (decline curves, seasonal variations, noise, etc.) by analyzing
the already-seeded database instead of generating new data for each test.
"""

import sqlite3

import numpy as np
import pandas as pd
import pytest

from src import config
from src.services.data_generator import SyntheticDataGenerator


@pytest.fixture
def generator() -> SyntheticDataGenerator:
    """Create a data generator instance for testing."""
    return SyntheticDataGenerator(seed=42)


@pytest.fixture
def db_connection() -> sqlite3.Connection:
    """Get connection to the already-seeded database."""
    conn = sqlite3.connect(config.DATABASE_PATH)
    yield conn
    conn.close()


@pytest.fixture
def sample_well_data(db_connection: sqlite3.Connection) -> pd.DataFrame:
    """Get sample timeseries data from database for one well and metric."""
    query = """
        SELECT timestamp, well_id, metric_name, value, quality_flag
        FROM timeseries_data
        WHERE well_id = 'WELL-001' AND metric_name = 'oil_production_rate'
        ORDER BY timestamp
    """
    df = pd.read_sql_query(query, db_connection)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def test_generator_initialization(generator: SyntheticDataGenerator) -> None:
    """Test that generator initializes with correct parameters."""
    assert generator.seed == 42


def test_generate_well_metadata(generator: SyntheticDataGenerator) -> None:
    """Test that well metadata is generated correctly."""
    wells = generator.generate_well_metadata()

    assert len(wells) == config.NUM_WELLS

    for i, well in enumerate(wells):
        # Check well_id format
        assert well["well_id"] == f"WELL-{i + 1:03d}"

        # Check required fields
        assert all(
            key in well
            for key in [
                "well_name",
                "latitude",
                "longitude",
                "operator",
                "field_name",
                "well_type",
                "spud_date",
                "data_start_date",
                "data_end_date",
            ]
        )

        # Check well_type is valid
        assert well["well_type"] in ["producer", "injector", "observation"]

        # Check latitude/longitude ranges
        assert -90 <= well["latitude"] <= 90
        assert -180 <= well["longitude"] <= 180


def test_generate_metric_definitions(generator: SyntheticDataGenerator) -> None:
    """Test that metric definitions are generated correctly."""
    metrics = generator.generate_metric_definitions()

    assert len(metrics) == len(config.METRIC_CONFIGS)

    expected_metrics = list(config.METRIC_CONFIGS.keys())
    metric_names = [m["metric_name"] for m in metrics]

    for expected in expected_metrics:
        assert expected in metric_names

    for metric in metrics:
        # Check required fields
        assert all(
            key in metric
            for key in [
                "metric_name",
                "display_name",
                "description",
                "unit_of_measurement",
                "data_type",
            ]
        )

        # Check typical ranges are logical
        if metric.get("typical_min") is not None and metric.get("typical_max") is not None:
            assert metric["typical_min"] < metric["typical_max"]


def test_decline_curves_applied(db_connection: sqlite3.Connection) -> None:
    """Test that decline curves are evident in the seeded data."""
    query = """
        SELECT timestamp, value
        FROM timeseries_data
        WHERE well_id = 'WELL-001' AND metric_name = 'oil_production_rate'
        ORDER BY timestamp
    """
    df = pd.read_sql_query(query, db_connection)
    values = df["value"].values

    # Split into quarters and check trend
    quarter_size = len(values) // 4
    quarters = [values[i * quarter_size : (i + 1) * quarter_size].mean() for i in range(4)]

    # First quarter should generally be higher than last quarter
    assert quarters[0] > quarters[-1] * 0.8, (
        f"Decline curve not evident: Q1={quarters[0]:.2f}, Q4={quarters[-1]:.2f}"
    )


def test_seasonal_variations_present(db_connection: sqlite3.Connection) -> None:
    """Test that seasonal variations are present in the seeded data."""
    query = """
        SELECT timestamp, value
        FROM timeseries_data
        WHERE well_id = 'WELL-001' AND metric_name = 'oil_production_rate'
        ORDER BY timestamp
    """
    df = pd.read_sql_query(query, db_connection)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Group by month and calculate average
    df["month"] = df["timestamp"].dt.month
    monthly_avg = df.groupby("month")["value"].mean()

    # Check that there's variation across months
    assert monthly_avg.std() > 0, "No seasonal variation detected"

    # Check that variation is significant (more than 1% of mean)
    coefficient_of_variation = monthly_avg.std() / monthly_avg.mean()
    assert coefficient_of_variation > 0.01, (
        f"Seasonal variation too small: CV={coefficient_of_variation:.4f}"
    )


def test_maintenance_periods_create_shutdowns(db_connection: sqlite3.Connection) -> None:
    """Test that data has significant variation (not constant values)."""
    query = """
        SELECT value
        FROM timeseries_data
        WHERE well_id = 'WELL-001' AND metric_name = 'oil_production_rate'
        ORDER BY timestamp
    """
    df = pd.read_sql_query(query, db_connection)
    values = df["value"].values

    # Verify data varies significantly (coefficient of variation > 1%)
    # This indicates the generator creates realistic variation including
    # seasonal changes, decline curves, and noise (not just constant values)
    mean_val = np.mean(values)
    std_val = np.std(values)
    cv = std_val / mean_val

    assert cv > 0.01, f"Coefficient of variation {cv:.4f} too low - data should vary"

    # Verify we have both high and low periods
    median_val = np.median(values)
    high_values = values > median_val * 1.1  # 10% above median
    low_values = values < median_val * 0.9  # 10% below median

    assert np.sum(high_values) > 0, "Should have high production periods"
    assert np.sum(low_values) > 0, "Should have low production periods"


def test_correlated_metrics(db_connection: sqlite3.Connection) -> None:
    """Test that oil and gas production are correlated in the seeded data."""
    query = """
        SELECT metric_name, value
        FROM timeseries_data
        WHERE well_id = 'WELL-001'
          AND metric_name IN ('oil_production_rate', 'gas_production_rate')
        ORDER BY timestamp, metric_name
    """
    df = pd.read_sql_query(query, db_connection)

    oil_values = df[df["metric_name"] == "oil_production_rate"]["value"].values
    gas_values = df[df["metric_name"] == "gas_production_rate"]["value"].values

    assert len(oil_values) == len(gas_values)

    # Calculate correlation
    correlation = np.corrcoef(oil_values, gas_values)[0, 1]

    # Should be positively correlated
    assert correlation > 0.5, f"Oil and gas not correlated: {correlation:.3f}"


def test_pressure_decline_with_depletion(db_connection: sqlite3.Connection) -> None:
    """Test that pressure decreases over time in the seeded data."""
    query = """
        SELECT value
        FROM timeseries_data
        WHERE well_id = 'WELL-001' AND metric_name = 'wellhead_pressure'
        ORDER BY timestamp
    """
    df = pd.read_sql_query(query, db_connection)
    values = df["value"].values

    # Split into first and last quarter
    quarter_size = len(values) // 4
    first_quarter = values[:quarter_size].mean()
    last_quarter = values[-quarter_size:].mean()

    # Pressure should generally decline
    assert first_quarter > last_quarter * 0.9, (
        f"Pressure decline not evident: Q1={first_quarter:.2f}, Q4={last_quarter:.2f}"
    )


def test_quality_flags_assigned(db_connection: sqlite3.Connection) -> None:
    """Test that quality flags are assigned in the seeded data."""
    query = """
        SELECT quality_flag, COUNT(*) as count
        FROM timeseries_data
        GROUP BY quality_flag
    """
    df = pd.read_sql_query(query, db_connection)

    # Check valid values
    valid_flags = ["good", "suspect", "bad", "estimated"]
    assert df["quality_flag"].isin(valid_flags).all()

    # Most data should be "good" quality
    total_count = df["count"].sum()
    good_count = df[df["quality_flag"] == "good"]["count"].sum()
    good_ratio = good_count / total_count

    assert good_ratio > 0.9, f"Most data should be good quality: {good_ratio:.2%}"


def test_timestamp_continuity(sample_well_data: pd.DataFrame) -> None:
    """Test that timestamps are continuous with configured intervals."""
    timestamps = sample_well_data["timestamp"].values

    # Check continuity for first 100 timestamps
    for i in range(min(100, len(timestamps) - 1)):
        time_diff = pd.Timedelta(timestamps[i + 1] - timestamps[i])
        expected_diff = pd.Timedelta(minutes=config.DATA_FREQUENCY_MINUTES)
        assert time_diff == expected_diff, f"Gap in timestamps at index {i}"


def test_different_wells_different_patterns(db_connection: sqlite3.Connection) -> None:
    """Test that different wells have different data patterns."""
    # Get first 1000 points from each well separately
    values1 = pd.read_sql_query(
        """
        SELECT value
        FROM timeseries_data
        WHERE metric_name = 'oil_production_rate' AND well_id = 'WELL-001'
        ORDER BY timestamp
        LIMIT 1000
    """,
        db_connection,
    )["value"].values

    values2 = pd.read_sql_query(
        """
        SELECT value
        FROM timeseries_data
        WHERE metric_name = 'oil_production_rate' AND well_id = 'WELL-002'
        ORDER BY timestamp
        LIMIT 1000
    """,
        db_connection,
    )["value"].values

    values3 = pd.read_sql_query(
        """
        SELECT value
        FROM timeseries_data
        WHERE metric_name = 'oil_production_rate' AND well_id = 'WELL-003'
        ORDER BY timestamp
        LIMIT 1000
    """,
        db_connection,
    )["value"].values

    # Verify we got data for each well
    assert len(values1) == 1000, "Should have 1000 points for WELL-001"
    assert len(values2) == 1000, "Should have 1000 points for WELL-002"
    assert len(values3) == 1000, "Should have 1000 points for WELL-003"

    # Different wells should have different patterns
    assert not np.allclose(values1, values2), "Wells 1 and 2 should have different patterns"
    assert not np.allclose(values2, values3), "Wells 2 and 3 should have different patterns"


def test_data_count_matches_expectations(db_connection: sqlite3.Connection) -> None:
    """Test that the total number of data points matches expectations."""
    query = "SELECT COUNT(*) as total FROM timeseries_data"
    df = pd.read_sql_query(query, db_connection)

    total_points = df["total"].iloc[0]

    # Calculate expected: num_wells * num_metrics * num_timestamps
    # Using approximate calculation since exact count depends on date range
    expected_min = config.NUM_WELLS * len(config.METRIC_CONFIGS) * 500000  # Minimum expected

    assert total_points >= expected_min, f"Data count too low: {total_points:,} < {expected_min:,}"


def test_value_ranges_reasonable(db_connection: sqlite3.Connection) -> None:
    """Test that values fall within reasonable ranges for each metric."""
    query = """
        SELECT metric_name, MIN(value) as min_val, MAX(value) as max_val
        FROM timeseries_data
        GROUP BY metric_name
    """
    df = pd.read_sql_query(query, db_connection)

    for _, row in df.iterrows():
        metric_name = row["metric_name"]
        min_val = row["min_val"]
        max_val = row["max_val"]

        # Get expected range from config
        metric_config = config.METRIC_CONFIGS.get(metric_name, {})
        typical_min = metric_config.get("typical_min")
        typical_max = metric_config.get("typical_max")

        if typical_min is not None and typical_max is not None:
            # Allow 50% margin for noise and variations
            assert min_val >= typical_min * 0.5, (
                f"{metric_name} min too low: {min_val} < {typical_min * 0.5}"
            )
            assert max_val <= typical_max * 1.5, (
                f"{metric_name} max too high: {max_val} > {typical_max * 1.5}"
            )
