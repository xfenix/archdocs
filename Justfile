default: install lint test

install:
  uv lock --upgrade
  uv sync --all-extras --frozen

lint:
  uv run ruff format
  uv run ruff check --fix
  uv run auto-typing-final fastarch tests/*.py
  uv run mypy .
  uv run flake8 --select=WPS --extend-exclude=tests/fastapi,tests/litestar fastarch tests
  uv run flake8 --select=COP --extend-exclude=tests/fastapi,tests/litestar fastarch tests

lint-ci:
  uv run ruff format --check
  uv run ruff check --no-fix
  uv run auto-typing-final --check fastarch tests/*.py
  uv run mypy .
  uv run flake8 --select=COP --extend-exclude=tests/fastapi,tests/litestar fastarch tests

test *args:
  uv run --no-sync pytest {{ args }}

publish:
  rm -rf dist
  uv build
  uv publish --token $PYPI_TOKEN
