# B1 — Repository Artifact Inventory

**Repository:** `Evil-Ai` (Eval AI Agent scaffold)  
**Scan date:** 2026-06-17  
**Scanner scope:** Full recursive scan from repository root, excluding `.git/` internals  
**Task output:** `docs/beginner/B1-repo-artifact-inventory/`

---

## Executive Summary

A complete recursive scan of the `Evil-Ai` repository found **no application source code** and **zero artifacts** in any of the requested software categories (classes, interfaces, controllers, services, models/entities, repositories/DAOs, jobs, consumers/listeners, configuration classes, utilities, middleware/filters, or validators).

The repository is a **scaffold-only** project: it contains a root `README.md`, a root `.gitignore`, and **25** empty placeholder `.gitkeep` files across exercise track directories (`beginner/`, `intermediate/`, `advanced/`, `devops/`, `docs/`). No `.java`, `.py`, `.ts`, `.js`, `.go`, `.rs`, `.kt`, `.rb`, `.cs`, `.php`, `.xml`, `.yml`, `.yaml`, `.properties`, `.json`, or `.toml` source or configuration files were present at scan time.

**Conclusion:** This inventory documents the absence of implementable application artifacts. Future tasks (B4–B6, I4–I5, D1–D6, etc.) are expected to introduce code into their respective task folders; this report should be re-run after substantive code is added.

---

## Architecture Overview

```
Evil-Ai/                          ← Git repository root (branch: main)
├── README.md                     ← Project documentation (Confirmed)
├── .gitignore                    ← Git ignore rules (Confirmed)
├── docs/                         ← Documentation area (placeholder only)
├── beginner/                     ← 6 exercise slots (B1–B6), all empty
├── intermediate/                 ← 6 exercise slots (I1–I6), all empty
├── advanced/                     ← 6 exercise slots (A1–A6), all empty
└── devops/                       ← 6 exercise slots (D1–D6), all empty
```

**Observed architecture type:** Multi-track exercise monorepo scaffold (directory-based partitioning by skill level).  
**Runtime / deployment topology:** None — no services, containers, or infrastructure code present.  
**Primary languages detected:** None (0 source files).  
**Frameworks detected:** None.

### Evidence — repository purpose

```1:5:README.md
# Eval AI Agent

Hands-on exercises for evaluating AI coding agents across beginner, intermediate, advanced, and DevOps tracks.

Each subfolder is a self-contained task. Implement your solution inside the task folder, then commit and push when ready.
```

---

## Scan Methodology

| Step | Action | Result |
|------|--------|--------|
| 1 | `find . -type f` excluding `.git/` | **27** files total |
| 2 | Extension inventory | 25× `.gitkeep`, 1× `.md`, 1× `.gitignore` |
| 3 | Source file glob (`*.java`, `*.py`, `*.ts`, `*.js`, `*.go`, `*.rs`, `*.kt`, `*.rb`, `*.cs`, `*.php`) | **0** matches |
| 4 | Config file glob (`*.xml`, `*.yml`, `*.yaml`, `*.properties`, `*.json`, `*.toml`) | **0** matches |
| 5 | Pattern grep for `class`, `interface`, `@Controller`, `@Service`, `@Repository`, `@Entity`, `@Scheduled`, `@KafkaListener` | **0** application matches (only `*.class` in `.gitignore`) |

---

## Artifact Counts by Category

| Category | Count | Notes |
|----------|------:|-------|
| Classes | 0 | No source files |
| Interfaces | 0 | No source files |
| Controllers | 0 | No source files |
| Services | 0 | No source files |
| Models / Entities | 0 | No source files |
| Repositories / DAOs | 0 | No source files |
| Jobs / Scheduled tasks | 0 | No source files |
| Consumers / Listeners | 0 | No source files |
| Configuration classes | 0 | No source files |
| Utility / Helper classes | 0 | No source files |
| Middleware / Filters | 0 | No source files |
| Validators | 0 | No source files |
| **Total classified application artifacts** | **0** | |

### Non-application repository files (informational — outside requested categories)

| File | Path | Purpose | Confidence |
|------|------|---------|------------|
| README | `README.md` | Project overview and exercise workflow | Confirmed |
| Git ignore rules | `.gitignore` | Excludes build artifacts, env files, IDE dirs | Confirmed |
| Directory placeholders | `**/.gitkeep` (25 files) | Preserve empty exercise directories in Git | Confirmed |

---

## Detailed Inventory Table

No artifacts matched the requested software categories. The `inventory.csv` file contains headers only.

| Name | Category | File Path | Purpose | Key Dependencies | Confidence |
|------|----------|-----------|---------|----------------|------------|
| — | — | — | — | — | — |

