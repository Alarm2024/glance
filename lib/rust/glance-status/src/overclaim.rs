use std::fmt;

/// Error returned when a status string contains banned overclaim phrases.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct OverclaimError {
    pub matches: Vec<String>,
}

impl fmt::Display for OverclaimError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "status string contains banned overclaim phrase(s): {}",
            self.matches.join(", ")
        )
    }
}

impl std::error::Error for OverclaimError {}

/// Fail when `status` contains any caller-supplied banned phrase (case-insensitive).
pub fn assert_no_overclaim(status: &str, banned_phrases: &[&str]) -> Result<(), OverclaimError> {
    let lower = status.to_ascii_lowercase();
    let mut matches = Vec::new();

    for phrase in banned_phrases {
        let needle = phrase.to_ascii_lowercase();
        if !needle.is_empty() && lower.contains(&needle) {
            matches.push((*phrase).to_string());
        }
    }

    if matches.is_empty() {
        Ok(())
    } else {
        Err(OverclaimError { matches })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn passes_clean_status() {
        assert!(assert_no_overclaim(
            "observe-only · no blocking flags",
            &["guaranteed", "profit"]
        )
        .is_ok());
    }

    #[test]
    fn fails_on_banned_phrase() {
        let err = assert_no_overclaim(
            "System is PROFIT-optimized",
            &["profit", "guaranteed win"],
        )
        .unwrap_err();
        assert_eq!(err.matches, vec!["profit"]);
    }

    #[test]
    fn fails_on_multiple_matches() {
        let err = assert_no_overclaim(
            "guaranteed profit for everyone",
            &["guaranteed", "profit"],
        )
        .unwrap_err();
        assert_eq!(err.matches.len(), 2);
    }

    #[test]
    fn empty_banned_list_always_passes() {
        assert!(assert_no_overclaim("anything goes", &[]).is_ok());
    }
}
