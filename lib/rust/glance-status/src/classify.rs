use crate::status::DoctorStatus;

/// Lines and flags supplied by the caller for classification.
pub struct FaultInput<'a> {
    pub blocking_flag: bool,
    pub lines: &'a [&'a str],
}

/// Caller-supplied phrase lists. Order of application is fixed:
/// blocking flag → hygiene/info exclusion → fault-phrase allowlist.
pub struct FaultClassifierConfig<'a> {
    pub hygiene_phrases: &'a [&'a str],
    pub fault_phrases: &'a [&'a str],
}

/// Classify doctor status using the fault-first pipeline.
///
/// 1. **Blocking flag** — immediate `Blocking`.
/// 2. **Hygiene / info exclusion** — matching lines are ignored (not faults).
/// 3. **Fault-phrase allowlist** — only matching non-hygiene lines count as faults.
///    Substrings `eye` / `eyes` in a matched phrase yield `EyesFault`; other matches yield `Warn`.
///    With no allowlist matches, returns `Ok`.
pub fn classify_fault(input: &FaultInput<'_>, config: &FaultClassifierConfig<'_>) -> DoctorStatus {
    if input.blocking_flag {
        return DoctorStatus::Blocking;
    }

    let mut saw_fault = false;
    let mut saw_eyes = false;

    for line in input.lines {
        let lower = line.to_ascii_lowercase();
        if config
            .hygiene_phrases
            .iter()
            .any(|phrase| lower.contains(&phrase.to_ascii_lowercase()))
        {
            continue;
        }

        for phrase in config.fault_phrases {
            if lower.contains(&phrase.to_ascii_lowercase()) {
                saw_fault = true;
                let pl = phrase.to_ascii_lowercase();
                if pl.contains("eye") {
                    saw_eyes = true;
                }
            }
        }
    }

    if saw_eyes {
        DoctorStatus::EyesFault
    } else if saw_fault {
        DoctorStatus::Warn
    } else if input.lines.is_empty() {
        DoctorStatus::Unknown
    } else {
        DoctorStatus::Ok
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const HYGIENE: &[&str] = &["heartbeat ok", "config exclusions applied"];
    const FAULTS: &[&str] = &["stale feed", "rpc timeout", "eyes desync"];

    #[test]
    fn blocking_flag_wins() {
        let input = FaultInput {
            blocking_flag: true,
            lines: &["stale feed"],
        };
        let config = FaultClassifierConfig {
            hygiene_phrases: HYGIENE,
            fault_phrases: FAULTS,
        };
        assert_eq!(classify_fault(&input, &config), DoctorStatus::Blocking);
    }

    #[test]
    fn hygiene_excluded_before_fault_allowlist() {
        let input = FaultInput {
            blocking_flag: false,
            lines: &["heartbeat ok · all feeds nominal"],
        };
        let config = FaultClassifierConfig {
            hygiene_phrases: HYGIENE,
            fault_phrases: FAULTS,
        };
        assert_eq!(classify_fault(&input, &config), DoctorStatus::Ok);
    }

    #[test]
    fn fault_allowlist_warn() {
        let input = FaultInput {
            blocking_flag: false,
            lines: &["price-oracle stale feed detected"],
        };
        let config = FaultClassifierConfig {
            hygiene_phrases: HYGIENE,
            fault_phrases: FAULTS,
        };
        assert_eq!(classify_fault(&input, &config), DoctorStatus::Warn);
    }

    #[test]
    fn fault_allowlist_eyes_fault() {
        let input = FaultInput {
            blocking_flag: false,
            lines: &["monitor eyes desync on slot boundary"],
        };
        let config = FaultClassifierConfig {
            hygiene_phrases: HYGIENE,
            fault_phrases: FAULTS,
        };
        assert_eq!(classify_fault(&input, &config), DoctorStatus::EyesFault);
    }

    #[test]
    fn empty_lines_unknown() {
        let input = FaultInput {
            blocking_flag: false,
            lines: &[],
        };
        let config = FaultClassifierConfig {
            hygiene_phrases: HYGIENE,
            fault_phrases: FAULTS,
        };
        assert_eq!(classify_fault(&input, &config), DoctorStatus::Unknown);
    }

    #[test]
    fn non_matching_lines_ok() {
        let input = FaultInput {
            blocking_flag: false,
            lines: &["all systems nominal"],
        };
        let config = FaultClassifierConfig {
            hygiene_phrases: HYGIENE,
            fault_phrases: FAULTS,
        };
        assert_eq!(classify_fault(&input, &config), DoctorStatus::Ok);
    }

    #[test]
    fn order_blocking_before_hygiene() {
        let input = FaultInput {
            blocking_flag: true,
            lines: &["heartbeat ok"],
        };
        let config = FaultClassifierConfig {
            hygiene_phrases: HYGIENE,
            fault_phrases: FAULTS,
        };
        assert_eq!(classify_fault(&input, &config), DoctorStatus::Blocking);
    }
}
