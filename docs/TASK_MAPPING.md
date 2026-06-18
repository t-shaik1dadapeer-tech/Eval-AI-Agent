# Task Mapping

Maps each evaluation task ID to its purpose, expected deliverable type, and folder location.

## Beginner (B1–B6)

| Task | Name                    | Purpose                                      | Folder                              |
| ---- | ----------------------- | -------------------------------------------- | ----------------------------------- |
| B1   | Repository Analysis     | Scan repo; inventory artifacts by category   | `beginner/B1-repo-artifact-inventory/` |
| B2   | Endpoint Discovery      | Map HTTP/API routes across services          | `beginner/B2-api-endpoint-map/`        |
| B3   | Test Discovery          | Find test frameworks; run and report results | `beginner/B3-test-discovery/`          |
| B4   | FastAPI Service         | Build in-memory transaction REST API         | `beginner/B4-fastapi-service/`         |
| B5   | Node Service            | Mirror B4 with Express + CLI patterns        | `beginner/B5-nodejs-api-cli/`          |
| B6   | Rust Service            | CLI log analyzer with Cargo tests            | `beginner/B6-rust-cli/`                |

## Intermediate (I1–I6)

| Task | Name                    | Purpose                                      | Folder                              |
| ---- | ----------------------- | -------------------------------------------- | ----------------------------------- |
| I1   | ER Diagram              | Entity/relationship analysis of data model     | `intermediate/I1-er-diagram/`          |
| I2   | End-to-End Trace        | Document request flow across components      | `intermediate/I2-end-to-end-trace/`    |
| I3   | Safe Change             | Assess risk of a scoped code change          | `intermediate/I3-safe-change/`         |
| I4   | FastAPI + Node          | Currency API + Node CLI client pair          | `intermediate/I4-fastapi-node-pair/`   |
| I5   | Dockerize               | Containerize a service; document approach    | `intermediate/I5-dockerize/`           |
| I6   | Bug Diagnosis           | Root-cause analysis and fix documentation    | `intermediate/I6-bug-diagnosis/`       |

## Advanced (A1–A6)

| Task | Name                    | Purpose                                      | Folder                              |
| ---- | ----------------------- | -------------------------------------------- | ----------------------------------- |
| A1   | Parallel Planning       | Multi-agent / multi-branch execution plan    | `advanced/A1-parallel-plan/`           |
| A2   | Parallel Worktrees      | Git worktree workflow and merge report       | `advanced/A2-parallel-worktrees/`      |
| A3   | Polyglot System         | FastAPI → queue → Node worker → Rust scorer  | `advanced/A3-polyglot-system/`         |
| A4   | Modernization           | Legacy upgrade analysis and prioritization   | `advanced/A4-modernization/`           |
| A5   | Agent Review            | Structured code/agent review findings        | `advanced/A5-agent-review/`            |
| A6   | Performance             | Profiling, benchmarks, optimization report   | `advanced/A6-performance/`             |

## DevOps (D1–D6)

| Task | Name                    | Purpose                                      | Folder                              |
| ---- | ----------------------- | -------------------------------------------- | ----------------------------------- |
| D1   | Terraform               | IaC for AWS Lambda and supporting resources  | `devops/D1-terraform/`                 |
| D2   | Docker Compose          | Multi-service stack with Postgres + worker   | `devops/D2-docker-compose/`            |
| D3   | CI Pipeline             | Lint, test, build, Docker image pipeline     | `devops/D3-ci-pipeline/`               |
| D4   | Kubernetes              | K8s manifests and local validation           | `devops/D4-kubernetes/`                |
| D5   | Dev Environment         | Reproducible bootstrap (Makefile + mise)     | `devops/D5-dev-environment/`           |
| D6   | Observability           | JSON logs, Prometheus metrics, Grafana       | `devops/D6-observability/`             |

## Cross-task relationships

- **B4 / B5 / D6** — same transaction domain; D6 extends B4 with observability.
- **B1 ↔ B2 ↔ B3** — analysis tasks; kept consistent after 2026-06-18 refresh (108 artifacts, 25 routes, 47 tests in `make test`).
- **D5** — entry point for all automated tests (`make bootstrap`).
- **D6** — Grafana dashboards consume metrics from the D6 FastAPI service; see `DASHBOARD_VISION.md` for future unified dashboard ideas.
