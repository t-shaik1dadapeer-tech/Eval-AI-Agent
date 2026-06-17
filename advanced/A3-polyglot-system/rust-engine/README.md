# A3 Rust Fraud Engine

CLI that scores transaction risk from JSON input.

## Build

```bash
cd advanced/A3-polyglot-system/rust-engine
cargo build --release
```

## Usage

```bash
echo '{"amount":15000,"merchant":"electronics","country":"IN"}' | ./target/release/fraud-engine
```

Output:

```json
{"risk_score":82,"risk_level":"HIGH"}
```

## Scoring rules

| Rule | Points |
|------|--------|
| `amount > 10000` | +50 |
| `merchant == electronics` (case-insensitive) | +20 |
| `country != IN` (foreign) | +30 |
| `amount >= 15000` | +12 |

| Score | Level |
|-------|-------|
| 0–30 | LOW |
| 31–70 | MEDIUM |
| 71+ | HIGH |

## Test

```bash
cargo test
```
