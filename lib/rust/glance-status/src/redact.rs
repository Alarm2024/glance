use regex::Regex;
use std::sync::LazyLock;

static URL_WITH_QUERY: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"https?://[^\s/?#]+[^\s]*\?[^\s]+").unwrap());

static HEX_KEY: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\b(?:0x)?[0-9a-fA-F]{32,64}\b").unwrap());

static BASE58_KEY: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\b[1-9A-HJ-NP-Za-km-z]{32,44}\b").unwrap()
});

static API_KEY: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\b(?:sk|pk|api|token|key)[-_][A-Za-z0-9-]{16,}\b").unwrap()
});

static WALLET_LIKE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\b[1-9A-HJ-NP-Za-km-z]{43,44}\b").unwrap()
});

const REDACTED: &str = "[REDACTED]";

/// Strip URLs with query params, key-shaped hex/base58, and common wallet/API-key shapes.
pub fn redact(input: &str) -> String {
    let mut out = input.to_string();
    out = URL_WITH_QUERY.replace_all(&out, REDACTED).into_owned();
    out = API_KEY.replace_all(&out, REDACTED).into_owned();
    out = WALLET_LIKE.replace_all(&out, REDACTED).into_owned();
    out = BASE58_KEY.replace_all(&out, REDACTED).into_owned();
    out = HEX_KEY.replace_all(&out, REDACTED).into_owned();
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn redacts_urls_with_query_params() {
        let input = "see https://api.example.com/v1/data?token=abc123 for details";
        let out = redact(input);
        assert!(!out.contains("token=abc123"));
        assert!(out.contains(REDACTED));
    }

    #[test]
    fn redacts_hex_keys() {
        let input = "key=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
        let out = redact(input);
        assert!(!out.contains("0123456789abcdef"));
        assert!(out.contains(REDACTED));
    }

    #[test]
    fn redacts_base58_wallet_shapes() {
        let input = "owner 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU signed";
        let out = redact(input);
        assert!(!out.contains("7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"));
        assert!(out.contains(REDACTED));
    }

    #[test]
    fn redacts_api_key_shapes() {
        let input = "using sk-live-abcdefghijklmnopqrstuvwxyz123456";
        let out = redact(input);
        assert!(!out.contains("sk-live"));
        assert!(out.contains(REDACTED));
    }

    #[test]
    fn leaves_plain_text_untouched() {
        let input = "status ok · no secrets here";
        assert_eq!(redact(input), input);
    }
}
