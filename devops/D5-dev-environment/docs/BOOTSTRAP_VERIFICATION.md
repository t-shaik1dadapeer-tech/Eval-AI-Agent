# Bootstrap Command

**Command:**

```bash
make bootstrap
```

Equivalent steps: `make install` then `make test`.

**Date:** 2026-06-17  
**Platform:** macOS arm64  
**Starting state:** mise not installed; system had ad-hoc Python 3.9 venv and Homebrew node

---

# Full Output

**Excerpt — mise install:**

```text
==> Installing mise...
mise: installed successfully to /Users/shaikdadapeer/.local/bin/mise
mise installed: 2026.6.11 macos-arm64 (2026-06-16)
```

**Excerpt — runtime install:**

```text
==> Installing pinned runtimes (mise)...
mise python@3.11.11 ✓ installed
mise node@20.18.1 ✓ installed
mise rust@1.84.1 ✓ installed
mise terraform@1.9.8 ✓ installed

==> Runtime versions
python 3.11.11
node 20.18.1
rust 1.84.1
terraform 1.9.8
```

**Excerpt — dependency install:**

```text
==> Python dependencies
--- beginner/B4-fastapi-service ---
--- intermediate/I4-polyglot-service-pair/fastapi-service ---
--- advanced/A3-polyglot-system/fastapi-service ---

==> Rust dependencies (fetch + release build for A3 node tests)
--- beginner/B6-rust-log-analyzer ---
--- advanced/A3-polyglot-system/rust-engine ---

==> Node dependencies
--- beginner/B5-nodejs-api ---
--- intermediate/I4-polyglot-service-pair/node-client ---
--- advanced/A3-polyglot-system/node-worker ---

==> Install complete
```

**Excerpt — test phase (end of bootstrap):**

```text
=== CI verification PASSED ===
```

**Full log:** captured at `/tmp/d5-bootstrap.log` during verification (≈4 min wall time including toolchain download).

---

# Result

| Step | Exit code | Status |
|------|-----------|--------|
| `install-mise.sh` | 0 | mise 2026.6.11 installed |
| `mise install` | 0 | 4 runtimes installed |
| `install-deps.sh` | 0 | Python/Node/Rust deps installed |
| `ci-verify.sh` (via `make test`) | 0 | All tests passed |

**Bootstrap result:** **SUCCESS**

---

# Test Execution

**Command:**

```bash
make test
```

**Output summary:**

| Suite | Service | Result |
|-------|---------|--------|
| Python | B4 | 8 passed |
| Python | I4 fastapi | 4 passed |
| Python | A3 fastapi | 3 passed |
| Rust | B6 | 17 passed (unit + integration) |
| Rust | A3 engine | 3 passed |
| Node | B5 | 5 passed |
| Node | I4 client | 5 passed |
| Node | A3 worker | 2 passed |

**Final line:**

```text
=== CI verification PASSED ===
```

**Exit code:** `0`

---

# Verification Summary

| Requirement | Met |
|-------------|-----|
| Single bootstrap command | `make bootstrap` |
| Runtime versions pinned | `mise.toml` |
| Dependencies installed automatically | `scripts/install-deps.sh` |
| Tests pass after bootstrap | 47 tests total, 0 failures |
| Implicit deps documented | `DEPENDENCY_INVENTORY.md` |
| Lint available | `make lint` → PASS |

**Post-bootstrap shell setup (recommended):**

```bash
echo 'eval "$(~/.local/bin/mise activate zsh)"' >> ~/.zshrc
```
