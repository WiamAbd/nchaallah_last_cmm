PYTHON := python
UV := uv
SRC := src

.PHONY: install run debug clean lint lint-strict

install:
	$(UV) sync

run:
	$(UV) run $(PYTHON) -m $(SRC)

debug:
	$(UV) run $(PYTHON) -m pdb -m $(SRC)

lint:
	$(UV) run flake8 $(SRC)
	$(UV) run mypy $(SRC)

lint-strict:
	$(UV) run flake8 $(SRC)
	$(UV) run mypy $(SRC) --strict

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete