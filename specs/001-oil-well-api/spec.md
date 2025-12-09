# Feature Specification: Oil Well Time Series API

**Feature Branch**: `001-oil-well-api`  
**Created**: 2025-12-09  
**Status**: Draft  
**Input**: User description: "Oil Well Time Series API – a public API that serves historical time-series data for oil wells, using synthetic data. The API will provide endpoints to retrieve both raw and aggregated time series data (oil production, gas injection, pressures, etc.) for a set of sample wells."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Query Raw Time Series Data for a Single Well (Priority: P1)

A data scientist wants to retrieve minute-by-minute oil production readings from a specific well over a date range to test an anomaly detection algorithm. They make an API request specifying the well ID, metric name (e.g., "oil_production_rate"), start date, and end date. The API returns timestamped data points in JSON format with realistic synthetic values.

**Why this priority**: This is the foundational MVP. Without the ability to retrieve raw time series data for a single well, no other functionality is possible. This delivers immediate value for developers building demos and testing analytics tools.

**Independent Test**: Can be fully tested by making a single HTTP request with a well ID and time range, verifying that the response contains properly formatted JSON with timestamps, metric values, and units. Success means developers can immediately integrate this endpoint into their applications.

**Acceptance Scenarios**:

1. **Given** a well with ID "WELL-001" exists in the system, **When** a user requests raw oil production data for January 2024, **Then** the system returns timestamped data points with values in barrels per day (bbl/day) and ISO 8601 timestamps.
2. **Given** multiple metrics exist for a well, **When** a user requests only "gas_injection_rate" data, **Then** only gas injection rate data is returned, not mixed with other metrics.
3. **Given** no data exists for the requested time range, **When** a user queries for raw data, **Then** the system returns an empty data array with metadata indicating zero results.
4. **Given** an invalid well ID is provided, **When** a user attempts to query, **Then** the system returns HTTP 404 with a clear error message.

---

### User Story 2 - Query Aggregated Time Series Data (Priority: P2)

An operations engineer wants to see daily average pressures for a well over the past month to identify trends. They request aggregated data specifying the well ID, metric name ("wellhead_pressure"), time range, and aggregation type ("daily_average"). The API returns computed daily averages with date labels and values.

**Why this priority**: Once raw data retrieval works, aggregation adds significant value by reducing data volume and enabling trend analysis. This is essential for realistic oil & gas use cases where monthly or daily summaries are common.

**Independent Test**: Can be fully tested by requesting daily aggregates for a multi-day period and verifying that the response contains one value per day with correct date labels. Success means users can build dashboards showing trends without processing massive raw datasets.

**Acceptance Scenarios**:

1. **Given** a well has hourly pressure readings for 30 days, **When** a user requests daily average pressures, **Then** the system returns 30 data points, each with a date and computed average value.
2. **Given** the user specifies aggregation type "daily_max", **When** data is returned, **Then** the response includes the maximum value for each day with clear labeling of the aggregation method.
3. **Given** a well has gaps in raw data (missing hours), **When** daily aggregation is requested, **Then** the system computes averages from available data and indicates data completeness in metadata.
4. **Given** the user requests aggregation for a single day with insufficient data points, **When** processing occurs, **Then** the system returns null or omits that day with a notation in metadata.

---

### User Story 3 - List Available Wells and Metrics (Priority: P3)

A developer exploring the API wants to discover what sample wells and metrics are available. They make a request to a "wells" endpoint and receive a list of all well IDs with metadata (location, name). They can also query a "metrics" endpoint to see available metric types (oil production, gas injection, pressures, etc.) with descriptions and units.

**Why this priority**: Discovery endpoints enable self-service exploration but aren't strictly necessary if documentation provides this information. This is valuable for usability but can be deprioritized if resources are limited.

**Independent Test**: Can be fully tested by calling the wells and metrics endpoints and verifying that the responses contain complete, well-formatted lists. Success means developers can build dynamic applications that adapt to available data without hardcoding well IDs.

**Acceptance Scenarios**:

1. **Given** 5 sample wells exist in the system, **When** a user requests the wells list, **Then** the system returns all 5 well IDs with names and location metadata.
2. **Given** 10 metric types are supported, **When** a user requests the metrics list, **Then** the system returns all metric names with descriptions and units of measurement.
3. **Given** a well has a subset of available metrics, **When** a user requests metrics for a specific well, **Then** only metrics with data for that well are returned.
4. **Given** the system has no wells (edge case for testing), **When** a user requests the wells list, **Then** an empty array is returned with HTTP 200 status.

---

### Edge Cases

