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

pub fn count_log_levels(content: &str) -> LogCounts {
    let mut counts = LogCounts::default();

    for line in content.lines() {
        let trimmed = line.trim();
        if trimmed.is_empty() {
            continue;
        }

        if trimmed.starts_with("INFO") {
            counts.info += 1;
        } else if trimmed.starts_with("WARN") {
            counts.warn += 1;
        } else if trimmed.starts_with("ERROR") {
            counts.error += 1;
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
}
