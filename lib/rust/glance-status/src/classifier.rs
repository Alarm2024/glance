//! Fault classifier — blocking flag, then hygiene exclusion, then fault allowlist.

/// Doctor card status values (matches demo/fixture.json `doctor.status`).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum DoctorStatus {
    Ok,
    Warn,
    EyesFault,
    Blocking,
    Unknown,
}

impl DoctorStatus {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Ok => "ok",
            Self::Warn => "warn",
            Self::EyesFault => "eyes_fault",
            Self::Blocking => "blocking",
            Self::Unknown => "unknown",
        }
    }
}

/// Inputs for fault classification. Order of evaluation is fixed:
/// 1. blocking flag
/// 2. hygiene / info exclusion
/// 3. caller-supplied fault-phrase allowlist (eyes faults checked first)
#[derive(Debug, Clone)]
pub struct ClassifierInput<'a> {
    pub blocking: bool,
    pub message: &'a str,
    pub hygiene_phrases: &'a [&'a str],
    pub fault_phrases: &'a [&'a str],
    pub eyes_fault_phrases: &'a [&'a str],
}

/// Classify a doctor message into a [`DoctorStatus`].
pub fn classify_fault(input: ClassifierInput<'_>) -> DoctorStatus {
    if input.blocking {
        return DoctorStatus::Blocking;
    }

    let msg = input.message.to_ascii_lowercase();

    for phrase in input.hygiene_phrases {
        if msg.contains(&phrase.to_ascii_lowercase()) {
            return DoctorStatus::Ok;
        }
    }

    for phrase in input.eyes_fault_phrases {
        if msg.contains(&phrase.to_ascii_lowercase()) {
            return DoctorStatus::EyesFault;
        }
    }

    for phrase in input.fault_phrases {
        if msg.contains(&phrase.to_ascii_lowercase()) {
            return DoctorStatus::Warn;
        }
    }

    if msg.trim().is_empty() {
        DoctorStatus::Unknown
    } else {
        DoctorStatus::Ok
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn base_input(message: &str) -> ClassifierInput<'_> {
        ClassifierInput {
            blocking: false,
            message,
            hygiene_phrases: &["hygiene", "heartbeat ok", "passed"],
            fault_phrases: &["stale", "timeout", "degraded"],
            eyes_fault_phrases: &["eyes offline", "observer fault"],
        }
    }

    #[test]
    fn blocking_flag_wins() {
        let status = classify_fault(ClassifierInput {
            blocking: true,
            ..base_input("anything")
        });
        assert_eq!(status, DoctorStatus::Blocking);
    }

    #[test]
    fn hygiene_exclusion_before_faults() {
        let status = classify_fault(base_input("Hygiene checks passed · stale ignored"));
        assert_eq!(status, DoctorStatus::Ok);
    }

    #[test]
    fn eyes_fault_from_allowlist() {
        let status = classify_fault(base_input("Observer fault on slot stream"));
        assert_eq!(status, DoctorStatus::EyesFault);
    }

    #[test]
    fn warn_from_fault_allowlist() {
        let status = classify_fault(base_input("Feed stale for 47s"));
        assert_eq!(status, DoctorStatus::Warn);
    }

    #[test]
    fn unknown_on_empty_message() {
        let status = classify_fault(ClassifierInput {
            blocking: false,
            message: "   ",
            hygiene_phrases: &[],
            fault_phrases: &[],
            eyes_fault_phrases: &[],
        });
        assert_eq!(status, DoctorStatus::Unknown);
    }

    #[test]
    fn ok_when_no_fault_phrases_match() {
        let status = classify_fault(base_input("All nominal"));
        assert_eq!(status, DoctorStatus::Ok);
    }
}
