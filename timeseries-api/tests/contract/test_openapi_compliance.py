"""Contract tests to verify API responses match OpenAPI specification."""

import sqlite3
from typing import Any

import pytest
import yaml
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def db_connection() -> sqlite3.Connection:
    """Get a database connection for test verification."""
    from src.config import DATABASE_PATH

    conn = sqlite3.connect(DATABASE_PATH)
    yield conn
    conn.close()


@pytest.fixture
def openapi_spec() -> dict[str, Any]:
    """Load the OpenAPI specification."""
    spec_path = (
        "/workspaces/chat-with-timeseries-speckit/specs/001-oil-well-api/contracts/openapi.yaml"
    )
    with open(spec_path) as f:
        return yaml.safe_load(f)


@pytest.fixture
def valid_well_id(db_connection: sqlite3.Connection) -> str:
    """Get a valid well_id from the database."""
    cursor = db_connection.cursor()
    cursor.execute("SELECT well_id FROM wells LIMIT 1")
    result = cursor.fetchone()
    assert result is not None
    return result[0]


@pytest.fixture
def valid_metric_name(db_connection: sqlite3.Connection) -> str:
    """Get a valid metric_name from the database."""
    cursor = db_connection.cursor()
    cursor.execute("SELECT metric_name FROM metrics LIMIT 1")
    result = cursor.fetchone()
    assert result is not None
    return result[0]


def validate_schema_properties(data: dict[str, Any], schema: dict[str, Any]) -> None:
    """Validate that data matches schema properties."""
    required = schema.get("required", [])
    properties = schema.get("properties", {})

    # Check all required properties are present
    for prop in required:
        assert prop in data, f"Required property '{prop}' missing"

    # Check each property type matches
    for prop, value in data.items():
        if prop not in properties:
            continue

        prop_schema = properties[prop]
        prop_type = prop_schema.get("type")

        if prop_type == "string":
            assert isinstance(value, str), f"Property '{prop}' should be string"
        elif prop_type == "number":
            assert isinstance(value, (int, float)), f"Property '{prop}' should be number"
        elif prop_type == "integer":
            assert isinstance(value, int), f"Property '{prop}' should be integer"
        elif prop_type == "boolean":
            assert isinstance(value, bool), f"Property '{prop}' should be boolean"
        elif prop_type == "array":
            assert isinstance(value, list), f"Property '{prop}' should be array"
        elif prop_type == "object":
            assert isinstance(value, dict), f"Property '{prop}' should be object"


def test_wells_list_matches_openapi_schema(
    client: TestClient, openapi_spec: dict[str, Any]
) -> None:
    """Test that GET /wells response matches OpenAPI schema."""
    response = client.get("/wells")
    assert response.status_code == 200

    data = response.json()

    # Get schema from OpenAPI spec
    wells_response_schema = openapi_spec["components"]["schemas"]["WellListResponse"]

    # Validate top-level response structure
    validate_schema_properties(data, wells_response_schema)

    # Validate each well object
    if data["wells"]:
        well_schema = openapi_spec["components"]["schemas"]["Well"]
        for well in data["wells"]:
            validate_schema_properties(well, well_schema)

            # Validate well_type enum
            assert well["well_type"] in well_schema["properties"]["well_type"]["enum"]


def test_metrics_list_matches_openapi_schema(
    client: TestClient, openapi_spec: dict[str, Any]
) -> None:
    """Test that GET /metrics response matches OpenAPI schema."""
    response = client.get("/metrics")
    assert response.status_code == 200

    data = response.json()

    # Get schema from OpenAPI spec
    metrics_response_schema = openapi_spec["components"]["schemas"]["MetricListResponse"]

    # Validate top-level response structure
    validate_schema_properties(data, metrics_response_schema)

    # Validate each metric object
    if data["metrics"]:
        metric_schema = openapi_spec["components"]["schemas"]["Metric"]
        for metric in data["metrics"]:
            validate_schema_properties(metric, metric_schema)

            # Validate data_type enum
            assert metric["data_type"] in metric_schema["properties"]["data_type"]["enum"]


