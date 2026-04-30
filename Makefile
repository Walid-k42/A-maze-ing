install:
	python3 -m pip install --upgrade pip
	python3 -m pip install build flake8 mypy pydantic

build:
	python3 -m pip install --upgrade build
	python3 -m build
	cp dist/mazegen-1.0.0-py3-none-any.whl .
	cp dist/mazegen-1.0.0.tar.gz .

run:
		python3 a_maze_ing.py config.txt

debug:
		python3 -m pdb a_maze_ing.py config.txt

clean:
		rm -rf __pycache__ .mypy_cache build dist mazegen.egg-info
		find . -type d -name "__pycache__" -exec rm -rf {} +
		find . -type f -name "*.pyc" -delete

lint:
		flake8 .
		mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs