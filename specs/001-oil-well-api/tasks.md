# Tasks: Oil Well Time Series API

**Feature**: 001-oil-well-api  
**Input**: Design documents from `/specs/001-oil-well-api/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Organization**: Tasks are grouped by user story (P1, P2, P3) to enable independent implementation and testing.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3)
- All paths reference timeseries-api/ subdirectory (monorepo structure)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Dev Container setup (Constitution Principle VII requirement)

- [X] T001 Create project structure: timeseries-api/src/{models,services,api,db}, timeseries-api/tests/{contract,integration,unit}
- [X] T002 Create timeseries-api/pyproject.toml with Python 3.14, FastAPI, uvicorn, pydantic, numpy, pandas, pytest, httpx, ruff
- [X] T003 [P] Create .devcontainer/devcontainer.json with Python 3.14 base image, uv installation, VS Code extensions
- [X] T004 [P] Create .devcontainer/postCreate.sh script to install uv, dependencies, and initialize database
- [X] T005 [P] Create ruff.toml with linting rules (E, W, F, I, N, UP, ANN, B, C4, SIM)
- [X] T006 Create README.md with project overview, quick start link, and API description

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Create timeseries-api/src/config.py with database path, data generation constants, and environment configuration
- [X] T008 Create timeseries-api/src/db/schema.sql with wells, metrics, and timeseries_data tables per data-model.md
- [X] T009 Create timeseries-api/src/db/database.py with SQLite connection management and get_db_connection() dependency
- [X] T010 [P] Create timeseries-api/src/models/__init__.py (package initialization)
- [X] T011 [P] Create timeseries-api/src/services/__init__.py (package initialization)
- [X] T012 [P] Create timeseries-api/src/api/__init__.py (package initialization)
- [X] T013 [P] Create timeseries-api/src/db/__init__.py (package initialization)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Query Raw Time Series Data (Priority: P1) 🎯 MVP

**Goal**: Enable data scientists to retrieve minute-by-minute time-series data for a specific well and metric over a date range

**Independent Test**: Make HTTP GET to `/wells/WELL-001/data/raw?metric_name=oil_production_rate&start_timestamp=2024-12-09T00:00:00Z&end_timestamp=2025-01-09T23:59:59Z` and verify JSON response with timestamped data points

### Data Layer for User Story 1

- [X] T014 [P] [US1] Create timeseries-api/src/models/well.py with Well Pydantic model (well_id pattern validation, enums for well_type)
- [X] T015 [P] [US1] Create timeseries-api/src/models/metric.py with Metric Pydantic model (data_type enum, optional typical_min/max)
- [X] T016 [P] [US1] Create timeseries-api/src/models/timeseries.py with TimeSeriesDataPoint Pydantic model (datetime validation, quality_flag enum)
- [X] T017 [P] [US1] Create timeseries-api/src/models/responses.py with RawDataResponse Pydantic model (data array + metadata)

### Synthetic Data Generation for User Story 1

- [X] T018 [US1] Create timeseries-api/src/services/data_generator.py with SyntheticDataGenerator class
- [X] T019 [US1] Implement generate_well_metadata() method returning 3 wells with varied characteristics per FR-009
- [X] T020 [US1] Implement generate_metric_definitions() method returning 5 metrics per FR-008
- [X] T021 [US1] Implement generate_timeseries_data() method with numpy/pandas per research.md decision #1
- [X] T022 [US1] Apply decline curves: production(t) = initial_rate * exp(-decline_rate * t)
- [X] T023 [US1] Add seasonal variations: seasonal_factor = 1 + 0.1 * sin(2π * day_of_year / 365)
- [X] T024 [US1] Add random noise (±5%) using np.random.normal()
- [X] T025 [US1] Simulate maintenance periods (random 2-7 day shutdowns per well)
- [X] T026 [US1] Generate correlated metrics (gas correlates with oil, pressure decreases with depletion)

### Database Initialization for User Story 1

- [X] T027 [US1] Create timeseries-api/src/db/seed.py script to execute schema.sql and populate database
- [X] T028 [US1] Implement seed_wells() function to insert 3 wells into wells table
- [X] T029 [US1] Implement seed_metrics() function to insert 5 metrics into metrics table
- [X] T030 [US1] Implement seed_timeseries_data() function to insert ~7.9M rows into timeseries_data table
- [X] T031 [US1] Add progress logging and estimated time remaining during seed operation
- [X] T032 [US1] Verify indexes (idx_well_metric_time, idx_timestamp) are created per research.md decision #2

### Query Service for User Story 1

- [X] T033 [US1] Create timeseries-api/src/services/query_service.py with QueryService class
- [X] T034 [US1] Implement get_raw_timeseries() method with SQL query per research.md decision #2
- [X] T035 [US1] Add input validation: well_id format, metric_name exists, timestamp format ISO 8601
- [X] T036 [US1] Implement response metadata: total_points, data_completeness calculation per FR-013
- [X] T037 [US1] Add error handling: 404 for non-existent well/metric, 400 for invalid parameters per FR-010

### API Endpoints for User Story 1

- [X] T038 [US1] Create timeseries-api/src/api/main.py with FastAPI app initialization, CORS, and OpenAPI metadata
- [X] T039 [US1] Create timeseries-api/src/api/timeseries.py router with /wells/{well_id}/data/raw endpoint
- [X] T040 [US1] Implement GET /wells/{well_id}/data/raw handler with dependency injection per research.md decision #3
- [X] T041 [US1] Add Query parameters: metric_name (required), start_timestamp (required), end_timestamp (required)
- [X] T042 [US1] Wire QueryService.get_raw_timeseries() to endpoint handler
- [X] T043 [US1] Return RawDataResponse with data array and metadata per contracts/openapi.yaml
- [X] T044 [US1] Add error responses: 400 (ValidationError), 404 (NotFound), 500 (InternalServerError)

### Testing for User Story 1

- [X] T045 [P] [US1] Create timeseries-api/tests/contract/test_openapi_compliance.py to validate responses match openapi.yaml schemas
- [X] T046 [P] [US1] Create timeseries-api/tests/integration/test_timeseries_api.py with test_get_raw_data_success()
- [X] T047 [P] [US1] Add test_get_raw_data_invalid_well_id() expecting HTTP 404
- [X] T048 [P] [US1] Add test_get_raw_data_invalid_timestamp_format() expecting HTTP 400
- [X] T049 [P] [US1] Add test_get_raw_data_empty_result() for time range with no data
- [ ] T050 [P] [US1] Create timeseries-api/tests/unit/test_data_generator.py to verify decline curves, seasonal variations, noise
- [ ] T051 [P] [US1] Create timeseries-api/tests/unit/test_query_service.py to test get_raw_timeseries() with mock database

**Checkpoint**: User Story 1 complete - raw time-series data retrieval fully functional and independently testable

---

## Phase 4: User Story 2 - Query Aggregated Time Series Data (Priority: P2)

**Goal**: Enable operations engineers to retrieve daily/monthly aggregated summaries (average, max, min, sum) for trend analysis

**Independent Test**: Make HTTP GET to `/wells/WELL-001/data/aggregated?metric_name=wellhead_pressure&start_date=2024-12-09&end_date=2025-01-09&aggregation_type=daily_average` and verify JSON response with one value per day

### Data Layer for User Story 2

- [ ] T052 [P] [US2] Create timeseries-api/src/models/aggregated.py with AggregatedDataPoint Pydantic model (aggregation_type enum)
- [ ] T053 [P] [US2] Add AggregatedDataResponse to timeseries-api/src/models/responses.py (data array + metadata)

### Aggregation Service for User Story 2

- [ ] T054 [US2] Create timeseries-api/src/services/aggregation.py with AggregationService class
- [ ] T055 [US2] Implement compute_daily_average() method using SQL AVG() per research.md decision #2
- [ ] T056 [US2] Implement compute_daily_max() method using SQL MAX()
- [ ] T057 [US2] Implement compute_daily_min() method using SQL MIN()
- [ ] T058 [US2] Implement compute_daily_sum() method using SQL SUM()
- [ ] T059 [US2] Implement compute_monthly_average() method with DATE grouping by month
- [ ] T060 [US2] Add data_completeness calculation: (actual_points / expected_points) * 100
- [ ] T061 [US2] Include min_value, max_value, data_point_count in each aggregated result per FR-004

### Query Service Extension for User Story 2

- [ ] T062 [US2] Add get_aggregated_timeseries() method to timeseries-api/src/services/query_service.py
- [ ] T063 [US2] Validate aggregation_type against enum: daily_average, daily_max, daily_min, daily_sum, monthly_average
- [ ] T064 [US2] Route to appropriate AggregationService method based on aggregation_type
- [ ] T065 [US2] Implement response metadata: total_periods, average_data_completeness per FR-013
- [ ] T066 [US2] Handle gaps in data: compute from available data, indicate completeness in metadata per US2 scenario 3

### API Endpoints for User Story 2

- [ ] T067 [US2] Add GET /wells/{well_id}/data/aggregated endpoint to timeseries-api/src/api/timeseries.py
- [ ] T068 [US2] Add Query parameters: metric_name, start_date, end_date, aggregation_type
- [ ] T069 [US2] Wire QueryService.get_aggregated_timeseries() to endpoint handler
- [ ] T070 [US2] Return AggregatedDataResponse per contracts/openapi.yaml
- [ ] T071 [US2] Add validation: date format (YYYY-MM-DD), aggregation_type enum per FR-011

### Testing for User Story 2

- [ ] T072 [P] [US2] Add timeseries-api/tests/integration/test_aggregated_api.py with test_get_aggregated_daily_average()
- [ ] T073 [P] [US2] Add test_get_aggregated_daily_max() verifying MAX aggregation
- [ ] T074 [P] [US2] Add test_get_aggregated_monthly_average() verifying monthly grouping
- [ ] T075 [P] [US2] Add test_get_aggregated_with_data_gaps() verifying data_completeness < 100%
- [ ] T076 [P] [US2] Add test_get_aggregated_invalid_aggregation_type() expecting HTTP 400
- [ ] T077 [P] [US2] Create timeseries-api/tests/unit/test_aggregation.py to test each aggregation method with mock data

**Checkpoint**: User Stories 1 AND 2 complete - both raw and aggregated data retrieval independently functional

---

## Phase 5: User Story 3 - List Available Wells and Metrics (Priority: P3)

**Goal**: Enable developers to discover available wells and metrics for self-service API exploration

**Independent Test**: Make HTTP GET to `/wells` and `/metrics`, verify responses contain complete lists with metadata

### Query Service for User Story 3

- [X] T078 [US3] Add get_all_wells() method to timeseries-api/src/services/query_service.py returning all 3 wells
- [X] T079 [US3] Add get_well_by_id(well_id) method returning single well or None
- [X] T080 [US3] Add get_all_metrics() method returning all 5 metrics
- [X] T081 [US3] Add get_metrics_for_well(well_id) method returning only metrics with data for that well per US3 scenario 3
- [X] T082 [US3] Include response metadata: total_count, generated_at timestamp per FR-013

### Data Layer for User Story 3

- [X] T083 [P] [US3] Add WellListResponse to timeseries-api/src/models/responses.py (wells array + total_count + metadata)
- [X] T084 [P] [US3] Add MetricListResponse to timeseries-api/src/models/responses.py (metrics array + total_count + metadata)

### API Endpoints for User Story 3

- [X] T085 [US3] Create timeseries-api/src/api/wells.py router with GET /wells endpoint
- [X] T086 [US3] Implement GET /wells handler returning WellListResponse per contracts/openapi.yaml
- [X] T087 [US3] Add GET /wells/{well_id} endpoint returning single Well or HTTP 404
- [X] T088 [US3] Create timeseries-api/src/api/metrics.py router with GET /metrics endpoint
- [X] T089 [US3] Implement GET /metrics handler returning MetricListResponse
- [X] T090 [US3] Add GET /wells/{well_id}/metrics endpoint returning metrics for specific well
- [X] T091 [US3] Register wells and metrics routers in timeseries-api/src/api/main.py

### Testing for User Story 3

- [X] T092 [P] [US3] Create timeseries-api/tests/integration/test_wells_api.py with test_list_all_wells()
- [X] T093 [P] [US3] Add test_get_well_by_id_success() verifying single well retrieval
- [X] T094 [P] [US3] Add test_get_well_by_id_not_found() expecting HTTP 404
- [X] T095 [P] [US3] Add test_list_wells_empty_database() for edge case per US3 scenario 4
- [X] T096 [P] [US3] Create timeseries-api/tests/integration/test_metrics_api.py with test_list_all_metrics()
- [X] T097 [P] [US3] Add test_get_well_metrics() verifying filtered metric list for specific well

**Checkpoint**: All user stories (1, 2, 3) complete - full API functionality independently testable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and final quality checks

### Documentation

- [ ] T098 [P] Verify FastAPI auto-generates OpenAPI docs at /docs and /redoc per SC-007
- [ ] T099 [P] Add docstrings to all service methods and API endpoints per Constitution Principle III
- [ ] T100 [P] Update README.md with API overview, endpoints summary, link to quickstart.md

### Code Quality

- [ ] T101 Run ruff check and ruff format on entire codebase, fix all issues
- [ ] T102 Run pytest with --cov flag, verify >80% coverage per Constitution Principle IV
- [ ] T103 Verify all contract tests pass (OpenAPI schema compliance) per SC-003

### Final Validation

- [ ] T104 Test Dev Container build and database initialization per Constitution Principle VII
- [ ] T105 Verify all error responses return appropriate HTTP status codes per SC-005
- [ ] T106 Manual smoke test: start server, call each endpoint, verify responses per SC-008

---

## Dependencies & Parallel Execution

### Critical Path (Sequential Dependencies)

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3/4/5 (User Stories) → Phase 6 (Polish)
```

