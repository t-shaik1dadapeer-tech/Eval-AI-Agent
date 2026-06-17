# A3 Node.js Worker

Polls the file-based transaction queue, invokes the Rust fraud engine, and writes results to `processed_transactions.json`.

## Setup

```bash
cd advanced/A3-polyglot-system/node-worker
npm install
```

Build the Rust engine first:

```bash
cd ../rust-engine && cargo build --release
```

## Run

Continuous polling:

```bash
export FRAUD_SYSTEM_ROOT=/path/to/advanced/A3-polyglot-system
npm start
```

Single processing cycle (integration / testing):

```bash
npm run worker:once
```

## Test

```bash
npm test
```

## Environment variables

| Variable | Default |
|----------|---------|
| `FRAUD_SYSTEM_ROOT` | Parent A3 directory |
| `TRANSACTIONS_QUEUE_FILE` | `shared/data/transactions.json` |
| `PROCESSED_TRANSACTIONS_FILE` | `shared/data/processed_transactions.json` |
| `RUST_ENGINE_BIN` | `rust-engine/target/release/fraud-engine` |
| `WORKER_POLL_MS` | `2000` |
