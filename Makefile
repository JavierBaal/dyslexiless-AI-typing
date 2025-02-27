# Makefile para DyslexiLess

.PHONY: all clean install test lint format docs build dist publish help

# Variables
PYTHON := python3
VENV := venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
BLACK := $(VENV)/bin/black
FLAKE8 := $(VENV)/bin/flake8
MYPY := $(VENV)/bin/mypy
TOX := $(VENV)/bin/tox
SPHINX := $(VENV)/bin/sphinx-build

# Directorios
SRC_DIR := dyslexiless
TEST_DIR := tests
DOCS_DIR := docs
BUILD_DIR := build
DIST_DIR := dist

help:
	@echo "Comandos disponibles:"
	@echo "  make install    - Instalar dependencias del proyecto"
	@echo "  make dev        - Instalar dependencias de desarrollo"
	@echo "  make test      - Ejecutar pruebas"
	@echo "  make lint      - Ejecutar análisis de código"
	@echo "  make format    - Formatear código"
	@echo "  make docs      - Generar documentación"
	@echo "  make build     - Construir paquete"
	@echo "  make dist      - Crear distribución"
	@echo "  make publish   - Publicar en PyPI"
	@echo "  make clean     - Limpiar archivos generados"
	@echo "  make all       - Ejecutar todas las tareas"

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install -r requirements.txt

dev: install
	$(PIP) install -r requirements-dev.txt
	pre-commit install

test:
	$(PYTEST) $(TEST_DIR) \
		--cov=$(SRC_DIR) \
		--cov-report=html \
		--cov-report=term \
		-v

lint:
	$(FLAKE8) $(SRC_DIR) $(TEST_DIR)
	$(MYPY) $(SRC_DIR)
	bandit -r $(SRC_DIR)

format:
	$(BLACK) $(SRC_DIR) $(TEST_DIR)
	isort $(SRC_DIR) $(TEST_DIR)

docs:
	cd $(DOCS_DIR) && $(PYTHON) generate_docs.py
	$(SPHINX) -b html $(DOCS_DIR)/source $(DOCS_DIR)/build/html

build: clean
	$(PYTHON) setup.py build

dist: clean
	$(PYTHON) setup.py sdist bdist_wheel

publish: dist
	twine check dist/*
	twine upload dist/*

clean:
	rm -rf $(BUILD_DIR)
	rm -rf $(DIST_DIR)
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .mypy_cache
	rm -rf .tox
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".eggs" -exec rm -rf {} +

all: install dev lint test docs build

# Configuración por defecto
.DEFAULT_GOAL := help
