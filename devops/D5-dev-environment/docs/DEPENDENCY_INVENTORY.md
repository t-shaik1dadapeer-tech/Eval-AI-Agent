# Languages

| Language | Services | Test runner |
|----------|----------|-------------|
| Python 3.11 | B4, I4 FastAPI, A3 FastAPI | pytest |
| Node.js 20 | B5 API, I4 CLI, A3 worker | jest |
| Rust 1.84 | B6 log analyzer, A3 fraud engine | cargo test |
| HCL | D1 Terraform (optional track) | terraform validate |

---

# Runtime Versions

Pinned in [`mise.toml`](../../../mise.toml) (repo root):

| Tool | Pinned version | CI reference |
|------|----------------|--------------|
| Python | **3.11.11** | `.github/workflows/ci.yml` → `3.11` |
| Node.js | **20.18.1** | `.github/workflows/ci.yml` → `20` |
| Rust | **1.84.1** | `dtolnay/rust-toolchain@stable` |
| Terraform | **1.9.8** | `devops/D1-terraform` docs |

**Optional (not pinned in mise — track-specific):**

| Tool | Version | Used by |
|------|---------|---------|
| Docker | 27+ | D2, D3, D4 |
| kind | 0.27+ | D4 |
| kubectl | 1.29+ | D4 |

---

# Package Managers

| Ecosystem | Manager | Lock file | Services |
|-----------|---------|-----------|----------|
| Python | pip | `requirements.txt` per service | B4, I4, A3 fastapi |
| Node | npm | `package-lock.json` | B5, I4 client, A3 worker |
| Rust | cargo | `Cargo.lock` (generated on build) | B6, A3 engine |
| Dev lint | pip | `requirements-dev.txt` (root) | ruff |

---

# System Packages

| Package | Required for bootstrap? | Notes |
|---------|-------------------------|-------|
| `curl` | Yes | Installs mise |
| `git` | Yes | Clone repo |
| `make` | Yes | Bootstrap entrypoint |
| `bash` | Yes | Scripts |
| C compiler toolchain | Transitive | Rust/Python wheels on some platforms |
| Docker | No (optional) | D2/D3/D4 only |

---

# Environment Variables

| Variable | Required | Set by | Purpose |
|----------|----------|--------|---------|
| `FRAUD_SYSTEM_ROOT` | A3 Node tests | `mise.toml` `[env]` | Root path to A3 polyglot system |
| `RUST_ENGINE_BIN` | A3 Node tests | `mise.toml` `[env]` | Path to built `fraud-engine` binary |
| `PATH` | mise | `~/.local/bin` after mise install | Access to mise shims |

---

# Previously Implicit Dependencies

| Dependency | Why required | Where discovered |
|------------|--------------|------------------|
| **Python 3.11** | FastAPI services and pytest | `ci.yml`, `requirements.txt` |
| **Node 20** | Jest tests for 3 Node projects | `ci.yml`, `package.json` scripts |
| **Rust stable** | B6 + A3 engine tests; A3 worker needs release binary | `ci.yml`, `ci-verify.sh` |
| **`FRAUD_SYSTEM_ROOT`** | A3 worker resolves queue/data paths | `ci.yml` env block, A5 review |
| **`RUST_ENGINE_BIN`** | Node worker spawns Rust CLI | `ci.yml`, `node-worker` tests |
| **A3 Rust release build** | Must exist before Node worker tests | `ci-verify.sh` line 31 |
| **npm ci** | Reproducible Node installs | `package-lock.json` presence |
| **pip** | Python dep install per service | All `requirements.txt` |
| **ruff** | D3 lint for B4 | `d3-ci.yml`, `pyproject.toml` |
| **Terraform 1.9.8** | D1 infrastructure track | `devops/D1-terraform` reports |
| **Docker** | D2 compose, D3 image build, D4 kind | Dockerfiles, D2/D3/D4 READMEs |
| **kind + kubectl** | D4 Kubernetes deploy | `D4-kubernetes-deployment` |
| **mise** | Not previously documented | Introduced by D5 to pin all runtimes |
| **make** | Not previously documented | Introduced by D5 as single entrypoint |
| **System Python/Node in PATH** | Assumed pre-installed | Implicit before D5 — replaced by mise |
