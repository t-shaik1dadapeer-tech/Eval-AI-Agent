# Executive Summary

Task **D5** makes the Eval-Ai monorepo reproducible from a fresh clone using **Makefile + mise** (Option A). A developer runs `make bootstrap` to install pinned language runtimes, project dependencies, and execute the full CI-equivalent test suite.

Verification on 2026-06-17: **`make bootstrap` exit 0**, **`make test` exit 0** (47 tests across Python, Rust, and Node), **`make lint` exit 0**.

---

# Selected Bootstrap Strategy

**Option A: Makefile + mise**

| Criterion | Why mise |
|-----------|----------|
| Polyglot repo | Single file pins Python, Node, Rust, Terraform |
| Simplicity | Lighter than Nix; no IDE lock-in like devcontainers |
| CI alignment | Versions match `.github/workflows/ci.yml` |
| Clean machine | `install-mise.sh` bootstraps mise via curl |
| Developer UX | `make bootstrap` is one memorable command |

**Not chosen:**

- **asdf** — similar to mise but mise has unified env var support in `mise.toml`
- **devcontainer** — heavier; Docker required upfront
- **Nix flake** — steeper learning curve for eval repo

---

# Files Added

| File | Purpose |
|------|---------|
| `Makefile` | `bootstrap`, `install`, `test`, `lint`, `clean`, `help`, `versions` |
| `mise.toml` | Pinned tool versions + A3 env vars |
| `requirements-dev.txt` | Root dev deps (ruff) |
| `scripts/install-mise.sh` | Idempotent mise installer |
| `scripts/install-deps.sh` | mise install + pip/npm/cargo |
| `scripts/lint.sh` | ruff + cargo fmt/clippy |
| `scripts/ci-verify.sh` | Updated to use `mise exec` |
| `devops/D5-dev-environment/docs/*` | Inventory, verification, this report |

---

# Environment Reproducibility Improvements

| Before D5 | After D5 |
|-----------|----------|
| Undocumented Python/Node/Rust versions | Pinned in `mise.toml` |
| Manual per-service `pip install` / `npm ci` | `make install` installs all |
| Hidden `FRAUD_SYSTEM_ROOT` / `RUST_ENGINE_BIN` | Set in `mise.toml` `[env]` |
| CI script used system PATH tools | `mise exec` ensures pinned versions |
| No single entrypoint | `make bootstrap` |
| Lint scattered | `make lint` |

---

# Verification Results

| Command | Exit code | Result |
|---------|-----------|--------|
| `make bootstrap` | 0 | Install + all tests pass |
| `make test` | 0 | 47 tests passed |
| `make lint` | 0 | ruff + clippy clean |
| `make versions` | 0 | Shows mise-pinned versions |

**Test breakdown:**

- Python pytest: **15** tests (8 + 4 + 3)
- Rust cargo test: **20** tests (B6 + A3)
- Node jest: **12** tests (5 + 5 + 2)

---

# Remaining Manual Steps

| Step | When needed |
|------|-------------|
| Add `~/.local/bin` to PATH | First mise install (if not in profile) |
| `eval "$(mise activate zsh)"` | Interactive shell convenience |
| Install Docker Desktop | D2, D3, D4 tracks only |
| AWS credentials | D1 `terraform apply` only |

Bootstrap covers **all automated test suites** in the repo; DevOps deploy tracks remain optional.

---

# Future Improvements

1. **Lock Python deps** — add `requirements.lock` or uv/poetry per service
2. **Pre-commit hook** — run `make lint` on commit
3. **CI mise integration** — use `jdx/mise-action` in GitHub Actions for exact parity
4. **devcontainer** — optional for teams wanting Docker-isolated dev
5. **Cache volumes** — document mise cache location for faster re-bootstrap

---

# Previously Implicit Requirements (now explicit)

See [`DEPENDENCY_INVENTORY.md`](DEPENDENCY_INVENTORY.md) for the full table. Highlights:

- A3 integration requires **release Rust binary** before Node tests
- **Environment variables** `FRAUD_SYSTEM_ROOT` and `RUST_ENGINE_BIN` were only in CI YAML
- **npm ci** requires committed `package-lock.json` files
- **Terraform/Docker/kind** assumed for DevOps tasks but not core bootstrap
