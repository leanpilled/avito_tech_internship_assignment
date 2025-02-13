lint:
	uv run ruff check --config pyproject.toml -n
	uv run mypy .

format:
	uv run ruff check --fix --config pyproject.toml -n
	uv run ruff format
