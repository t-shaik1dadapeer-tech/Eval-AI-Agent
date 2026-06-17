use std::env;
use std::path::Path;
use std::process;

use b6_rust_log_analyzer::analyzer::{count_log_levels, format_summary};
use b6_rust_log_analyzer::errors::{read_log_file, LogAnalyzerError};

fn main() {
    if let Err(error) = run() {
        eprintln!("{error}");
        process::exit(1);
    }
}

fn run() -> Result<(), LogAnalyzerError> {
    let file_path = env::args().nth(1).ok_or(LogAnalyzerError::MissingArgument)?;
    let path = Path::new(&file_path);

    let content = read_log_file(path)?;
    let counts = count_log_levels(&content);

    println!("{}", format_summary(&counts));
    Ok(())
}
