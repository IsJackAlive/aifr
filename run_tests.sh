#!/bin/bash
set -e

echo "Running type checks..."
./venv/bin/python -m mypy aifr/ --strict

echo "Running tests..."
./venv/bin/python -m pytest tests/

echo "All checks passed!"