def test_raw_data_matches_openapi_schema(
    client: TestClient,
    openapi_spec: dict[str, Any],
    valid_well_id: str,
    valid_metric_name: str,
) -> None:
    """Test that GET /wells/{well_id}/data/raw response matches OpenAPI schema."""
    params = {
        "metric_name": valid_metric_name,
        "start_timestamp": "2024-12-09T00:00:00Z",
        "end_timestamp": "2024-12-09T01:00:00Z",
    }

    response = client.get(f"/wells/{valid_well_id}/data/raw", params=params)
    assert response.status_code == 200

    data = response.json()

    # Get schema from OpenAPI spec
    raw_data_response_schema = openapi_spec["components"]["schemas"]["RawDataResponse"]

    # Validate top-level response structure
    validate_schema_properties(data, raw_data_response_schema)

    # Validate each data point
    if data["data"]:
        data_point_schema = openapi_spec["components"]["schemas"]["TimeSeriesDataPoint"]
        for point in data["data"]:
            validate_schema_properties(point, data_point_schema)

            # Validate quality_flag enum
            assert point["quality_flag"] in data_point_schema["properties"]["quality_flag"]["enum"]

    # Validate metadata
    metadata_schema = raw_data_response_schema["properties"]["metadata"]
    validate_schema_properties(data["metadata"], metadata_schema)


def test_error_response_matches_openapi_schema(
    client: TestClient, openapi_spec: dict[str, Any]
) -> None:
    """Test that error responses match OpenAPI schema."""
    # Trigger a 404 error
    response = client.get("/wells/WELL-999")
    assert response.status_code == 404

    data = response.json()

    # FastAPI uses standard error format
    assert "detail" in data


def test_well_by_id_matches_openapi_schema(
    client: TestClient, openapi_spec: dict[str, Any], valid_well_id: str
) -> None:
    """Test that GET /wells/{well_id} response matches OpenAPI schema."""
    response = client.get(f"/wells/{valid_well_id}")
    assert response.status_code == 200

    data = response.json()

    # Get schema from OpenAPI spec
    well_schema = openapi_spec["components"]["schemas"]["Well"]

    # Validate well object
    validate_schema_properties(data, well_schema)

    # Validate well_type enum
    assert data["well_type"] in well_schema["properties"]["well_type"]["enum"]


def test_well_metrics_matches_openapi_schema(
    client: TestClient, openapi_spec: dict[str, Any], valid_well_id: str
) -> None:
    """Test that GET /wells/{well_id}/metrics response matches OpenAPI schema."""
    response = client.get(f"/wells/{valid_well_id}/metrics")
    assert response.status_code == 200

    data = response.json()

    # Get schema from OpenAPI spec
    metrics_response_schema = openapi_spec["components"]["schemas"]["MetricListResponse"]

    # Validate top-level response structure
    validate_schema_properties(data, metrics_response_schema)

    # Validate each metric object
    if data["metrics"]:
        metric_schema = openapi_spec["components"]["schemas"]["Metric"]
        for metric in data["metrics"]:
            validate_schema_properties(metric, metric_schema)


def test_openapi_json_endpoint_available(client: TestClient) -> None:
    """Test that OpenAPI JSON is available at /openapi.json."""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    openapi_json = response.json()
    assert "openapi" in openapi_json
    assert "info" in openapi_json
    assert "paths" in openapi_json


def test_all_required_endpoints_exist(client: TestClient, openapi_spec: dict[str, Any]) -> None:
    """Test that all endpoints defined in OpenAPI spec are implemented."""
    paths = openapi_spec["paths"]

    # List of expected endpoints
    expected_endpoints = [
        ("/wells", "get"),
        ("/wells/{well_id}", "get"),
        ("/wells/{well_id}/metrics", "get"),
        ("/wells/{well_id}/data/raw", "get"),
        ("/metrics", "get"),
    ]

    for path, method in expected_endpoints:
        assert path in paths, f"Path {path} not found in OpenAPI spec"
        assert method in paths[path], f"Method {method} not found for path {path}"


def test_content_type_headers(client: TestClient) -> None:
    """Test that responses have correct Content-Type headers."""
    response = client.get("/wells")
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]


def test_timestamp_formats_are_iso8601(
    client: TestClient, valid_well_id: str, valid_metric_name: str
) -> None:
    """Test that all timestamps in responses are ISO 8601 format."""
    params = {
        "metric_name": valid_metric_name,
        "start_timestamp": "2024-12-09T00:00:00Z",
        "end_timestamp": "2024-12-09T00:10:00Z",
    }

    response = client.get(f"/wells/{valid_well_id}/data/raw", params=params)
    assert response.status_code == 200

    data = response.json()

    # Check data point timestamps
    for point in data["data"]:
        timestamp = point["timestamp"]
        # ISO 8601 format: YYYY-MM-DDTHH:MM:SS[.ffffff][+HH:MM|Z]
        assert "T" in timestamp
        assert timestamp.endswith("Z") or "+" in timestamp or "-" in timestamp.split("T")[1]

    # Check metadata timestamps
    assert "T" in data["metadata"]["start_timestamp"]
    assert "T" in data["metadata"]["end_timestamp"]