### Parallel Opportunities Within Each Phase

**Phase 1**: T003, T004, T005 can run in parallel after T001, T002

**Phase 2**: T010, T011, T012, T013 can run in parallel after T007, T008, T009

**Phase 3 (User Story 1)**:
- Data Layer (T014-T017): All run in parallel
- Synthetic Data (T018-T026): Sequential within, but parallel with Data Layer
- Database Init (T027-T032): Depends on T018-T026, sequential
- Query Service (T033-T037): Depends on Data Layer, sequential
- API Endpoints (T038-T044): Depends on Query Service, mostly sequential
- Testing (T045-T051): All run in parallel after implementation complete

**Phase 4 (User Story 2)**:
- T052, T053 in parallel
- T054-T061 sequential (aggregation methods)
- T072-T077 testing all in parallel

**Phase 5 (User Story 3)**:
- T078-T082 sequential (query methods)
- T083, T084 in parallel
- T092-T097 testing all in parallel

**Phase 6**: T098-T100 all in parallel, then T101-T106 sequential validation

### User Story Independence

- **US1, US2, US3 can be implemented in parallel** after Phase 2 completes
- Each user story has independent endpoints, models, and tests
- No inter-story dependencies (US2 does not depend on US1, US3 does not depend on US2)
- MVP can ship with just US1 (raw data retrieval)
- US2 and US3 are incremental enhancements

