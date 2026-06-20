# A6 — Performance

## What to do

Reproduce benchmarks via run-benchmark.sh; compare to PERFORMANCE_REPORT.md.

## Depends on

None — start here

## Required deliverables

- `advanced/A6-performance/PERFORMANCE_REPORT.md`
- `advanced/A6-performance/run-benchmark.sh`

## Reference files (golden examples in this repo)

- `advanced/A6-performance/README.md`
- `advanced/A6-performance/PERFORMANCE_REPORT.md`
- `advanced/A6-performance/run-benchmark.sh`
- `advanced/A6-performance/benchmark-results.csv`

## Cursor prompt

Open **docs/AGENT_PROMPTS.md** → section **## A6 —**

Or run slash command: `/evil-ai-performance`

## Verify (optional)

```bash
BENCH_LINES=100000 BENCH_RUNS=2 bash advanced/A6-performance/run-benchmark.sh
```
