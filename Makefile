# Makefile for Medium to WordPress Converter

.PHONY: help install test clean lint format run-example

# Default target
help:
	@echo "Medium to WordPress Converter - Development Commands"
	@echo "=================================================="
	@echo "install    - Install dependencies"
	@echo "test       - Run test suite"
	@echo "test-deps  - Test only dependencies"
	@echo "clean      - Clean generated files"
	@echo "lint       - Run code linting (if flake8 installed)"
	@echo "format     - Format code (if black installed)"
	@echo "example    - Run example with sample data"
	@echo "list       - List available posts"
	@echo "help       - Show this help message"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed"

# Run test suite
test:
	@echo "Running test suite..."
	python test_setup.py

# Test only dependencies
test-deps:
	@echo "Testing dependencies..."
	python -c "import requests; print('✅ requests')"
	python -c "from bs4 import BeautifulSoup; print('✅ beautifulsoup4')"
	python -c "import lxml; print('✅ lxml')"
	@echo "✅ All dependencies working"

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -f *.xml
	rm -rf __pycache__/
	rm -rf *.egg-info/
	rm -rf build/
	rm -rf dist/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	@echo "✅ Cleaned"

# Run linting (optional)
lint:
	@if command -v flake8 >/dev/null 2>&1; then \
		echo "Running flake8..."; \
		flake8 medium_to_wordpress_optimized.py test_setup.py; \
	else \
		echo "flake8 not installed, skipping lint"; \
	fi

# Format code (optional)
format:
	@if command -v black >/dev/null 2>&1; then \
		echo "Formatting with black..."; \
		black medium_to_wordpress_optimized.py test_setup.py; \
	else \
		echo "black not installed, skipping format"; \
	fi

# Run example (list posts)
list:
	@echo "Listing available posts..."
	python medium_to_wordpress_optimized.py list

# Example conversion (requires posts in export_htmls)
example:
	@if [ -d "export_htmls" ] && [ "$$(ls -A export_htmls/*.html 2>/dev/null | wc -l)" -gt 0 ]; then \
		echo "Running example conversion..."; \
		python medium_to_wordpress_optimized.py single 1 example.com --no-images; \
	else \
		echo "No HTML files found in export_htmls directory"; \
		echo "Please add Medium HTML exports to run example"; \
	fi

# Quick setup for new users
setup: install test
	@echo ""
	@echo "🎉 Setup complete! Your environment is ready."
	@echo ""
	@echo "Next steps:"
	@echo "1. Export your Medium posts (Settings → Download your information)"
	@echo "2. Copy HTML files to export_htmls/ directory"
	@echo "3. Run: make list"
	@echo "4. Run: python medium_to_wordpress_optimized.py all yourdomain.com"

# Development setup
dev-setup: install
	@echo "Installing development dependencies..."
	@pip install black flake8 2>/dev/null || echo "Optional dev tools not installed"
	@echo "✅ Development setup complete"
