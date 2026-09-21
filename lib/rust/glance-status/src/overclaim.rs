//! Anti-overclaim guard — fail when status text contains banned phrases.

use std::fmt;

/// Error returned when a status string contains a banned overclaim phrase.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct OverclaimError {
    pub phrase: String,
}

impl fmt::Display for OverclaimError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "status string contains banned overclaim phrase: {:?}",
            self.phrase
        )
    }
}

impl std::error::Error for OverclaimError {}

/// Return `Err` if `status` contains any caller-supplied banned phrase (case-insensitive).
pub fn assert_no_overclaim(status: &str, banned_phrases: &[&str]) -> Result<(), OverclaimError> {
    let lower = status.to_ascii_lowercase();
    for phrase in banned_phrases {
        if lower.contains(&phrase.to_ascii_lowercase()) {
            return Err(OverclaimError {
                phrase: (*phrase).to_string(),
            });
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn passes_clean_status() {
        assert_no_overclaim(
            "No blocking flags, no active faults",
            &["guaranteed", "profit", "alpha"],
        )
        .unwrap();
    }

    #[test]
    fn fails_on_banned_phrase() {
        let err = assert_no_overclaim(
            "System is Guaranteed stable",
            &["guaranteed", "profit"],
        )
        .unwrap_err();
        assert_eq!(err.phrase, "guaranteed");
    }

    #[test]
    fn case_insensitive_match() {
        assert!(assert_no_overclaim("ALPHA leak detected", &["alpha"]).is_err());
    }
}
