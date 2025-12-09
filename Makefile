.PHONY: help test lint fix

help:
	@echo "Available commands:"
	@echo "  make test      - Run all tests with pytest"
	@echo "  make lint      - Run ruff linter (check only)"
	@echo "  make fix       - Auto-fix linting issues and format code"

test:
	@echo "Running tests..."
	pytest

lint:
	@echo "Running ruff linter..."
	ruff check src/ tests/

fix:
	@echo "Fixing linting issues..."
	ruff check src/ tests/ --fix
	@echo "Formatting code..."
	ruff format src/ tests/
