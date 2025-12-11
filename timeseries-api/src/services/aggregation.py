"""Aggregation service for computing time-series summaries."""

import sqlite3
from datetime import date, datetime
from typing import Literal

from src.models.aggregated import AggregatedDataPoint, AggregationType


class AggregationService:
    """Service for computing aggregated time-series data summaries.

    Provides methods to compute daily and monthly aggregations (average,
    max, min, sum) from raw minute-level time-series data.
    """

    def __init__(self, db_connection: sqlite3.Connection) -> None:
        """Initialize aggregation service with database connection.

        Args:
            db_connection: SQLite database connection
        """
        self.db_connection = db_connection

    def compute_daily_average(
        self,
        well_id: str,
        metric_name: str,
        start_date: date,
        end_date: date,
        unit: str,
    ) -> list[AggregatedDataPoint]:
        """Compute daily average values for a metric.

        Args:
            well_id: Well identifier
            metric_name: Metric identifier
            start_date: Start date for aggregation
            end_date: End date for aggregation
            unit: Unit of measurement for the metric

        Returns:
            List of aggregated data points, one per day
        """
        return self._compute_daily_aggregation(
            well_id=well_id,
            metric_name=metric_name,
            start_date=start_date,
            end_date=end_date,
            unit=unit,
            aggregation_func="AVG",
            aggregation_type=AggregationType.DAILY_AVERAGE,
        )

    def compute_daily_max(
        self,
        well_id: str,
        metric_name: str,
        start_date: date,
        end_date: date,
        unit: str,
    ) -> list[AggregatedDataPoint]:
        """Compute daily maximum values for a metric.

        Args:
            well_id: Well identifier
            metric_name: Metric identifier
            start_date: Start date for aggregation
            end_date: End date for aggregation
            unit: Unit of measurement for the metric

        Returns:
            List of aggregated data points, one per day
        """
        return self._compute_daily_aggregation(
            well_id=well_id,
            metric_name=metric_name,
            start_date=start_date,
            end_date=end_date,
            unit=unit,
            aggregation_func="MAX",
            aggregation_type=AggregationType.DAILY_MAX,
        )

    def compute_daily_min(
        self,
        well_id: str,
        metric_name: str,
        start_date: date,
        end_date: date,
        unit: str,
    ) -> list[AggregatedDataPoint]:
        """Compute daily minimum values for a metric.

        Args:
            well_id: Well identifier
            metric_name: Metric identifier
            start_date: Start date for aggregation
            end_date: End date for aggregation
            unit: Unit of measurement for the metric

        Returns:
            List of aggregated data points, one per day
        """
        return self._compute_daily_aggregation(
            well_id=well_id,
            metric_name=metric_name,
            start_date=start_date,
            end_date=end_date,
            unit=unit,
            aggregation_func="MIN",
            aggregation_type=AggregationType.DAILY_MIN,
        )

    def compute_daily_sum(
        self,
        well_id: str,
        metric_name: str,
        start_date: date,
        end_date: date,
        unit: str,
    ) -> list[AggregatedDataPoint]:
        """Compute daily sum of values for a metric.

        Args:
            well_id: Well identifier
            metric_name: Metric identifier
            start_date: Start date for aggregation
            end_date: End date for aggregation
            unit: Unit of measurement for the metric

        Returns:
            List of aggregated data points, one per day
        """
        return self._compute_daily_aggregation(
            well_id=well_id,
            metric_name=metric_name,
            start_date=start_date,
            end_date=end_date,
            unit=unit,
            aggregation_func="SUM",
            aggregation_type=AggregationType.DAILY_SUM,
        )

    def compute_monthly_average(
        self,
        well_id: str,
        metric_name: str,
        start_date: date,
        end_date: date,
        unit: str,
    ) -> list[AggregatedDataPoint]:
        """Compute monthly average values for a metric.

        Args:
            well_id: Well identifier
            metric_name: Metric identifier
            start_date: Start date for aggregation
            end_date: End date for aggregation
            unit: Unit of measurement for the metric

        Returns:
            List of aggregated data points, one per month
        """
        query = """
            SELECT
                DATE(timestamp, 'start of month') as period_date,
                STRFTIME('%Y-%m', timestamp) as time_period,
                AVG(value) as aggregated_value,
                COUNT(*) as data_point_count,
                MIN(value) as min_value,
                MAX(value) as max_value
            FROM timeseries_data
            WHERE well_id = ?
              AND metric_name = ?
              AND DATE(timestamp) >= DATE(?)
              AND DATE(timestamp) <= DATE(?)
            GROUP BY STRFTIME('%Y-%m', timestamp)
            ORDER BY period_date
        """

        cursor = self.db_connection.cursor()
        cursor.execute(
            query,
            (well_id, metric_name, start_date.isoformat(), end_date.isoformat()),
        )

        results = []
        for row in cursor.fetchall():
            period_date_str, time_period, agg_val, count, min_val, max_val = row

            # Calculate data completeness
            # For monthly: expected points = days_in_month * 24 hours * 60 minutes
            period_date = datetime.strptime(period_date_str, "%Y-%m-%d").date()

            # Calculate days in month
            if period_date.month == 12:
                next_month = period_date.replace(year=period_date.year + 1, month=1, day=1)
            else:
                next_month = period_date.replace(month=period_date.month + 1, day=1)
            days_in_month = (next_month - period_date.replace(day=1)).days

            expected_points = days_in_month * 24 * 60
            data_completeness = (count / expected_points) * 100 if expected_points > 0 else 0.0

            results.append(
                AggregatedDataPoint(
                    date=period_date,
                    time_period=time_period,
                    well_id=well_id,
                    metric_name=metric_name,
                    aggregated_value=agg_val,
                    aggregation_type=AggregationType.MONTHLY_AVERAGE,
                    unit=unit,
                    data_point_count=count,
                    min_value=min_val,
                    max_value=max_val,
                    data_completeness=round(data_completeness, 2),
                )
            )

        cursor.close()
        return results

    def _compute_daily_aggregation(
        self,
        well_id: str,
        metric_name: str,
        start_date: date,
        end_date: date,
        unit: str,
        aggregation_func: Literal["AVG", "MAX", "MIN", "SUM"],
        aggregation_type: AggregationType,
    ) -> list[AggregatedDataPoint]:
        """Internal method to compute daily aggregations using SQL.

        Args:
            well_id: Well identifier
            metric_name: Metric identifier
            start_date: Start date for aggregation
            end_date: End date for aggregation
            unit: Unit of measurement
            aggregation_func: SQL aggregation function (AVG, MAX, MIN, SUM)
            aggregation_type: Type of aggregation for the response

        Returns:
            List of aggregated data points, one per day
        """
        query = f"""
            SELECT
                DATE(timestamp) as period_date,
                DATE(timestamp) as time_period,
                {aggregation_func}(value) as aggregated_value,
                COUNT(*) as data_point_count,
                MIN(value) as min_value,
                MAX(value) as max_value
            FROM timeseries_data
            WHERE well_id = ?
              AND metric_name = ?
              AND DATE(timestamp) >= DATE(?)
              AND DATE(timestamp) <= DATE(?)
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp)
        """

        cursor = self.db_connection.cursor()
        cursor.execute(
            query,
            (well_id, metric_name, start_date.isoformat(), end_date.isoformat()),
        )

        results = []
        for row in cursor.fetchall():
            period_date_str, time_period_str, agg_val, count, min_val, max_val = row

            # Calculate data completeness
            # Expected points per day = 24 hours * 60 minutes = 1440 points
            expected_points = 24 * 60
            data_completeness = (count / expected_points) * 100 if expected_points > 0 else 0.0

            # Convert date strings to date objects
            period_date = datetime.strptime(period_date_str, "%Y-%m-%d").date()

            results.append(
                AggregatedDataPoint(
                    date=period_date,
                    time_period=time_period_str,
                    well_id=well_id,
                    metric_name=metric_name,
                    aggregated_value=agg_val,
                    aggregation_type=aggregation_type,
                    unit=unit,
                    data_point_count=count,
                    min_value=min_val,
                    max_value=max_val,
                    data_completeness=round(data_completeness, 2),
                )
            )

        cursor.close()
        return results
