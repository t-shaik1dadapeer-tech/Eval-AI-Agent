# Evil-Ai — reproducible development environment

SHELL := /bin/bash
ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
export PATH := $(HOME)/.local/bin:$(PATH)
PORT ?= 8788

.PHONY: help bootstrap install install-mise test lint clean verify versions \
	setup build-skills build-blueprints install-cursor-skills validate-dag \
	eval eval-full eval-dashboard eval-api eval-stop run-pipeline run-all run-all-tests \
	eval-compare eval-metrics eval-orch-config eval-reset-config

help: ## Show targets
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

setup: build-blueprints build-skills validate-dag ## Blueprints + skills + DAG check
	@echo "Run: make install-cursor-skills  then  make eval-api"

build-blueprints: ## Generate eval_blueprints/*.md from registry
	@python3 "$(ROOT)/scripts/eval/update_registry.py"
	@python3 "$(ROOT)/scripts/eval/generate_blueprints.py"

build-skills: build-blueprints ## Build skills/*.skill.md
	@python3 "$(ROOT)/scripts/build_skills.py"

install-cursor-skills: build-skills ## Install skills to ~/.cursor/skills/
	@python3 "$(ROOT)/tools/install_cursor_skills.py"

validate-dag: ## Validate task depends_on graph
	@python3 "$(ROOT)/scripts/eval/validate_dag.py"

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

eval: ## Verify all 24 task deliverables (writes docs/eval-status.json)
	@python3 "$(ROOT)/scripts/eval/portfolio.py" verify

eval-full: ## Deliverables + run verify_command for all tasks (needs Docker)
	@python3 "$(ROOT)/scripts/eval/portfolio.py" verify --run-tests --run-docker

eval-dashboard: ## Print live portfolio dashboard URL (run make eval-api)
	@echo "Evil-Ai portfolio — http://127.0.0.1:$(PORT)/"
	@echo "Start server: make eval-api"

eval-api: ## Start live eval API + portfolio dashboard http://127.0.0.1:8788
	@python3 "$(ROOT)/scripts/eval/portfolio.py" serve --port $(PORT)

eval-stop: ## Stop eval portfolio server on port 8788
	@lsof -ti :$(PORT) | xargs kill 2>/dev/null || echo "No process on $(PORT)"

run-pipeline: ## Print pipeline plan JSON
	@python3 "$(ROOT)/scripts/eval/portfolio.py" pipeline

run-all: ## Verify all 24 pipeline tasks
	@python3 "$(ROOT)/scripts/eval/portfolio.py" run-all

run-all-tests: ## Verify all 24 + run verify_command per task
	@python3 "$(ROOT)/scripts/eval/portfolio.py" run-all --run-tests

eval-compare: ## Compare agent output: make eval-compare TASK=I2 AGENT_OUTPUT=./out.md
	@test -n "$(TASK)" || (echo "Usage: make eval-compare TASK=B2 AGENT_OUTPUT=./file.md" && exit 1)
	@python3 "$(ROOT)/scripts/eval/portfolio.py" compare "$(TASK)" $(if $(AGENT_OUTPUT),--agent-output "$(AGENT_OUTPUT)",) --agent-name "$(or $(AGENT_NAME),manual)" $(if $(API_BASE_URL),--api-base-url "$(API_BASE_URL)",)

eval-metrics: eval ## Prometheus metrics for eval portfolio
	@python3 "$(ROOT)/scripts/eval/portfolio.py" metrics

eval-orch-config: ## Register API + eval config
	@python3 "$(ROOT)/scripts/eval/portfolio.py" orch-config $(if $(API_ID),--api-id "$(API_ID)",) $(if $(API_BASE_URL),--api-base-url "$(API_BASE_URL)",) $(if $(PROJECT_NAME),--project-name "$(PROJECT_NAME)",)

eval-reset-config: ## Reset .eval/eval-config.json
	@bash "$(ROOT)/scripts/eval/reset-orchestrator-config.sh"

versions: ## Print pinned and active tool versions
	@command -v mise >/dev/null 2>&1 && mise current || echo "mise not installed"
	@command -v mise >/dev/null 2>&1 && mise exec -- python --version || true
	@command -v mise >/dev/null 2>&1 && mise exec -- node --version || true
	@command -v mise >/dev/null 2>&1 && mise exec -- cargo --version || true
	@command -v mise >/dev/null 2>&1 && mise exec -- terraform version 2>/dev/null | head -1 || true
