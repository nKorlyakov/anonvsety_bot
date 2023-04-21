install:
	pip install poetry && \
	poetry install
	
start:
	poetry run python anonvsety_bot/main.py