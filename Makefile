install:
	pip install poetry && \
	poetry install
	
start:
	poetry run python src/main.py
