.PHONY: help test test-cov lint fix

help:
	@echo "Available commands:"
	@echo "  make test      - Run all tests with pytest"
	@echo "  make test-cov  - Run tests with coverage report"
	@echo "  make lint      - Run ruff linter (check only)"
	@echo "  make fix       - Auto-fix linting issues and format code"

test:
	@echo "Running tests..."
	pytest -c timeseries-api/pyproject.toml timeseries-api/tests/

test-cov:
	@echo "Running tests with coverage report..."
	pytest -c timeseries-api/pyproject.toml timeseries-api/tests/ --cov=timeseries-api/src --cov-report=html --cov-report=term-missing

lint:
	@echo "Running ruff linter..."
	ruff check timeseries-api/src/ timeseries-api/tests/

fix:
	@echo "Fixing linting issues..."
	ruff check timeseries-api/src/ timeseries-api/tests/ --fix
	@echo "Formatting code..."
	ruff format timeseries-api/src/ timeseries-api/tests/
