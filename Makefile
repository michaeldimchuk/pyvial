modules = vial tests

init:
	poetry install
	poetry run pre-commit install

test:
	coverage run -m pytest
	coverage report -m --precision 2

lint:
	isort --check $(modules)
	black --quiet --check $(modules)
	flake8 $(modules)
	pylint $(modules)
	mypy --show-error-codes --strict $(modules)
	bandit -rqs B101,B404,B603,B311 $(modules)

format:
	isort $(modules)
	black $(modules)
