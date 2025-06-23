.PHONY: help install dev test test-cov clean build upload docs format lint type-check

help:
	@echo "Available commands:"
	@echo "  install     Install the package"
	@echo "  dev         Install development dependencies"
	@echo "  test        Run tests"
	@echo "  test-cov    Run tests with coverage"
	@echo "  clean       Clean build artifacts"
	@echo "  build       Build the package"
	@echo "  upload      Upload to PyPI"
	@echo "  format      Format code with black"
	@echo "  lint        Lint code with ruff"
	@echo "  type-check  Type check with mypy"

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/

test-cov:
	pytest --cov=result_type --cov-report=term-missing --cov-report=html tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete

format:
	black result_type tests

lint:
	ruff check result_type tests

type-check:
	mypy result_type

build: clean
	python -m build

upload: build
	@echo "Uploading to PyPI..."
	@echo "Make sure you have your PyPI API token ready!"
	python -m twine upload dist/*

upload-test: build
	@echo "Uploading to Test PyPI..."
	@echo "Make sure you have your Test PyPI API token ready!"
	python -m twine upload --repository testpypi dist/*

publish: 
	@echo "Running interactive publish script..."
	./publish.sh
