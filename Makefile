.PHONY: help install install-dev test lint type-check format clean build upload

help:
	@echo "Aifr Development Commands"
	@echo ""
	@echo "  make install       - Install package"
	@echo "  make install-dev   - Install package with dev dependencies"
	@echo "  make test          - Run tests with pytest"
	@echo "  make lint          - Run linting checks"
	@echo "  make type-check    - Run mypy type checking"
	@echo "  make clean         - Remove build artifacts"
	@echo "  make build         - Build distribution packages"
	@echo "  make upload        - Upload to PyPI (requires credentials)"
	@echo ""

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

lint:
	@echo "Running basic Python syntax check..."
	python -m py_compile aifr/*.py

type-check:
	mypy aifr/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

build: clean
	python -m build

upload: build
	python -m twine upload dist/*