*See `inventory.csv` for machine-readable export (header row, zero data rows).*

---

## Notable Findings

1. **Scaffold-only repository.** All exercise task directories exist but contain only `.gitkeep` placeholders — no implementations yet.

2. **B1 output location mismatch.** Task deliverables are written to `docs/beginner/B1-repo-artifact-inventory/` per requirements. The exercise slot folder `beginner/B1-repo-artifact-inventory/` still contains only `.gitkeep`.

3. **Pre-provisioned ignore rules.** `.gitignore` anticipates future polyglot development (Python, Node, Java, Go, Rust) but no corresponding source trees exist yet.

   ```19:29:.gitignore
   # Python
   __pycache__/
   *.py[cod]
   ...
   .ruff_cache/
   ```

4. **No build or CI artifacts.** No `pom.xml`, `package.json`, `requirements.txt`, `Cargo.toml`, `Dockerfile`, Terraform files, or pipeline definitions were found.

5. **No tests.** No test directories or test source files detected.

6. **No submodules or nested repositories.** `.git` is the sole version-control root; no `.gitmodules` file present.

---

## Areas Requiring Manual Verification

| # | Area | Reason |
|---|------|--------|
| 1 | Ignored paths | Files matching `.gitignore` patterns (e.g. `.env`, `node_modules/`, `target/`) are excluded from Git and were not present on disk during scan |
| 2 | Uncommitted local changes | Scan reflects working tree at analysis time; artifacts added but not saved to disk would be missed |
| 3 | External / submodule code | No submodules detected; if added later, re-scan required |
| 4 | Generated artifacts | Build outputs are gitignored; none were found locally |
| 5 | Intended target repository | If B1 was meant to analyze a different (external) application repo, this scaffold will not satisfy that intent — confirm evaluation target with task owner |

---

## Verification Summary

| Metric | Verified Value |
|--------|---------------:|
| Total files scanned (excl. `.git/`) | 27 |
| Total source code files | 0 |
| Total directories (excl. `.git/`) | 30 |
| **Total controllers** | **0** |
| **Total services** | **0** |
| **Total repositories** | **0** |
| **Total entities/models** | **0** |
| **Total jobs** | **0** |
| **Total consumers** | **0** |
| **Total config classes** | **0** |
| **Total utilities** | **0** |

---

## Appendix — Complete File Manifest

| # | Path | Type |
|---|------|------|
| 1 | `.gitignore` | Git configuration |
| 2 | `README.md` | Documentation |
| 3 | `docs/.gitkeep` | Placeholder |
| 4 | `beginner/B1-repo-artifact-inventory/.gitkeep` | Placeholder |
| 5 | `beginner/B2-api-endpoint-map/.gitkeep` | Placeholder |
| 6 | `beginner/B3-test-discovery/.gitkeep` | Placeholder |
| 7 | `beginner/B4-fastapi-service/.gitkeep` | Placeholder |
| 8 | `beginner/B5-nodejs-api-cli/.gitkeep` | Placeholder |
| 9 | `beginner/B6-rust-cli/.gitkeep` | Placeholder |
| 10 | `intermediate/I1-er-diagram/.gitkeep` | Placeholder |
| 11 | `intermediate/I2-end-to-end-trace/.gitkeep` | Placeholder |
| 12 | `intermediate/I3-safe-change/.gitkeep` | Placeholder |
| 13 | `intermediate/I4-fastapi-node-pair/.gitkeep` | Placeholder |
| 14 | `intermediate/I5-dockerize/.gitkeep` | Placeholder |
| 15 | `intermediate/I6-bug-diagnosis/.gitkeep` | Placeholder |
| 16 | `advanced/A1-parallel-plan/.gitkeep` | Placeholder |
| 17 | `advanced/A2-parallel-worktrees/.gitkeep` | Placeholder |
| 18 | `advanced/A3-polyglot-system/.gitkeep` | Placeholder |
| 19 | `advanced/A4-modernization/.gitkeep` | Placeholder |
| 20 | `advanced/A5-agent-review/.gitkeep` | Placeholder |
| 21 | `advanced/A6-performance/.gitkeep` | Placeholder |
| 22 | `devops/D1-terraform/.gitkeep` | Placeholder |
| 23 | `devops/D2-docker-compose/.gitkeep` | Placeholder |
| 24 | `devops/D3-ci-pipeline/.gitkeep` | Placeholder |
| 25 | `devops/D4-kubernetes/.gitkeep` | Placeholder |
| 26 | `devops/D5-dev-environment/.gitkeep` | Placeholder |
| 27 | `devops/D6-observability/.gitkeep` | Placeholder |