- What happens when a user requests a time range spanning multiple years with potentially millions of data points? (Response size limits, performance degradation, pagination requirements)
- How does the system handle requests for metrics that don't exist or are misspelled? (Clear error messages, suggestions for valid metric names)
- What if a well's synthetic data has intentional gaps to simulate realistic sensor failures? (Documentation of data completeness, metadata flags)
- How are timezone specifications handled in timestamp queries? (Assume UTC, document clearly, handle timezone parameters if needed)
- What happens when a user requests aggregation with an invalid aggregation type (e.g., "daily_median" if not supported)? (HTTP 400 with list of supported aggregation types)
- How does the API behave under high concurrent load from multiple users? (Rate limiting considerations, performance benchmarks)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an endpoint to retrieve raw time series data by specifying well ID, metric name, start timestamp, and end timestamp.
- **FR-002**: System MUST return raw data as a JSON array of timestamped data points, with each point containing: timestamp (ISO 8601 UTC), metric_name, value, and unit.
- **FR-003**: System MUST provide an endpoint to retrieve aggregated time series data by specifying well ID, metric name, start date, end date, and aggregation type (daily_average, daily_max, daily_min, daily_sum, monthly_average).
- **FR-004**: System MUST return aggregated data in JSON format with: date or time period label, computed value, aggregation type, unit, and data point count used in calculation.
- **FR-005**: System MUST provide an endpoint to list all available wells with metadata including well ID, well name, location (latitude, longitude), and date range of available data.
- **FR-006**: System MUST provide an endpoint to list all available metrics with metadata including metric name, description, unit of measurement, and data type (numeric, boolean, categorical).
- **FR-007**: System MUST generate realistic synthetic time series data for at least 5 sample wells covering approximately 2 years of historical data.
- **FR-008**: System MUST include at least the following metric types: oil_production_rate (bbl/day), gas_production_rate (mcf/day), water_production_rate (bbl/day), wellhead_pressure (psi), gas_injection_rate (mcf/day), choke_setting (percent), well_status (online/offline/maintenance).
- **FR-009**: System MUST vary synthetic data characteristics across wells (e.g., different production profiles, seasonal variations, maintenance periods, gradual decline) to simulate realistic oilfield diversity.
- **FR-010**: System MUST return appropriate HTTP status codes: 200 for successful queries, 404 for non-existent wells or metrics, 400 for invalid parameters, 500 for server errors.
- **FR-011**: System MUST validate all query parameters (well IDs, metric names, date formats, aggregation types) and return clear error messages for invalid inputs.
- **FR-012**: System MUST support ISO 8601 timestamp formats for all time-related parameters and responses.
- **FR-013**: System MUST include response metadata indicating: total data points returned, time range covered, aggregation method (if applicable), and data completeness indicators.
- **FR-014**: System MUST provide consistent JSON naming conventions (snake_case recommended) across all endpoints and responses.
- **FR-015**: System MUST be publicly accessible with no authentication required (for this initial version focused on open demonstration purposes).

### Key Entities *(include if feature involves data)*

- **Well**: Represents an individual oil well with synthetic operational data. Key attributes: well_id (unique identifier), well_name (human-readable name), location (latitude, longitude), operator (company name), field_name, well_type (producer, injector, observation), spud_date (drilling start date), data_start_date, data_end_date.

- **Metric**: Represents a measurable oilfield KPI or operational parameter. Key attributes: metric_name (unique identifier like "oil_production_rate"), display_name (user-friendly label), description, unit_of_measurement, data_type (numeric, boolean, categorical), typical_range (min/max values for context).

- **TimeSeriesDataPoint**: Represents a single timestamped measurement from a well sensor. Key attributes: timestamp (ISO 8601 UTC), well_id, metric_name, value, unit, quality_flag (optional: good, suspect, bad).

- **AggregatedDataPoint**: Represents a computed summary over a time period. Key attributes: date or time_period, well_id, metric_name, aggregated_value, aggregation_type (daily_average, monthly_sum, etc.), unit, data_point_count, min_value (in period), max_value (in period).

- **SyntheticDataGenerator** (conceptual entity): The system component responsible for generating realistic synthetic time series data. Must simulate: baseline production trends, seasonal variations, gradual decline curves, random noise, planned maintenance periods, sensor failures, production optimization events.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: API returns properly formatted JSON responses that conform to documented schemas for 100% of valid requests (verified by automated contract tests).
- **SC-002**: Synthetic data exhibits realistic characteristics: production values within industry-typical ranges, gradual decline trends, seasonal variations, and maintenance periods for all 5 sample wells (verified by data quality analysis).
- **SC-003**: All API endpoints return appropriate HTTP status codes and error messages for invalid inputs with 100% consistency (verified by negative test cases).
- **SC-004**: API documentation (OpenAPI specification and README) covers 100% of endpoints with complete parameter descriptions, example requests, and example responses.
- **SC-005**: Developers can successfully integrate and retrieve data from any endpoint within 15 minutes of first reading the documentation (verified by user acceptance testing with 3+ external developers).

## Assumptions *(optional)*

- The API is designed for demonstration and testing purposes, so performance requirements are moderate (50 concurrent users, not 5000).
- All data is synthetic and publicly available—no real oilfield data or proprietary information is included.
- Authentication and authorization are explicitly out of scope for v1.0—the API is publicly accessible.
- Synthetic data generation occurs once at system initialization or deployment, not dynamically per request (data is pre-generated and stored).
- Time series data has consistent granularity (e.g., minute-level or hourly) defined at initialization.
- All timestamps are in UTC; timezone conversion is the client's responsibility.
- The API is read-only—no endpoints for modifying or deleting data.

## Out of Scope *(optional)*

- Real-time streaming of time series data (WebSocket or Server-Sent Events)
- User authentication or API keys
- Data ingestion endpoints (ability to upload new well data)
- Machine learning or predictive analytics features
- Data export in formats other than JSON (CSV, Excel, Parquet)
- Multi-well aggregation (e.g., total production across all wells in a field)
- Advanced query capabilities (filtering by value ranges, complex time-based windows)
- Visualization or charting components (API is data-only)
- Mobile-specific optimizations or SDKs
- Production-grade scalability (handling thousands of wells or petabytes of data)
