use std::fmt;

#[derive(Debug, Default, PartialEq, Eq)]
pub struct LogCounts {
    pub info: usize,
    pub warn: usize,
    pub error: usize,
}

impl LogCounts {
    pub fn total(&self) -> usize {
        self.info + self.warn + self.error
    }
}

fn line_needs_trim(line: &str) -> bool {
    let bytes = line.as_bytes();
    if bytes.is_empty() {
        return false;
    }
    bytes[0].is_ascii_whitespace() || bytes[bytes.len() - 1].is_ascii_whitespace()
}

fn normalize_line(line: &str) -> &str {
    if line_needs_trim(line) {
        line.trim()
    } else {
        line
    }
}

fn matches_log_level(line: &str, level: &str) -> bool {
    match line.strip_prefix(level) {
        None => false,
        Some(rest) => rest.is_empty() || rest.starts_with(' ') || rest.starts_with(':'),
    }
}

fn classify_log_level(line: &str) -> Option<LogLevelKind> {
    if line.is_empty() {
        return None;
    }

    match line.as_bytes().first() {
        Some(b'I') if matches_log_level(line, "INFO") => Some(LogLevelKind::Info),
        Some(b'W') if matches_log_level(line, "WARN") => Some(LogLevelKind::Warn),
        Some(b'E') if matches_log_level(line, "ERROR") => Some(LogLevelKind::Error),
        _ => None,
    }
}

enum LogLevelKind {
    Info,
    Warn,
    Error,
}

pub fn count_log_levels(content: &str) -> LogCounts {
    let mut counts = LogCounts::default();

    for line in content.lines() {
        if line.is_empty() {
            continue;
        }

        let normalized = normalize_line(line);
        match classify_log_level(normalized) {
            Some(LogLevelKind::Info) => counts.info += 1,
            Some(LogLevelKind::Warn) => counts.warn += 1,
            Some(LogLevelKind::Error) => counts.error += 1,
            None => {}
        }
    }

    counts
}

pub fn format_summary(counts: &LogCounts) -> String {
    format!(
        "## Log Summary\n\nINFO: {}\nWARN: {}\nERROR: {}",
        counts.info, counts.warn, counts.error
    )
}

impl fmt::Display for LogCounts {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", format_summary(self))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn count_info_logs() {
        let content = "INFO Application started\nINFO User authenticated\nINFO Request processed\n";
        let counts = count_log_levels(content);
        assert_eq!(counts.info, 3);
        assert_eq!(counts.warn, 0);
        assert_eq!(counts.error, 0);
    }

    #[test]
    fn count_warn_logs() {
        let content = "WARN Rate limit approaching\nWARN Disk space low\n";
        let counts = count_log_levels(content);
        assert_eq!(counts.info, 0);
        assert_eq!(counts.warn, 2);
        assert_eq!(counts.error, 0);
    }

    #[test]
    fn count_error_logs() {
        let content = "ERROR Database connection failed\nERROR Timeout exceeded\n";
        let counts = count_log_levels(content);
        assert_eq!(counts.info, 0);
        assert_eq!(counts.warn, 0);
        assert_eq!(counts.error, 2);
    }

    #[test]
    fn mixed_log_file() {
        let content = "\
INFO Application started
INFO User authenticated
WARN Rate limit approaching
ERROR Database connection failed
INFO Request processed
";
        let counts = count_log_levels(content);
        assert_eq!(counts.info, 3);
        assert_eq!(counts.warn, 1);
        assert_eq!(counts.error, 1);
    }

    #[test]
    fn empty_file() {
        let counts = count_log_levels("");
        assert_eq!(counts.info, 0);
        assert_eq!(counts.warn, 0);
        assert_eq!(counts.error, 0);
    }

    #[test]
    fn format_summary_output() {
        let counts = LogCounts {
            info: 3,
            warn: 1,
            error: 1,
        };
        assert_eq!(
            format_summary(&counts),
            "## Log Summary\n\nINFO: 3\nWARN: 1\nERROR: 1"
        );
    }

    #[test]
    fn does_not_match_longer_level_prefixes() {
        let content = "INFORMATION log line\nWARNING deprecated\nERROR_HANDLER init\n";
        let counts = count_log_levels(content);
        assert_eq!(counts.info, 0);
        assert_eq!(counts.warn, 0);
        assert_eq!(counts.error, 0);
    }

    #[test]
    fn matches_level_token_followed_by_space() {
        let content = "INFO Application started\nWARN Rate limit\nERROR Connection failed\n";
        let counts = count_log_levels(content);
        assert_eq!(counts.info, 1);
        assert_eq!(counts.warn, 1);
        assert_eq!(counts.error, 1);
    }

    #[test]
    fn matches_level_token_followed_by_colon() {
        let content = "INFO: Application started\nWARN: Rate limit\nERROR: Connection failed\n";
        let counts = count_log_levels(content);
        assert_eq!(counts.info, 1);
        assert_eq!(counts.warn, 1);
        assert_eq!(counts.error, 1);
    }
}
