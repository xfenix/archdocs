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
  uv run auto-typing-final {{ if mode == "check" { "--check" } else { "" } }} fastarch tests/*.py
  uv run mypy .
  uv run flake8 --select=WPS,COP fastarch tests

test *args:
  uv run --no-sync pytest {{ args }}

publish:
  rm -rf dist
  uv build
  uv publish --token $PYPI_TOKEN
