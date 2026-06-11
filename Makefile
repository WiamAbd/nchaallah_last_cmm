PYTHON := python
UV := uv
SRC := src

.PHONY: install run debug clean lint lint-strict

install:
	mkdir -p /goinfre/wabdella/.uv-cache
	UV_CACHE_DIR=/goinfre/wabdella/.uv-cache $(UV) sync

run:
	$(UV) run $(PYTHON) -m $(SRC)

debug:
	$(UV) run $(PYTHON) -m pdb -m $(SRC)

lint:
	$(UV) run flake8 src
	$(UV) run mypy src \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs \
		--follow-imports=skip

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete