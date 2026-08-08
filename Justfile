default: install lint test

install:
  uv lock --upgrade
  uv sync --all-extras --frozen

# One list of checks for local runs and for the pipeline: `just lint` fixes code in place,
# `just lint check` only verifies the same list — that is the mode CI runs.
lint mode="fix":
  #!/usr/bin/env sh
  set -e
  case "{{ mode }}" in
    fix|check) ;;
    *) echo "usage: just lint [fix|check]" && exit 1 ;;
  esac
  uv run ruff format {{ if mode == "check" { "--check" } else { "" } }}
  uv run ruff check {{ if mode == "check" { "--no-fix" } else { "--fix" } }}
  uv run auto-typing-final {{ if mode == "check" { "--check" } else { "" } }} archdocs tests/*.py scripts/*.py
  uv run mypy .
  uv run flake8 --select=WPS,COP archdocs tests
  uv run --no-sync python scripts/check-package-contents.py

test *args:
  uv run --no-sync pytest {{ args }}

# Coverage html report for github pages and the badge json for shields.io.
coverage: (test "--cov-report=html" "--cov-report=json")
  uv run --no-sync python scripts/generate-coverage-badge.py

# Badge json with the package's lines of code for shields.io.
lines:
  uv run --no-sync python scripts/generate-lines-badge.py

# Re-shoots `screenshot.png` for README from the showcase page — the same one the playground serves.
# The browser installs into the same .venv, so a repeated run downloads nothing.
screenshot:
  uv run --no-sync playwright install chromium
  PYTHONPATH=. uv run --no-sync python scripts/generate-architecture-screenshot.py

# Playground: a FastAPI application serving archdocs pages for the examples from tests/.
# The diagram is cached per process, so package and example edits show up thanks to --reload.
playground port="8000":
  uv run --no-sync uvicorn tests.playground:playground_app --reload --reload-dir archdocs --reload-dir tests --port {{ port }}

# Publishing to pypi: the version comes from the tag, auth via trusted publisher (OIDC).
publish version:
  uv version "{{ version }}"
  rm -rf dist
  uv build
  uv publish --trusted-publishing always
