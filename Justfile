default: install lint test
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

install:
    uv lock --upgrade
    uv sync --all-extras --frozen

lint:
    uv run ruff format
    uv run ruff check --fix
    uv run mypy .
    uv run flake8 --select=WPS --extend-exclude=tests/fastapi fastarch

lint-ci:
    uv run ruff format --check
    uv run ruff check --no-fix
    uv run mypy .

test *args:
    uv run --no-sync pytest {{ args }}

publish:
    rm -rf dist
    uv build
    uv publish --token $PYPI_TOKEN
