//! Fault classifier — blocking flag, hygiene exclusion, fault allowlist, then unknown.

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

/// Inputs for doctor status classification.
///
/// Evaluation order is fixed:
/// 1. `blocking_flag`
/// 2. hygiene / info exclusion (`hygiene_phrases`)
/// 3. caller-supplied fault allowlist (`fault_phrases`)
/// 4. [`DoctorStatus::Unknown`]
#[derive(Debug, Clone)]
pub struct ClassifyInput {
    pub blocking_flag: bool,
    pub hygiene_phrases: Vec<String>,
    pub fault_phrases: Vec<String>,
    pub raw_message: String,
}

/// Classify a doctor message into a [`DoctorStatus`].
pub fn classify(input: &ClassifyInput) -> DoctorStatus {
    if input.blocking_flag {
        return DoctorStatus::Blocking;
    }

    let msg = input.raw_message.to_ascii_lowercase();

    for phrase in &input.hygiene_phrases {
        if msg.contains(&phrase.to_ascii_lowercase()) {
            return DoctorStatus::Ok;
        }
    }

    for phrase in &input.fault_phrases {
        if msg.contains(&phrase.to_ascii_lowercase()) {
            return DoctorStatus::Warn;
        }
    }

    DoctorStatus::Unknown
}

#[cfg(test)]
mod tests {
    use super::*;

    fn base_input(raw_message: impl Into<String>) -> ClassifyInput {
        ClassifyInput {
            blocking_flag: false,
            hygiene_phrases: vec![
                "hygiene".into(),
                "heartbeat ok".into(),
                "passed".into(),
            ],
            fault_phrases: vec![
                "stale".into(),
                "timeout".into(),
                "degraded".into(),
            ],
            raw_message: raw_message.into(),
        }
    }

    #[test]
    fn blocking_overrides_everything() {
        let status = classify(&ClassifyInput {
            blocking_flag: true,
            ..base_input("Hygiene checks passed · stale feed")
        });
        assert_eq!(status, DoctorStatus::Blocking);
    }

    #[test]
    fn hygiene_never_classifies_as_fault() {
        let status = classify(&base_input(
            "Hygiene checks passed · stale ignored for now",
        ));
        assert_eq!(status, DoctorStatus::Ok);
    }

    #[test]
    fn warn_from_fault_allowlist() {
        let status = classify(&base_input("Feed stale for 47s"));
        assert_eq!(status, DoctorStatus::Warn);
    }

    #[test]
    fn unknown_on_empty_message() {
        let status = classify(&ClassifyInput {
            blocking_flag: false,
            hygiene_phrases: vec![],
            fault_phrases: vec![],
            raw_message: "   ".into(),
        });
        assert_eq!(status, DoctorStatus::Unknown);
    }

    #[test]
    fn unknown_when_no_phrase_matches() {
        let status = classify(&base_input("All nominal"));
        assert_eq!(status, DoctorStatus::Unknown);
    }
}
