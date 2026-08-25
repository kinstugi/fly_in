MAP ?= maps/easy/01_linear_path.txt
UV ?= uv
PYTHON_VERSION ?= 3.12

.PHONY: run install debug clean lint lint-strict

run: install
	./env/bin/python3 main.py $(MAP)

install: env
	$(UV) pip install --python ./env/bin/python flake8 mypy pygame

env: env/.uv-python-$(PYTHON_VERSION)

env/.uv-python-$(PYTHON_VERSION):
	@command -v $(UV) >/dev/null || \
		(echo "Error: $(UV) is required to create env" >&2; exit 1)
	$(UV) venv --python $(PYTHON_VERSION) --clear env
	touch $@

debug: install
	./env/bin/python3 -m pdb main.py $(MAP)

clean:
	rm -rf env
	rm -rf __pycache__
	rm -rf .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

lint: install
	./env/bin/flake8 . --exclude=env,build && ./env/bin/mypy . \
		--warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs --exclude env --exclude build

lint-strict: install
	./env/bin/flake8 . --exclude=env,build && ./env/bin/mypy . --exclude env --exclude build --strict
