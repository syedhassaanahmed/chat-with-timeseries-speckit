-- Database schema for Oil Well Time Series API
-- SQLite database to store synthetic well data, metrics, and time-series measurements

-- Wells table: metadata for each oil well
CREATE TABLE IF NOT EXISTS wells (
    well_id TEXT PRIMARY KEY,
    well_name TEXT NOT NULL,
    latitude REAL NOT NULL CHECK(latitude BETWEEN -90 AND 90),
    longitude REAL NOT NULL CHECK(longitude BETWEEN -180 AND 180),
    operator TEXT NOT NULL,
    field_name TEXT NOT NULL,
    well_type TEXT NOT NULL CHECK(well_type IN ('producer', 'injector', 'observation')),
    spud_date TEXT NOT NULL,  -- ISO 8601 date (YYYY-MM-DD)
    data_start_date TEXT NOT NULL,
    data_end_date TEXT NOT NULL
);

-- Metrics table: definitions of measurable KPIs
CREATE TABLE IF NOT EXISTS metrics (
    metric_name TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    description TEXT NOT NULL,
    unit_of_measurement TEXT NOT NULL,
    data_type TEXT NOT NULL CHECK(data_type IN ('numeric', 'boolean', 'categorical')),
    typical_min REAL,
    typical_max REAL
);

-- Time-series data table: timestamped measurements
CREATE TABLE IF NOT EXISTS timeseries_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,  -- ISO 8601 UTC (YYYY-MM-DDTHH:MM:SSZ)
    well_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    value REAL NOT NULL,
    quality_flag TEXT DEFAULT 'good' CHECK(quality_flag IN ('good', 'suspect', 'bad')),
    FOREIGN KEY (well_id) REFERENCES wells(well_id),
    FOREIGN KEY (metric_name) REFERENCES metrics(metric_name)
);

-- Critical indexes for query performance
-- Index for time-range queries (well + metric + time range)
CREATE INDEX IF NOT EXISTS idx_well_metric_time 
ON timeseries_data(well_id, metric_name, timestamp);

-- Index for timestamp-based queries
CREATE INDEX IF NOT EXISTS idx_timestamp 
ON timeseries_data(timestamp);

-- Optional: Index for quality filtering
CREATE INDEX IF NOT EXISTS idx_quality_flag 
ON timeseries_data(quality_flag);
