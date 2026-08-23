MAP ?= maps/easy/01_linear_path.txt

.PHONY: run install debug clean lint lint-strict

run: install
	./env/bin/python3 main.py $(MAP)

install: env
	./env/bin/pip install flake8 mypy

env:
	python3 -m venv env
	./env/bin/pip install --upgrade pip

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
