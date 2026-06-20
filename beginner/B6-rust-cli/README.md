# B6 — Rust Log Analyzer CLI

Command-line tool that reads a log file and counts `INFO`, `WARN`, and `ERROR` entries.

## Project overview

| Component | Description |
|-----------|-------------|
| Language | Rust (edition 2021) |
| Build tool | Cargo |
| Binary | `log-analyzer` |
| Library | `b6_rust_log_analyzer` (shared logic for tests) |

## Folder structure

```
B6-rust-cli/
├── src/
│   ├── main.rs        # CLI entry point
│   ├── lib.rs         # Library root
│   ├── analyzer.rs    # Log parsing and counting
│   └── errors.rs      # Error types and file I/O
├── tests/
│   └── log_analyzer_test.rs
├── logs/
│   ├── sample.log
│   └── empty.log
├── Cargo.toml
├── README.md
└── .gitignore
```

## Installation

Requires [Rust](https://www.rust-lang.org/tools/install) (Cargo 1.70+).

```bash
rustc --version
cargo --version
```

## Build

```bash
cd beginner/B6-rust-cli
cargo build
```

Release build:

```bash
cargo build --release
```

## Run

```bash
cargo run -- logs/sample.log
```

**Example output:**

```
## Log Summary

INFO: 3
WARN: 1
ERROR: 1
```

### Missing file

```bash
cargo run -- logs/missing.log
```

**Example output (stderr):**

```
Error: File not found: logs/missing.log
```

Exit code: `1`

## Test

```bash
cargo test
```

Expected: **17 passed** (9 unit tests in `analyzer.rs`, 8 integration tests in `tests/`).

## Example log file

`logs/sample.log`:

```
INFO Application started
INFO User authenticated
WARN Rate limit approaching
ERROR Database connection failed
INFO Request processed
```

## Log level detection

Lines are counted when they **start with** (after trimming whitespace):

- `INFO`
- `WARN`
- `ERROR`

Blank lines are ignored. Other lines are not counted.

## Error handling

| Condition | Message | Exit code |
|-----------|---------|-----------|
| Missing CLI argument | `Error: missing file path argument` | 1 |
| File not found | `Error: File not found: <path>` | 1 |
| Permission denied | `Error: Permission denied reading file: <path>` | 1 |
| Other read failure | `Error: Failed to read file <path>: <reason>` | 1 |
| Empty file | Valid — all counts `0` | 0 |
