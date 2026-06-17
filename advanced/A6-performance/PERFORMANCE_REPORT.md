# A6 — Performance Report

**Date:** 2026-06-17  
**Output:** `advanced/A6-performance/`

---

# Executive Summary

Profiled and optimized **`count_log_levels()`** in the B6 Rust log analyzer. Baseline processing of **1,000,000 log lines** averaged **13.815 ms**; after optimization **12.318 ms** — a **10.8% improvement** (~**1.5 ms** saved per million lines). All **17 Rust tests** and full **CI suite (47 tests)** pass with unchanged behavior.

---

# Selected Component

| Field | Value |
|-------|-------|
| **Component** | `beginner/B6-rust-log-analyzer` — `count_log_levels()` |
| **File** | `src/analyzer.rs` |
| **Why selected** | CPU-bound hot loop over every log line; easy to benchmark in isolation; clear per-line overhead |

### Selection criteria met

| Criterion | Evidence |
|-----------|----------|
| Measurable runtime | 1M lines → ~14ms (measurable with millisecond precision) |
| Easy to benchmark | In-memory string, no network/DB |
| Clear optimization opportunity | Unconditional `trim()` + triple prefix checks per line |

---

# Baseline Measurement

## Methodology

1. Build release benchmark binary: `cargo build --release --bin count-bench`
2. Generate 1,000,000 synthetic log lines in memory (70% INFO, 20% WARN, 10% ERROR)
3. Warm-up: one `count_log_levels` call
4. Run **5 timed iterations**, record milliseconds per run
5. Environment: macOS, Rust release profile, `BENCH_LINES=1000000`

## Commands

```bash
cd beginner/B6-rust-log-analyzer
CARGO_TARGET_DIR=./target cargo build --release --bin count-bench
BENCH_LINES=1000000 BENCH_RUNS=5 ./target/release/count-bench
```

## Results (before optimization)

| Run | Time (ms) |
|-----|-----------|
| 1 | 13.808 |
| 2 | 13.817 |
| 3 | 14.008 |
| 4 | 13.715 |
| 5 | 13.726 |
| **Avg** | **13.815** |

**Throughput (before):** ~72.4 million lines/second (1,000,000 / 0.013815)

---

# Profiling Results

| Tool | Finding |
|------|---------|
| macOS `sample` | 364 samples in `count_log_levels` — dominates CPU |
| Code analysis | Per-line `trim()` + up to 3× `matches_log_level` |

See `profiling-analysis.md` for full evidence.

**Bottleneck:** Per-line string scanning and redundant prefix matching in the main counting loop.

---

# Root Cause

## What is slow?

The main loop in `count_log_levels` processes every line with:

1. **`line.trim()`** on every non-empty line — scans from both ends even when log lines are already normalized (`INFO message...`).
2. **Up to three `matches_log_level` calls** — non-matching lines attempt INFO, WARN, and ERROR sequentially.

## Why is it slow?

At **1M lines**, micro-per-line overhead accumulates:
- ~1M unnecessary end-of-line trim checks for typical logs
- ~300k extra prefix comparisons for lines not starting with `I`/`W`/`E`

## Why is it safe to optimize?

- Conditional trim preserves behavior for lines with leading/trailing whitespace (I3/I6 test cases)
- First-byte dispatch still delegates to `matches_log_level` — same delimiter rules
- All existing unit and integration tests verify semantic equivalence

---

# Optimization

| Field | Value |
|-------|-------|
| **File** | `beginner/B6-rust-log-analyzer/src/analyzer.rs` |
| **Change** | O(1) whitespace check before trim; first-byte dispatch before prefix match |
| **Rationale** | Target measured hot path without API or architecture changes |

See `optimization-summary.md` for diff details.

---

# After Measurement

Same methodology, same machine, same `BENCH_LINES=1000000`, 5 runs.

| Run | Time (ms) |
|-----|-----------|
| 1 | 12.761 |
| 2 | 12.260 |
| 3 | 12.262 |
| 4 | 12.370 |
| 5 | 11.937 |
| **Avg** | **12.318** |

## Comparison

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Avg runtime (1M lines) | 13.815 ms | 12.318 ms | **10.8% faster** |
| Absolute savings | — | — | **1.497 ms** |
| Throughput | 72.4 M lines/s | 81.2 M lines/s | **+12.1%** |

---

# Performance Improvement

| Measure | Value |
|---------|-------|
| **Percentage improvement** | **10.8%** |
| **Absolute improvement** | **1.497 ms** per 1M lines |

---

# Behavior Verification

## B6 unit + integration tests

```bash
cd beginner/B6-rust-log-analyzer && cargo test
```

**Result:** 17/17 passed (9 lib + 8 integration)

## Full repository CI

```bash
bash scripts/ci-verify.sh
```

**Result:** exit `0` — 47/47 tests passed

## Count correctness (after optimization)

Benchmark output confirms unchanged distribution:

```
info=700000 warn=200000 error=100000
```

Matches expected 70/20/10 synthetic mix.

---

# Deliverables

| File | Purpose |
|------|---------|
| `PERFORMANCE_REPORT.md` | This report |
| `benchmark-results.csv` | Before/after run times |
| `profiling-analysis.md` | Profiling evidence |
| `optimization-summary.md` | Code change summary |

## Reproduce benchmark

```bash
cd beginner/B6-rust-log-analyzer
cargo build --release --bin count-bench
BENCH_LINES=1000000 BENCH_RUNS=5 ./target/release/count-bench
```
