# Evil-Ai — reproducible development environment
# Strategy: Makefile + mise (Option A)

SHELL := /bin/bash
ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
export PATH := $(HOME)/.local/bin:$(PATH)

.PHONY: help bootstrap install install-mise test lint clean verify versions

help: ## Show targets
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

bootstrap: install test ## Install everything and run tests (fresh-clone entrypoint)

install: install-mise ## Install mise runtimes and project dependencies
	@bash "$(ROOT)/scripts/install-deps.sh"

install-mise: ## Install mise version manager if missing
	@bash "$(ROOT)/scripts/install-mise.sh"
	@command -v mise >/dev/null 2>&1 || (echo "Add ~/.local/bin to PATH and re-run make bootstrap" && exit 1)

test: ## Run full test suite (mirrors CI)
	@bash "$(ROOT)/scripts/ci-verify.sh"

lint: ## Run linters (ruff, cargo fmt/clippy)
	@bash "$(ROOT)/scripts/lint.sh"

clean: ## Remove node_modules and caches (keeps Cargo target/)
	@find "$(ROOT)" -name node_modules -type d -prune -exec rm -rf {} + 2>/dev/null || true
	@rm -rf "$(ROOT)/.venv" "$(ROOT)/.ruff_cache"
	@echo "clean complete (cargo target/ retained for A3 integration tests)"

verify: bootstrap ## Alias for bootstrap (install + test)

versions: ## Print pinned and active tool versions
	@command -v mise >/dev/null 2>&1 && mise current || echo "mise not installed"
	@command -v mise >/dev/null 2>&1 && mise exec -- python --version || true
	@command -v mise >/dev/null 2>&1 && mise exec -- node --version || true
	@command -v mise >/dev/null 2>&1 && mise exec -- cargo --version || true
	@command -v mise >/dev/null 2>&1 && mise exec -- terraform version 2>/dev/null | head -1 || true
