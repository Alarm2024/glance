use crate::DoctorStatus;

/// Input lines and an explicit blocking flag for fault classification.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ClassifyInput<'a> {
    pub blocking: bool,
    pub lines: &'a [&'a str],
}

/// Classify doctor status using caller-supplied hygiene and fault phrase lists.
///
/// Order: blocking flag → hygiene/info exclusion → fault-phrase allowlist.
pub fn classify_fault(
    input: &ClassifyInput<'_>,
    hygiene_patterns: &[&str],
    fault_phrases: &[&str],
) -> DoctorStatus {
    if input.blocking {
        return DoctorStatus::Blocking;
    }

    let mut saw_actionable = false;

    for line in input.lines {
        let trimmed = line.trim();
        if trimmed.is_empty() {
            continue;
        }

        if hygiene_patterns
            .iter()
            .any(|pattern| trimmed.contains(pattern))
        {
            continue;
        }

        saw_actionable = true;

        if fault_phrases
            .iter()
            .any(|phrase| trimmed.contains(phrase))
        {
            return DoctorStatus::EyesFault;
        }
    }

    if saw_actionable {
        DoctorStatus::Warn
    } else {
        DoctorStatus::Ok
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn blocking_flag_wins_first() {
        let input = ClassifyInput {
            blocking: true,
            lines: &["rpc timeout", "hygiene passed"],
        };
        assert_eq!(
            classify_fault(&input, &["hygiene"], &["rpc timeout"]),
            DoctorStatus::Blocking
        );
    }

    #[test]
    fn hygiene_lines_are_excluded() {
        let input = ClassifyInput {
            blocking: false,
            lines: &["config loaded", "info: heartbeat ok"],
        };
        assert_eq!(
            classify_fault(&input, &["info:", "config loaded"], &["rpc down"]),
            DoctorStatus::Ok
        );
    }

    #[test]
    fn fault_phrase_allowlist_triggers_eyes_fault() {
        let input = ClassifyInput {
            blocking: false,
            lines: &["slot lag detected", "info: tick"],
        };
        assert_eq!(
            classify_fault(&input, &["info:"], &["slot lag"]),
            DoctorStatus::EyesFault
        );
    }

    #[test]
    fn actionable_non_fault_line_is_warn() {
        let input = ClassifyInput {
            blocking: false,
            lines: &["feed stale"],
        };
        assert_eq!(
            classify_fault(&input, &["info:"], &["rpc down"]),
            DoctorStatus::Warn
        );
    }

    #[test]
    fn empty_input_is_ok() {
        let input = ClassifyInput {
            blocking: false,
            lines: &[],
        };
        assert_eq!(
            classify_fault(&input, &["info:"], &["fault"]),
            DoctorStatus::Ok
        );
    }
}
