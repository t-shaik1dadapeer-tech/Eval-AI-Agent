use std::hint::black_box;
use std::time::Instant;

use b6_rust_log_analyzer::analyzer::count_log_levels;

fn build_log(lines: usize) -> String {
    let mut content = String::with_capacity(lines * 48);
    for i in 0..lines {
        let level = match i % 10 {
            0..=6 => "INFO",
            7..=8 => "WARN",
            _ => "ERROR",
        };
        content.push_str(level);
        content.push_str(" request processed id=");
        content.push_str(&i.to_string());
        content.push('\n');
    }
    content
}

fn main() {
    let lines = std::env::var("BENCH_LINES")
        .ok()
        .and_then(|value| value.parse().ok())
        .unwrap_or(1_000_000);
    let runs: usize = std::env::var("BENCH_RUNS")
        .ok()
        .and_then(|value| value.parse().ok())
        .unwrap_or(5);

    let content = build_log(lines);
    black_box(count_log_levels(&content));

    let mut durations_ms = Vec::with_capacity(runs);
    for run in 1..=runs {
        let start = Instant::now();
        let counts = count_log_levels(&content);
        let elapsed_ms = start.elapsed().as_secs_f64() * 1000.0;
        durations_ms.push(elapsed_ms);
        eprintln!(
            "run={run} lines={lines} info={} warn={} error={} time_ms={elapsed_ms:.3}",
            counts.info, counts.warn, counts.error
        );
        black_box(counts);
    }

    let avg = durations_ms.iter().sum::<f64>() / runs as f64;
    println!("lines={lines}");
    println!("runs={runs}");
    println!("avg_ms={avg:.3}");
    for (index, value) in durations_ms.iter().enumerate() {
        println!("run_{}={value:.3}", index + 1);
    }
}
