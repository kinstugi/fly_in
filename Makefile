run: install
	./env/bin/python3 main.py maps/easy/01_linear_path.txt

install: env
	./env/bin/pip install flake8 mypy

env:
	python3 -m venv env
	./env/bin/pip install --upgrade pip

debug: install
	./env/bin/python3 -m pdb a_maze_ing.py config.txt

clean:
	rm -rf env
	rm -rf __pycache__
	rm -rf .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

lint:
	./env/bin/flake8 . --exclude=env,build && ./env/bin/mypy . --exclude env --exclude build

lint-strict:
	./env/bin/flake8 . --exclude=env,build && ./env/bin/mypy . --exclude env --exclude build --strict
