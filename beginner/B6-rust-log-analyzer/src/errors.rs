use std::fmt;
use std::io;
use std::path::Path;

#[derive(Debug)]
pub enum LogAnalyzerError {
    MissingArgument,
    FileNotFound(String),
    ReadPermissionDenied(String),
    ReadFailed { path: String, source: io::Error },
}

impl fmt::Display for LogAnalyzerError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            LogAnalyzerError::MissingArgument => {
                write!(f, "Error: missing file path argument")
            }
            LogAnalyzerError::FileNotFound(path) => {
                write!(f, "Error: File not found: {path}")
            }
            LogAnalyzerError::ReadPermissionDenied(path) => {
                write!(f, "Error: Permission denied reading file: {path}")
            }
            LogAnalyzerError::ReadFailed { path, source } => {
                write!(f, "Error: Failed to read file {path}: {source}")
            }
        }
    }
}

impl std::error::Error for LogAnalyzerError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            LogAnalyzerError::ReadFailed { source, .. } => Some(source),
            _ => None,
        }
    }
}

pub fn read_log_file(path: &Path) -> Result<String, LogAnalyzerError> {
    if !path.exists() {
        return Err(LogAnalyzerError::FileNotFound(path.display().to_string()));
    }

    std::fs::read_to_string(path).map_err(|source| {
        if source.kind() == io::ErrorKind::PermissionDenied {
            LogAnalyzerError::ReadPermissionDenied(path.display().to_string())
        } else {
            LogAnalyzerError::ReadFailed {
                path: path.display().to_string(),
                source,
            }
        }
    })
}
