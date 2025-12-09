"""Query service for Oil Well Time Series API.

Handles business logic for querying wells, metrics, and time-series data.
"""

import sqlite3
from datetime import datetime
from typing import Any

from src.models.metric import Metric
from src.models.timeseries import TimeSeriesDataPoint
from src.models.well import Well


class QueryService:
    """Service for querying time-series data and metadata."""

    def get_raw_timeseries(
        self,
        db: sqlite3.Connection,
        well_id: str,
        metric_name: str,
        start_timestamp: datetime,
        end_timestamp: datetime,
    ) -> dict[str, Any]:
        """Query raw time-series data for a specific well and metric.

        Args:
            db: Database connection
            well_id: Well identifier (e.g., "WELL-001")
            metric_name: Metric identifier (e.g., "oil_production_rate")
            start_timestamp: Start of time range (ISO 8601 UTC)
            end_timestamp: End of time range (ISO 8601 UTC)

        Returns:
            Dictionary with 'data' (list of TimeSeriesDataPoint) and 'metadata'

        Raises:
            ValueError: If well_id or metric_name doesn't exist
            ValueError: If timestamp range is invalid
        """
        # Validate inputs
        self._validate_well_exists(db, well_id)
        self._validate_metric_exists(db, metric_name)
        self._validate_timestamp_range(start_timestamp, end_timestamp)

        # Query time-series data
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT timestamp, well_id, metric_name, value, quality_flag
            FROM timeseries_data
            WHERE well_id = ? 
              AND metric_name = ?
              AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp
            """,
            (
                well_id,
                metric_name,
                start_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                end_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
            ),
        )

        rows = cursor.fetchall()

        # Get unit for this metric
        cursor.execute(
            "SELECT unit_of_measurement FROM metrics WHERE metric_name = ?", (metric_name,)
        )
        unit_row = cursor.fetchone()
        unit = unit_row[0] if unit_row else "unknown"

        # Convert rows to TimeSeriesDataPoint objects
        data_points = []
        for row in rows:
            data_points.append(
                TimeSeriesDataPoint(
                    timestamp=datetime.fromisoformat(row[0].replace("Z", "+00:00")),
                    well_id=row[1],
                    metric_name=row[2],
                    value=row[3],
                    unit=unit,
                    quality_flag=row[4],
                )
            )

        # Calculate metadata
        metadata = self._calculate_raw_data_metadata(
            well_id, metric_name, start_timestamp, end_timestamp, data_points
        )

        return {"data": data_points, "metadata": metadata}

    def get_all_wells(self, db: sqlite3.Connection) -> list[Well]:
        """Get all wells from the database.

        Args:
            db: Database connection

        Returns:
            List of Well objects
        """
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT well_id, well_name, latitude, longitude, operator,
                   field_name, well_type, spud_date, data_start_date, data_end_date
            FROM wells
            ORDER BY well_id
            """
        )

        wells = []
        for row in cursor.fetchall():
            wells.append(
                Well(
                    well_id=row[0],
                    well_name=row[1],
                    latitude=row[2],
                    longitude=row[3],
                    operator=row[4],
                    field_name=row[5],
                    well_type=row[6],
                    spud_date=row[7],
                    data_start_date=row[8],
                    data_end_date=row[9],
                )
            )

        return wells

    def get_well_by_id(self, db: sqlite3.Connection, well_id: str) -> Well | None:
        """Get a single well by ID.

        Args:
            db: Database connection
            well_id: Well identifier

        Returns:
            Well object or None if not found
        """
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT well_id, well_name, latitude, longitude, operator,
                   field_name, well_type, spud_date, data_start_date, data_end_date
            FROM wells
            WHERE well_id = ?
            """,
            (well_id,),
        )

        row = cursor.fetchone()
        if not row:
            return None

        return Well(
            well_id=row[0],
            well_name=row[1],
            latitude=row[2],
            longitude=row[3],
            operator=row[4],
            field_name=row[5],
            well_type=row[6],
            spud_date=row[7],
            data_start_date=row[8],
            data_end_date=row[9],
        )

    def get_all_metrics(self, db: sqlite3.Connection) -> list[Metric]:
        """Get all metrics from the database.

        Args:
            db: Database connection

        Returns:
            List of Metric objects
        """
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT metric_name, display_name, description,
                   unit_of_measurement, data_type, typical_min, typical_max
            FROM metrics
            ORDER BY metric_name
            """
        )

        metrics = []
        for row in cursor.fetchall():
            metrics.append(
                Metric(
                    metric_name=row[0],
                    display_name=row[1],
                    description=row[2],
                    unit_of_measurement=row[3],
                    data_type=row[4],
                    typical_min=row[5],
                    typical_max=row[6],
                )
            )

        return metrics

    def _validate_well_exists(self, db: sqlite3.Connection, well_id: str) -> None:
        """Validate that a well exists in the database.

        Args:
            db: Database connection
            well_id: Well identifier

        Raises:
            ValueError: If well doesn't exist
        """
        cursor = db.cursor()
        cursor.execute("SELECT 1 FROM wells WHERE well_id = ?", (well_id,))
        if not cursor.fetchone():
            raise ValueError(f"Well not found: {well_id}")

    def _validate_metric_exists(self, db: sqlite3.Connection, metric_name: str) -> None:
        """Validate that a metric exists in the database.

        Args:
            db: Database connection
            metric_name: Metric identifier

        Raises:
            ValueError: If metric doesn't exist
        """
        cursor = db.cursor()
        cursor.execute("SELECT 1 FROM metrics WHERE metric_name = ?", (metric_name,))
        if not cursor.fetchone():
            raise ValueError(f"Metric not found: {metric_name}")

    def _validate_timestamp_range(
        self, start_timestamp: datetime, end_timestamp: datetime
    ) -> None:
        """Validate that timestamp range is valid.

        Args:
            start_timestamp: Start of time range
            end_timestamp: End of time range

        Raises:
            ValueError: If range is invalid
        """
        if start_timestamp >= end_timestamp:
            raise ValueError("start_timestamp must be before end_timestamp")

    def _calculate_raw_data_metadata(
        self,
        well_id: str,
        metric_name: str,
        start_timestamp: datetime,
        end_timestamp: datetime,
        data_points: list[TimeSeriesDataPoint],
    ) -> dict[str, Any]:
        """Calculate metadata for raw time-series query response.

        Args:
            well_id: Well identifier
            metric_name: Metric identifier
            start_timestamp: Start of time range
            end_timestamp: End of time range
            data_points: List of data points returned

        Returns:
            Dictionary with metadata fields
        """
        total_points = len(data_points)

        # Calculate expected points (minute-level granularity)
        time_diff = end_timestamp - start_timestamp
        expected_points = int(time_diff.total_seconds() / 60) + 1

        # Calculate data completeness
        data_completeness = (
            (total_points / expected_points * 100) if expected_points > 0 else 0.0
        )

        return {
            "well_id": well_id,
            "metric_name": metric_name,
            "start_timestamp": start_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end_timestamp": end_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_points": total_points,
            "data_completeness": round(data_completeness, 2),
        }
