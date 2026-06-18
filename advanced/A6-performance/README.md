# Task

A6 — Performance

# Objective

Profile performance hotspots and document benchmarks and optimizations.

# Deliverables

- `PERFORMANCE_REPORT.md` — analysis
- `profiling-analysis.md` — profiling notes
- `optimization-summary.md` — recommendations
- `benchmark-results.csv` — benchmark data
- `run-benchmark.sh` — reproducible benchmark script

# Status

Completed

# Verification

```bash
BENCH_LINES=100000 BENCH_RUNS=2 bash run-benchmark.sh
```

Run from repo root; script targets `beginner/B6-rust-cli`.
