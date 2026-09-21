//! Anti-overclaim guard — fail when status text contains banned phrases.

/// Return `Err` if `status_text` contains any caller-supplied banned phrase (case-insensitive).
pub fn assert_no_overclaim(status_text: &str, banned: &[String]) -> Result<(), String> {
    let lower = status_text.to_ascii_lowercase();
    for phrase in banned {
        if lower.contains(&phrase.to_ascii_lowercase()) {
            return Err(format!(
                "status string contains banned overclaim phrase: {:?}",
                phrase
            ));
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn banned(items: &[&str]) -> Vec<String> {
        items.iter().map(|s| (*s).to_string()).collect()
    }

    #[test]
    fn passes_clean_status() {
        assert_no_overclaim(
            "No blocking flags, no active faults",
            &banned(&["guaranteed", "profit", "alpha"]),
        )
        .unwrap();
    }

    #[test]
    fn catches_banned_phrase() {
        let err = assert_no_overclaim(
            "System is Guaranteed stable",
            &banned(&["guaranteed", "profit"]),
        )
        .unwrap_err();
        assert!(err.contains("guaranteed"));
    }

    #[test]
    fn case_insensitive_match() {
        assert!(assert_no_overclaim("ALPHA leak detected", &banned(&["alpha"])).is_err());
    }
}
