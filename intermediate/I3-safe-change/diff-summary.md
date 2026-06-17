# I3 — Diff Summary

**Branch:** `feature/I3-safe-change`  
**Base:** `main` (commit `f083a2a`)

---

## Changed Files

| File | Change type |
|------|-------------|
| `beginner/B6-rust-cli/src/analyzer.rs` | Modified |
| `beginner/B6-rust-cli/tests/log_analyzer_test.rs` | Modified |

---

## Diff Overview

### `src/analyzer.rs`

- **Added** private helper `matches_log_level(line, level)` — requires level token + EOL or space
- **Modified** `count_log_levels` to use helper instead of `starts_with`
- **Added** 2 unit tests: `does_not_match_longer_level_prefixes`, `matches_level_token_followed_by_space`

### `tests/log_analyzer_test.rs`

- **Added** integration test `ignores_lines_with_level_prefix_substrings`

---

## Statistics

```
 beginner/B6-rust-cli/src/analyzer.rs      | 31 +++++++++++++++++++---
 beginner/B6-rust-cli/tests/log_analyzer_test.rs | 7 +++++
 2 files changed, 35 insertions(+), 3 deletions(-)
```

---

## Commit Summary

**Suggested message:**

```
I3: Small safe change with test coverage
```

**Scope:**

- Fix B6 log level false-positive matching
- Add 3 tests (2 unit, 1 integration)
- No changes to B4 FastAPI or B5 Node.js services
