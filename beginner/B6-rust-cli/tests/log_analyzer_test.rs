use std::path::PathBuf;

use b6_rust_log_analyzer::analyzer::{count_log_levels, format_summary};
use b6_rust_log_analyzer::errors::{read_log_file, LogAnalyzerError};

fn sample_log_content() -> &'static str {
    "INFO Application started\nINFO User authenticated\nWARN Rate limit approaching\nERROR Database connection failed\nINFO Request processed\n"
}

#[test]
fn count_info_logs() {
    let counts = count_log_levels(
        "INFO Application started\nINFO User authenticated\nINFO Request processed\n",
    );
    assert_eq!(counts.info, 3);
    assert_eq!(counts.warn, 0);
    assert_eq!(counts.error, 0);
}

#[test]
fn count_warn_logs() {
    let counts = count_log_levels("WARN Rate limit approaching\nWARN Disk space low\n");
    assert_eq!(counts.warn, 2);
}

#[test]
fn count_error_logs() {
    let counts = count_log_levels("ERROR Database connection failed\nERROR Timeout exceeded\n");
    assert_eq!(counts.error, 2);
}

#[test]
fn missing_file() {
    let path = PathBuf::from("logs/does-not-exist-integration.log");
    let result = read_log_file(&path);
    assert!(matches!(result, Err(LogAnalyzerError::FileNotFound(_))));
}

#[test]
fn empty_file() {
    let manifest_dir = env!("CARGO_MANIFEST_DIR");
    let path = PathBuf::from(manifest_dir).join("tests/fixtures/empty.txt");
    let content = read_log_file(&path).expect("empty fixture should be readable");
    let counts = count_log_levels(&content);
    assert_eq!(counts.total(), 0);
    assert_eq!(
        format_summary(&counts),
        "## Log Summary\n\nINFO: 0\nWARN: 0\nERROR: 0"
    );
}

#[test]
fn mixed_log_file() {
    let counts = count_log_levels(sample_log_content());
    assert_eq!(counts.info, 3);
    assert_eq!(counts.warn, 1);
    assert_eq!(counts.error, 1);
}

#[test]
fn ignores_lines_with_level_prefix_substrings() {
    let content = "INFORMATION updated\nWARNING sign\nERROR_HANDLER ready\n";
    let counts = count_log_levels(content);
    assert_eq!(counts.total(), 0);
}

#[test]
fn counts_colon_delimited_log_levels() {
    let content = "INFO: Application started\nWARN: Rate limit\nERROR: Connection failed\n";
    let counts = count_log_levels(content);
    assert_eq!(counts.info, 1);
    assert_eq!(counts.warn, 1);
    assert_eq!(counts.error, 1);
}
