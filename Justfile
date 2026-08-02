default: install lint test

install:
  uv lock --upgrade
  uv sync --all-extras --frozen

# Один список проверок на локалку и на пайплайн: `just lint` правит код на месте,
# `just lint check` тот же список только проверяет — этот режим и гоняет CI.
lint mode="fix":
  #!/usr/bin/env sh
  set -e
  case "{{ mode }}" in
    fix|check) ;;
    *) echo "usage: just lint [fix|check]" && exit 1 ;;
  esac
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

# Json бейджа со строками кода пакета для shields.io.
lines:
  uv run --no-sync python scripts/generate-lines-badge.py

# Пересъёмка `screenshot.png` для README со страницы showcase — той же, что даёт песочница.
# Браузер ставится сюда же, в .venv, и повторный запуск ничего не качает.
screenshot:
  uv run --no-sync playwright install chromium
  PYTHONPATH=. uv run --no-sync python scripts/generate-architecture-screenshot.py

# Песочница: FastAPI-приложение, которое отдаёт страницы fastarch по примерам из tests/.
# Диаграмма кэшируется на процесс, поэтому правки пакета и примеров видны за счёт --reload.
playground port="8000":
  uv run --no-sync uvicorn tests.playground:playground_app --reload --reload-dir fastarch --reload-dir tests --port {{ port }}

# Публикация в pypi: версия проставляется из тега, токен берётся из $PYPI_TOKEN.
publish version:
  uv version "{{ version }}"
  rm -rf dist
  uv build
  uv publish --token "$PYPI_TOKEN"
