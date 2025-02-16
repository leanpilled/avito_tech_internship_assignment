lint:
	uv run ruff check --config pyproject.toml -n

format:
	uv run ruff check --fix --config pyproject.toml -n
	uv run ruff format

test:
	uv run pytest --cov=. --cov-report=term
