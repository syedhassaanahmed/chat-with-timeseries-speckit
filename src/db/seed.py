"""Database seed script for Oil Well Time Series API.

Initializes SQLite database and populates with synthetic time-series data.
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import DATABASE_PATH
from src.db.database import init_database
from src.services.data_generator import SyntheticDataGenerator


def check_if_data_exists() -> bool:
    """Check if the database already contains seeded data.

    Returns:
        True if data exists, False otherwise
    """
    if not DATABASE_PATH.exists():
        return False

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Check if timeseries_data table has any rows
        cursor.execute("SELECT COUNT(*) FROM timeseries_data")
        count = cursor.fetchone()[0]
        return count > 0
    except sqlite3.OperationalError:
        # Table doesn't exist yet
        return False
    finally:
        conn.close()


def seed_database() -> None:
    """Seed the database with synthetic well data, metrics, and time-series data."""
    print("=" * 60)
    print("Oil Well Time Series API - Database Seeding")
    print("=" * 60)
    print()

    # Check if data already exists
    if check_if_data_exists():
        print("ℹ️  Database already contains data. Skipping seeding.")
        print(f"   Database location: {DATABASE_PATH}")
        print(f"   Database size: {DATABASE_PATH.stat().st_size / (1024**3):.2f} GB")
        print()
        print("   To reseed, delete the database file and run this script again:")
        print(f"   rm {DATABASE_PATH}")
        print()
        return

    # Initialize database schema
    print("📋 Step 1/4: Initializing database schema...")
    init_database()
    print("✓ Schema created")
    print()

    # Create data generator
    generator = SyntheticDataGenerator(seed=42)

    # Generate and insert wells
    print("🏭 Step 2/4: Generating well metadata...")
    wells = generator.generate_well_metadata()
    seed_wells(wells)
    print(f"✓ Inserted {len(wells)} wells")
    print()

    # Generate and insert metrics
    print("📊 Step 3/4: Generating metric definitions...")
    metrics = generator.generate_metric_definitions()
    seed_metrics(metrics)
    print(f"✓ Inserted {len(metrics)} metrics")
    print()

    # Generate and insert time-series data
    print("⏱️  Step 4/4: Generating time-series data...")
    print("⚠️  This may take several minutes (~7.9M rows)...")
    df_timeseries = generator.generate_timeseries_data(wells, metrics)
    seed_timeseries_data(df_timeseries)
    print(f"✓ Inserted {len(df_timeseries):,} data points")
    print()

    # Verify indexes
    verify_indexes()

    print("=" * 60)
    print("✅ Database seeding complete!")
    print("=" * 60)
    print(f"Database location: {DATABASE_PATH}")
    print(f"Database size: {DATABASE_PATH.stat().st_size / (1024**3):.2f} GB")
    print()


def seed_wells(wells: list[dict]) -> None:
    """Insert well metadata into the database.

    Args:
        wells: List of well metadata dictionaries
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    for well in wells:
        cursor.execute(
            """
            INSERT OR REPLACE INTO wells (
                well_id, well_name, latitude, longitude, operator,
                field_name, well_type, spud_date, data_start_date, data_end_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                well["well_id"],
                well["well_name"],
                well["latitude"],
                well["longitude"],
                well["operator"],
                well["field_name"],
                well["well_type"],
                well["spud_date"].isoformat(),
                well["data_start_date"].isoformat(),
                well["data_end_date"].isoformat(),
            ),
        )

    conn.commit()
    conn.close()


def seed_metrics(metrics: list[dict]) -> None:
    """Insert metric definitions into the database.

    Args:
        metrics: List of metric definition dictionaries
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    for metric in metrics:
        cursor.execute(
            """
            INSERT OR REPLACE INTO metrics (
                metric_name, display_name, description,
                unit_of_measurement, data_type, typical_min, typical_max
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                metric["metric_name"],
                metric["display_name"],
                metric["description"],
                metric["unit_of_measurement"],
                metric["data_type"],
                metric["typical_min"],
                metric["typical_max"],
            ),
        )

    conn.commit()
    conn.close()


def seed_timeseries_data(df) -> None:
    """Insert time-series data into the database.

    Args:
        df: DataFrame with columns: timestamp, well_id, metric_name, value, quality_flag
    """
    conn = sqlite3.connect(DATABASE_PATH)

    # Insert in batches for better performance
    batch_size = 10000
    total_rows = len(df)

    for start_idx in range(0, total_rows, batch_size):
        end_idx = min(start_idx + batch_size, total_rows)
        batch = df.iloc[start_idx:end_idx]

        batch.to_sql(
            "timeseries_data",
            conn,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1000,
        )

        # Progress logging
        progress = (end_idx / total_rows) * 100
        print(f"  Progress: {progress:.1f}% ({end_idx:,}/{total_rows:,} rows)", end="\r")

    print()  # New line after progress
    conn.close()


def verify_indexes() -> None:
    """Verify that database indexes were created correctly."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA index_list('timeseries_data')")
    indexes = cursor.fetchall()

    print("🔍 Verifying indexes...")
    expected_indexes = ["idx_well_metric_time", "idx_timestamp", "idx_quality_flag"]

    for expected in expected_indexes:
        found = any(expected in str(idx) for idx in indexes)
        status = "✓" if found else "✗"
        print(f"  {status} {expected}")

    conn.close()


if __name__ == "__main__":
    try:
        seed_database()
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
