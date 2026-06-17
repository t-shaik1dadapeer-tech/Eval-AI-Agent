# I6 — Root Cause Analysis

**Bug:** Colon-delimited log lines not counted  
**Component:** `beginner/B6-rust-cli`  
**Branch:** `bugfix/I6-diagnosis-fix`

---

# Root Cause

| Field | Value |
|-------|-------|
| **File path** | `beginner/B6-rust-cli/src/analyzer.rs` |
| **Function** | `matches_log_level` |
| **Called from** | `count_log_levels` |

## Responsible code (before fix)

```16:21:beginner/B6-rust-cli/src/analyzer.rs
fn matches_log_level(line: &str, level: &str) -> bool {
    match line.strip_prefix(level) {
        None => false,
        Some(rest) => rest.is_empty() || rest.starts_with(' '),
    }
}
```

---

# Why It Happened

1. I3 introduced `matches_log_level` to prevent false positives (e.g. `INFORMATION` matching `INFO`).
2. The delimiter check only allowed **end-of-line** or **space** after the level token.
3. Many log formats use **colon** as delimiter: `INFO: Application started`.
4. For input `INFO: Application started`:
   - `strip_prefix("INFO")` → rest = `": Application started"`
   - `rest.is_empty()` → false
   - `rest.starts_with(' ')` → false (starts with `:`)
   - **Result: no match** → line skipped

---

# Trigger Conditions

| Condition | Example |
|-----------|---------|
| Line starts with valid level token | `INFO`, `WARN`, `ERROR` |
| Delimiter after token is `:` | `INFO: message` |
| Not space or EOL delimiter | `INFO message` works; `INFO: message` fails |

---

# Affected Components

| Component | Impact |
|-----------|--------|
| `count_log_levels` | Returns zero counts for colon-format files |
| `format_summary` / CLI output | Misleading summary |
| `logs/colon-format.log` | New reproduction fixture (added in I6) |

**Not affected:** Space-delimited logs (`logs/sample.log`), false-positive filtering (`INFORMATION`, `ERROR_HANDLER`).

---

# Supporting Evidence

## Trace for `INFO: Application started`

```
trimmed = "INFO: Application started"
matches_log_level(trimmed, "INFO")
  strip_prefix("INFO") → Some(": Application started")
  rest.is_empty() → false
  rest.starts_with(' ') → false
  return false  ← BUG
```

## I3 change introduced strict space-only delimiter

I3 `CHANGE_REPORT.md` documented intentional trade-off:

> Logs using non-standard prefixes without space delimiter (e.g. `INFO:msg`) would no longer match

I6 confirms this was a real gap, not just theoretical.

## Reproduction command output

```
INFO: 0
WARN: 0
ERROR: 0
```

for three valid colon-format log lines.

---

# Confidence

| Aspect | Level |
|--------|-------|
| Root cause identified | **Confirmed** |
| Code path traced | **Confirmed** |
| Reproduced before fix | **Confirmed** |
