# A6 — Profiling Analysis

**Component:** `beginner/B6-rust-cli` — `count_log_levels()`  
**Date:** 2026-06-17

---

## Profiling approach

| Step | Tool | Purpose |
|------|------|---------|
| 1 | Custom `count-bench` binary | Repeatable in-process timing of `count_log_levels` on 1M lines |
| 2 | macOS `sample` | CPU stack sampling during long benchmark run |
| 3 | Code inspection | Identify per-line work in hot loop |

**Benchmark binary:** `beginner/B6-rust-cli/src/bin/count_bench.rs`  
**Build:** `cargo build --release --bin count-bench`  
**Run:** `BENCH_LINES=1000000 BENCH_RUNS=5 ./target/release/count-bench`

---

## Profiling command (macOS sample)

```bash
BENCH_LINES=5000000 BENCH_RUNS=20 ./target/release/count-bench &
BPID=$!
sleep 0.2
sample $BPID 1 -f /tmp/b6-profile-before.txt
wait $BPID
```

---

## Hot path evidence

### Sample output (before optimization)

```
Sample analysis of process ... written to file /tmp/b6-profile-before.txt
    b6_rust_log_analyzer::analyzer::count_log_levels  364 samples
```

**Interpretation:** ~100% of CPU time in `count_log_levels` during benchmark — no I/O, no allocation in bench harness after initial string build.

### Code hot path (before)

```rust
for line in content.lines() {
    let trimmed = line.trim();           // O(n) scan both ends, every line
    if matches_log_level(trimmed, "INFO") { ... }
    else if matches_log_level(trimmed, "WARN") { ... }
    else if matches_log_level(trimmed, "ERROR") { ... }
}
```

| Operation | Per-line cost (before) |
|-----------|------------------------|
| `line.trim()` | Scans start **and** end even when unnecessary |
| `matches_log_level` × up to 3 | Up to 3 `strip_prefix` calls for non-INFO lines |
| Non-matching lines | Always attempted INFO, then WARN, then ERROR |

---

## Bottleneck discovered

1. **Unconditional `trim()`** — For typical log lines (`INFO message...`) with no leading/trailing whitespace, `trim()` still validates both ends of every line.

2. **Sequential prefix checks** — Lines not starting with `I`/`W`/`E` still paid up to three prefix comparisons (e.g. `INFORMATION`, blank-adjacent noise).

3. **Scale** — At 1M lines, micro-per-line overhead accumulates to ~14ms total runtime.

---

## Why this is the bottleneck (not file I/O)

The benchmark calls `count_log_levels(&content)` on an in-memory `String` — `read_log_file` and `format_summary` are excluded. Profiling confirms time is dominated by `count_log_levels`.

---

## Post-optimization profile (expected)

After first-byte dispatch + conditional trim:
- Lines not starting with `I`/`W`/`E` exit after one byte check
- Typical lines skip full `trim()` scan
- At most **one** `matches_log_level` call per classifiable line

Measured improvement: **10.8%** average runtime reduction (see `benchmark-results.csv`).
