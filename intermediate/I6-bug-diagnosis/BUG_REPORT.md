# I6 — Bug Report

**Repository:** `Eval-Ai`  
**Branch:** `bugfix/I6-diagnosis-fix`  
**Component:** B6 Rust Log Analyzer  
**Date:** 2026-06-17

---

# Executive Summary

| Field | Value |
|-------|-------|
| **Bug description** | Log lines using colon-delimited level format (`INFO: message`) are not counted |
| **Impact** | Under-reported INFO/WARN/ERROR counts; incorrect summary for common log formats |
| **Severity** | **Medium** — silent data loss (returns zero counts, no error) |

---

# Reproduction Steps

## Preconditions

- B6 log analyzer built (`cargo build`)
- Log file with colon-delimited entries

## Steps

1. Create a log file with colon format:

   ```bash
   printf 'INFO: Application started\nWARN: Rate limit\nERROR: Connection failed\n' > /tmp/colon-format.log
   ```

2. Run the analyzer:

   ```bash
   cd beginner/B6-rust-cli
   cargo run -- /tmp/colon-format.log
   ```

## Commands executed (before fix)

```bash
cargo run -- /tmp/colon-format.log
```

---

# Expected Behavior

```
## Log Summary

INFO: 1
WARN: 1
ERROR: 1
```

Each line starts with a valid level token (`INFO`, `WARN`, `ERROR`) followed by `:` and a message — standard format in many logging frameworks.

---

# Actual Behavior (before fix)

```
## Log Summary

INFO: 0
WARN: 0
ERROR: 0
```

All colon-delimited lines were **silently ignored**.

---

# Evidence

## CLI output (pre-fix, reproduced on `main`)

```
## Log Summary

INFO: 0
WARN: 0
ERROR: 0
EXIT:0
```

## Input file content

```
INFO: Application started
WARN: Rate limit
ERROR: Connection failed
```

## Contrast with space-delimited format (works correctly)

`logs/sample.log` uses space delimiter:

```
INFO Application started
```

Pre-fix output: `INFO: 3, WARN: 1, ERROR: 1` — correct.

## I3 documented limitation (foreshadowing)

I3 risk assessment noted colon format would not match:

> Custom format `INFO:details` (colon, no space) stops matching

---

# Candidate Bugs Considered

| # | Location | Issue | Selected |
|---|----------|-------|----------|
| 1 | B6 `matches_log_level` | Colon delimiter not accepted | **Yes** |
| 2 | I4 converter | Same-currency no rounding | No — cosmetic |
| 3 | B5 CLI | String amount rejection | No — by design |

---

# Post-Fix Verification

```bash
cargo run -- logs/colon-format.log
```

```
## Log Summary

INFO: 2
WARN: 1
ERROR: 1
```

```bash
cargo test
```

```
17 passed (9 unit + 8 integration)
TEST_EXIT:0
```
