# A6 — Optimization Summary

---

## Files changed

| File | Change |
|------|--------|
| `beginner/B6-rust-log-analyzer/src/analyzer.rs` | Optimized `count_log_levels` hot loop |
| `beginner/B6-rust-log-analyzer/src/bin/count_bench.rs` | **Added** — repeatable benchmark harness |
| `beginner/B6-rust-log-analyzer/Cargo.toml` | Registered `count-bench` binary |

**Lines changed in `analyzer.rs`:** ~45 lines (refactor of loop + 3 helper functions)

---

## Diff summary

### Added helpers

- `line_needs_trim()` — O(1) check of first/last byte for ASCII whitespace
- `normalize_line()` — calls `trim()` only when needed
- `classify_log_level()` — first-byte dispatch (`I`/`W`/`E`) before prefix match
- `LogLevelKind` enum — internal classification only

### Removed pattern

```rust
// BEFORE: unconditional trim + up to 3 prefix checks
let trimmed = line.trim();
if matches_log_level(trimmed, "INFO") { ... }
else if matches_log_level(trimmed, "WARN") { ... }
else if matches_log_level(trimmed, "ERROR") { ... }
```

### New pattern

```rust
// AFTER: conditional trim + single classification path
let normalized = normalize_line(line);
match classify_log_level(normalized) { ... }
```

---

## Rationale

| Decision | Why |
|----------|-----|
| Conditional trim | Typical log lines have no outer whitespace — avoid redundant scans |
| First-byte dispatch | Reject non-matching lines with one byte comparison |
| Single `matches_log_level` call | At most one prefix check per line vs up to three |
| No architecture change | Same public API, same counting semantics |
| No new dependencies | Pure std library |

---

## What was NOT changed

- Public function signatures
- `matches_log_level` delimiter rules (space/colon/end)
- CLI (`main.rs`) or file reading
- Test expectations (all 17 tests pass)

---

## Rollback

```bash
git checkout HEAD~1 -- beginner/B6-rust-log-analyzer/src/analyzer.rs
```

Or revert commit containing A6 optimization.
