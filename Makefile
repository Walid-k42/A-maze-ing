install:
		pip install build pydantic
		python3 -m build

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