---

## Implementation Strategy

### Suggested MVP Scope (Sprint 1)

**Goal**: Deliver minimal viable API with raw data retrieval

- Phase 1: Setup (T001-T006)
- Phase 2: Foundational (T007-T013)
- Phase 3: User Story 1 only (T014-T051)
- Phase 6: Basic validation (T101-T103, T106)

**Estimated Effort**: ~3-5 days for experienced developer

**MVP Deliverable**: Working API with GET /wells/{id}/data/raw endpoint, synthetic data, Dev Container

### Incremental Delivery (Sprint 2+)

- Sprint 2: Add User Story 2 (aggregated data) - T052-T077
- Sprint 3: Add User Story 3 (discovery endpoints) - T078-T097
- Sprint 4: Documentation and polish - T098-T100, T104-T106

---

## Task Count Summary

- **Phase 1 (Setup)**: 6 tasks
- **Phase 2 (Foundational)**: 7 tasks (blocking)
- **Phase 3 (User Story 1)**: 38 tasks (MVP)
- **Phase 4 (User Story 2)**: 26 tasks
- **Phase 5 (User Story 3)**: 20 tasks
- **Phase 6 (Polish)**: 9 tasks

**Total**: 106 tasks

**Parallelizable**: 28 tasks marked with [P]

**MVP Critical Path**: 13 tasks (Phase 1) + 7 tasks (Phase 2) + ~25 sequential tasks (Phase 3) = ~45 tasks for MVP
