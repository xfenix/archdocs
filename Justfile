default: install lint test

install:
  uv lock --upgrade
  uv sync --all-extras --frozen

# Один список проверок на локалку и на пайплайн: `just lint` правит код на месте,
# `just lint check` тот же список только проверяет — этот режим и гоняет CI.
lint mode="fix":
  @{{ assert(mode =~ '^(fix|check)$', "usage: just lint [fix|check]") }}true
  uv run ruff format {{ if mode == "check" { "--check" } else { "" } }}
  uv run ruff check {{ if mode == "check" { "--no-fix" } else { "--fix" } }}
  uv run auto-typing-final {{ if mode == "check" { "--check" } else { "" } }} fastarch tests/*.py scripts/*.py
  uv run mypy .
  uv run flake8 --select=WPS,COP fastarch tests

test *args:
  uv run --no-sync pytest {{ args }}

# Html-отчёт покрытия для github pages и json бейджа для shields.io.
coverage: (test "--cov-report=html" "--cov-report=json")
  uv run --no-sync python scripts/generate-coverage-badge.py

# Песочница: FastAPI-приложение, которое отдаёт страницы fastarch по примерам из tests/.
# Диаграмма кэшируется на процесс, поэтому правки пакета и примеров видны за счёт --reload.
playground port="8000":
  uv run --no-sync uvicorn tests.playground:playground_app --reload --reload-dir fastarch --reload-dir tests --port {{ port }}

publish:
  rm -rf dist
  uv build
  uv publish --token $PYPI_TOKEN
