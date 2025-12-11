"""Synthetic data generator for Oil Well Time Series API.

Generates realistic oil well time-series data with:
- Production decline curves
- Seasonal variations
- Random noise
- Maintenance periods
- Correlated metrics
"""

import random
from datetime import datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd

from src.config import (
    DATA_END_DATE,
    DATA_FREQUENCY_MINUTES,
    DATA_START_DATE,
    DECLINE_RATE_MAX,
    DECLINE_RATE_MIN,
    FIELDS,
    INITIAL_PRODUCTION_MAX,
    INITIAL_PRODUCTION_MIN,
    MAINTENANCE_DURATION_MAX,
    MAINTENANCE_DURATION_MIN,
    MAINTENANCE_PROBABILITY,
    METRIC_CONFIGS,
    NOISE_AMPLITUDE,
    NUM_WELLS,
    OPERATORS,
    SEASONAL_AMPLITUDE,
    WELL_TYPES,
)


class SyntheticDataGenerator:
    """Generates synthetic oil well time-series data."""

    def __init__(self, seed: int | None = 42) -> None:
        """Initialize the data generator.

        Args:
            seed: Random seed for reproducibility. Defaults to 42.
        """
        self.seed = seed
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

    def generate_well_metadata(self) -> list[dict[str, Any]]:
        """Generate metadata for sample wells.

        Returns:
            List of well metadata dictionaries with varied characteristics.
        """
        wells = []
        for i in range(NUM_WELLS):
            well_id = f"WELL-{i + 1:03d}"
            wells.append(
                {
                    "well_id": well_id,
                    "well_name": f"{random.choice(FIELDS)} {chr(65 + i)} {i + 1}",
                    "latitude": round(random.uniform(28.0, 32.0), 4),
                    "longitude": round(random.uniform(-97.0, -93.0), 4),
                    "operator": random.choice(OPERATORS),
                    "field_name": random.choice(FIELDS),
                    "well_type": random.choice(WELL_TYPES),
                    "spud_date": (
                        datetime.strptime(DATA_START_DATE, "%Y-%m-%d")
                        - timedelta(days=random.randint(180, 730))
                    ).date(),
                    "data_start_date": datetime.strptime(DATA_START_DATE, "%Y-%m-%d").date(),
                    "data_end_date": datetime.strptime(DATA_END_DATE, "%Y-%m-%d").date(),
                }
            )
        return wells

    def generate_metric_definitions(self) -> list[dict[str, Any]]:
        """Generate metric definitions.

        Returns:
            List of metric definition dictionaries.
        """
        metrics = []
        for metric_name, config in METRIC_CONFIGS.items():
            metrics.append(
                {
                    "metric_name": metric_name,
                    "display_name": config["display_name"],
                    "description": f"Synthetic {config['display_name'].lower()} measurements",
                    "unit_of_measurement": config["unit"],
                    "data_type": config["data_type"],
                    "typical_min": config["typical_min"],
                    "typical_max": config["typical_max"],
                }
            )
        return metrics

    def generate_timeseries_data(
        self, wells: list[dict[str, Any]], metrics: list[dict[str, Any]]
    ) -> pd.DataFrame:
        """Generate synthetic time-series data for all wells and metrics.

        Implements:
        - Decline curves: production(t) = initial_rate * exp(-decline_rate * t)
        - Seasonal variations: seasonal_factor = 1 + amplitude * sin(2π * day_of_year / 365)
        - Random noise: ±5% using normal distribution
        - Maintenance periods: random 2-7 day shutdowns
        - Correlated metrics: gas correlates with oil, pressure decreases with depletion

        Args:
            wells: List of well metadata dictionaries
            metrics: List of metric definition dictionaries

        Returns:
            DataFrame with columns: timestamp, well_id, metric_name, value, quality_flag
        """
        # Generate timestamp range at minute-level granularity
        timestamps = pd.date_range(
            start=DATA_START_DATE,
            end=DATA_END_DATE,
            freq=f"{DATA_FREQUENCY_MINUTES}min",
        )

        all_data = []

        for well in wells:
            well_id = well["well_id"]
            well_type = well["well_type"]

            # Generate production profiles per well
            initial_oil_rate = random.uniform(INITIAL_PRODUCTION_MIN, INITIAL_PRODUCTION_MAX)
            decline_rate = random.uniform(DECLINE_RATE_MIN, DECLINE_RATE_MAX)

            # Generate maintenance periods for this well
            maintenance_periods = self._generate_maintenance_periods(timestamps)

            for metric in metrics:
                metric_name = metric["metric_name"]

                # Generate base time-series with decline curve
                values = self._apply_decline_curve(
                    timestamps, initial_oil_rate, decline_rate, metric_name, well_type
                )

                # Apply seasonal variations
                values = self._apply_seasonal_variations(values, timestamps)

                # Add random noise
                values = self._add_random_noise(values)

                # Apply maintenance periods (set to near-zero) - only for production/flow metrics
                if metric_name in [
                    "oil_production_rate",
                    "gas_production_rate",
                    "gas_injection_rate",
                ]:
                    values = self._apply_maintenance_periods(
                        values, timestamps, maintenance_periods
                    )

                # Ensure non-negative values for production metrics
                if metric_name in [
                    "oil_production_rate",
                    "gas_production_rate",
                    "gas_injection_rate",
                ]:
                    values = np.maximum(values, 0)

                # Generate quality flags (mostly "good")
                quality_flags = np.random.choice(
                    ["good", "suspect", "bad"],
                    size=len(values),
                    p=[0.98, 0.015, 0.005],  # 98% good, 1.5% suspect, 0.5% bad
                )

                # Create DataFrame for this well + metric
                df_segment = pd.DataFrame(
                    {
                        "timestamp": timestamps,
                        "well_id": well_id,
                        "metric_name": metric_name,
                        "value": values,
                        "quality_flag": quality_flags,
                    }
                )

                all_data.append(df_segment)

        # Combine all data
        df_all = pd.concat(all_data, ignore_index=True)

        # Convert timestamp to ISO 8601 UTC string
        df_all["timestamp"] = df_all["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        return df_all

    def _apply_decline_curve(
        self,
        timestamps: pd.DatetimeIndex,
        initial_rate: float,
        decline_rate: float,
        metric_name: str,
        well_type: str,
    ) -> np.ndarray:
        """Apply exponential decline curve to production data.

        Formula: production(t) = initial_rate * exp(-decline_rate * t)

        Args:
            timestamps: Time series index
            initial_rate: Initial production rate
            decline_rate: Decline rate per day
            metric_name: Name of the metric
            well_type: Type of well (producer, injector, observation)

        Returns:
            Array of values with decline applied
        """
        days = (timestamps - timestamps[0]).days.values

        if metric_name == "oil_production_rate":
            values = initial_rate * np.exp(-decline_rate * days)
        elif metric_name == "gas_production_rate":
            # Gas correlates with oil (GOR ratio ~3-5 mcf/bbl)
            gor = random.uniform(3, 5)
            values = initial_rate * gor * np.exp(-decline_rate * days)
        elif metric_name == "wellhead_pressure":
            # Pressure decreases with depletion
            initial_pressure = random.uniform(1500, 2500)
            values = initial_pressure * np.exp(-decline_rate * days * 0.5)
        elif metric_name == "tubing_pressure":
            # Tubing pressure slightly lower than wellhead
            initial_pressure = random.uniform(1200, 2200)
            values = initial_pressure * np.exp(-decline_rate * days * 0.5)
        elif metric_name == "gas_injection_rate":
            # Injection rate stays relatively constant
            if well_type == "injector":
                values = np.full(len(days), random.uniform(500, 1200))
            else:
                values = np.zeros(len(days))
        else:
            values = np.full(len(days), 100.0)

        return values

    def _apply_seasonal_variations(
        self, values: np.ndarray, timestamps: pd.DatetimeIndex
    ) -> np.ndarray:
        """Apply seasonal variations to data.

        Formula: seasonal_factor = 1 + amplitude * sin(2π * day_of_year / 365)

        Args:
            values: Base values
            timestamps: Time series index

        Returns:
            Values with seasonal variations applied
        """
        day_of_year = timestamps.dayofyear.values
        seasonal_factor = 1 + SEASONAL_AMPLITUDE * np.sin(2 * np.pi * day_of_year / 365)
        return values * seasonal_factor

    def _add_random_noise(self, values: np.ndarray) -> np.ndarray:
        """Add random noise to data (±5%).

        Args:
            values: Base values

        Returns:
            Values with noise added
        """
        noise = np.random.normal(1.0, NOISE_AMPLITUDE, size=len(values))
        return values * noise

    def _generate_maintenance_periods(
        self, timestamps: pd.DatetimeIndex
    ) -> list[tuple[datetime, datetime]]:
        """Generate random maintenance periods.

        Args:
            timestamps: Time series index

        Returns:
            List of (start, end) datetime tuples for maintenance periods
        """
        maintenance_periods = []
        current_date = timestamps[0]

        while current_date < timestamps[-1]:
            # Check if maintenance should start (based on probability)
            if random.random() < MAINTENANCE_PROBABILITY:
                duration_days = random.randint(MAINTENANCE_DURATION_MIN, MAINTENANCE_DURATION_MAX)
                start = current_date
                end = start + timedelta(days=duration_days)
                maintenance_periods.append((start, end))
                current_date = end + timedelta(days=30)  # Skip 30 days after maintenance
            else:
                current_date += timedelta(days=1)

        return maintenance_periods

    def _apply_maintenance_periods(
        self,
        values: np.ndarray,
        timestamps: pd.DatetimeIndex,
        maintenance_periods: list[tuple[datetime, datetime]],
    ) -> np.ndarray:
        """Set values to near-zero during maintenance periods.

        Args:
            values: Base values
            timestamps: Timestamp index corresponding to values
            maintenance_periods: List of (start, end) datetime tuples

        Returns:
            Values with maintenance periods applied (near-zero during shutdowns)
        """
        # Create a copy to avoid modifying the original array
        result = values.copy()

        # For each maintenance period, find matching timestamps and set values to near-zero
        for start, end in maintenance_periods:
            # Find indices where timestamps fall within this maintenance period
            mask = (timestamps >= start) & (timestamps <= end)
            # Set values to near-zero (0.1% of original to simulate minimal residual flow)
            result[mask] = result[mask] * 0.001

        return result
