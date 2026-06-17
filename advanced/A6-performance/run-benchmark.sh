#!/usr/bin/env bash
# Reproduce A6 benchmark for B6 log analyzer
set -euo pipefail
cd "$(dirname "$0")/../../beginner/B6-rust-log-analyzer"
CARGO_TARGET_DIR=./target cargo build --release --bin count-bench -q
BENCH_LINES="${BENCH_LINES:-1000000}" BENCH_RUNS="${BENCH_RUNS:-5}" ./target/release/count-bench
