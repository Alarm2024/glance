use std::error::Error;
use std::fmt;

/// Returned when a status string contains a banned overclaim phrase.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct OverclaimError {
    pub phrase: String,
}

impl fmt::Display for OverclaimError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "status string contains banned overclaim phrase: {}",
            self.phrase
        )
    }
}

impl Error for OverclaimError {}

/// Fail when `text` contains any caller-supplied banned phrase (case-insensitive).
///
/// Intended for unit / integration tests that guard public status copy against
/// profit, live-send, or other overclaim language.
pub fn assert_no_overclaim(text: &str, banned: &[&str]) -> Result<(), OverclaimError> {
    let lower = text.to_ascii_lowercase();
    for phrase in banned {
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

    const BANNED: &[&str] = &[
        "guaranteed profit",
        "risk-free",
        "live-send armed",
        "alpha included",
    ];

    #[test]
    fn clean_status_passes() {
        assert!(assert_no_overclaim(
            "No blocking flags, no active faults",
            BANNED
        )
        .is_ok());
    }

    #[test]
    fn banned_phrase_fails() {
        let err = assert_no_overclaim("This bot delivers guaranteed profit daily", BANNED)
            .unwrap_err();
        assert_eq!(err.phrase, "guaranteed profit");
    }

    #[test]
    fn case_insensitive_match() {
        assert!(assert_no_overclaim("ALPHA INCLUDED in bundle", BANNED).is_err());
    }

    #[test]
    fn empty_banned_always_passes() {
        assert!(assert_no_overclaim("anything goes", &[]).is_ok());
    }
}
