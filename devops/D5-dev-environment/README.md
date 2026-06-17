# Overview

Evaluation task **D5** documents and implements the reproducible development environment for this monorepo.

**Single command from a fresh clone:**

```bash
make bootstrap
```

This installs [mise](https://mise.jdx.dev) (if needed), pins runtimes, installs all project dependencies, and runs the full test suite.

See also: [`docs/DEV_ENVIRONMENT_REPORT.md`](docs/DEV_ENVIRONMENT_REPORT.md)

# Prerequisites

Only these must exist on a clean machine before `make bootstrap`:

| Tool | Purpose |
|------|---------|
| `git` | Clone repository |
| `curl` | Install mise |
| `make` | Bootstrap entrypoint |

Everything else (Python, Node, Rust, Terraform, ruff) is installed by mise.

# Fresh Clone Setup

```bash
git clone <repo-url> Evil-Ai
cd Evil-Ai
make bootstrap
```

# Run Tests

```bash
make test
```

# Other Targets

```bash
make help      # list targets
make install   # deps only (no tests)
make lint      # ruff + cargo fmt/clippy
make clean     # remove node_modules caches
make versions  # show pinned runtime versions
```

# Troubleshooting

| Issue | Fix |
|-------|-----|
| `mise: command not found` | `export PATH="$HOME/.local/bin:$PATH"` |
| Wrong Python/Node version | `mise install` then `make install` |
| A3 Node tests fail | Ensure `make install` built Rust release binary |
| `npm ci` fails | Delete `node_modules` and re-run `make install` |
| Slow first bootstrap | Normal — downloads ~200MB of toolchains |

# Supported Versions

From [`mise.toml`](../../../mise.toml):

- Python **3.11.11**
- Node **20.18.1**
- Rust **1.84.1**
- Terraform **1.9.8**
