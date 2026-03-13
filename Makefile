.PHONY: help venv install build run run-extract run-materialize run-serve test lint format clean version version-increment push

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

venv: ## Create virtual environment using uv
	uv venv

install: ## Install all dependencies (including dev)
	uv sync --extra dev

build: ## Build the package
	uv build

run: ## Run the MCP context server (set DB_PATH env var or pass ARGS)
	uv run holocron-serve $(ARGS)

run-extract: ## Run the Plex extractor (pass ARGS="--dir /path --plex-token TOKEN")
	uv run holocron-extract $(ARGS)

run-materialize: ## Run the NFO materializer (pass ARGS="--dir /path")
	uv run holocron-materialize $(ARGS)

run-serve: ## Run the MCP context server
	uv run holocron-serve $(ARGS)

test: ## Run tests with pytest
	uv run pytest tests/ -v --tb=short

lint: ## Lint source code with ruff
	uv run ruff check src/ tests/

format: ## Format source code with ruff
	uv run ruff format src/ tests/

clean: ## Remove build artifacts and caches
	rm -rf .venv dist __pycache__ .pytest_cache .ruff_cache *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.duckdb" -delete 2>/dev/null || true
	find . -name "*.duckdb.wal" -delete 2>/dev/null || true

version: ## Display the current version from pyproject.toml
	@grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'

version-increment: ## Bump the patch version in pyproject.toml
	@VERSION=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/') && \
	MAJOR=$$(echo $$VERSION | cut -d. -f1) && \
	MINOR=$$(echo $$VERSION | cut -d. -f2) && \
	PATCH=$$(echo $$VERSION | cut -d. -f3) && \
	NEW_PATCH=$$((PATCH + 1)) && \
	NEW_VERSION="$$MAJOR.$$MINOR.$$NEW_PATCH" && \
	sed -i "s/^version = \"$$VERSION\"/version = \"$$NEW_VERSION\"/" pyproject.toml && \
	echo "Bumped $$VERSION → $$NEW_VERSION"

push: format lint test ## Format, lint, test, bump patch version, commit, push, and tag
	@VERSION=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/') && \
	MAJOR=$$(echo $$VERSION | cut -d. -f1) && \
	MINOR=$$(echo $$VERSION | cut -d. -f2) && \
	PATCH=$$(echo $$VERSION | cut -d. -f3) && \
	NEW_PATCH=$$((PATCH + 1)) && \
	NEW_VERSION="$$MAJOR.$$MINOR.$$NEW_PATCH" && \
	sed -i "s/^version = \"$$VERSION\"/version = \"$$NEW_VERSION\"/" pyproject.toml && \
	echo "Bumped $$VERSION → $$NEW_VERSION" && \
	git add -A && \
	git commit -m "release: v$$NEW_VERSION.  $$(gitsum)" && \
	git push && \
	git tag v$$NEW_VERSION && \
	git push --tags && \
	echo "Released v$$NEW_VERSION"
