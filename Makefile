.PHONY: help test lint fix

help:
	@echo "Available commands:"
	@echo "  make test      - Run all tests with pytest"
	@echo "  make lint      - Run ruff linter (check only)"
	@echo "  make fix       - Auto-fix linting issues and format code"

test:
	@echo "Running tests..."
	pytest -c timeseries-api/pyproject.toml timeseries-api/tests/

lint:
	@echo "Running ruff linter..."
	ruff check --config timeseries-api/ruff.toml timeseries-api/src/ timeseries-api/tests/

fix:
	@echo "Fixing linting issues..."
	ruff check --config timeseries-api/ruff.toml timeseries-api/src/ timeseries-api/tests/ --fix
	@echo "Formatting code..."
	ruff format --config timeseries-api/ruff.toml timeseries-api/src/ timeseries-api/tests/
