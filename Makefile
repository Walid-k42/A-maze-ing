run:
		python3 a_maze_ing.py config.txt

clean:
		rm -rf __pycache__
		find . -type d -name "__pycache__" -exec rm -rf {} +
		find . -type f -name "*.pyc" -delete

lint:
		flake8 *.py
		mypy --strict *.py