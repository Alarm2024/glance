//! Strip sensitive shapes from status strings before display or logging.

use regex::Regex;
use std::sync::LazyLock;

static URL_WITH_QUERY: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"https?://[^\s]+?\?[^\s#]+").unwrap());

static HEX_KEY: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\b[0-9a-fA-F]{32,64}\b").unwrap());

/// Base58 alphabet (no 0, O, I, l) — typical for encoded keys.
static BASE58_KEY: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\b[1-9A-HJ-NP-Za-km-z]{32,44}\b").unwrap()
});

static API_KEY_PREFIX: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\b(sk|pk|api)[_-][A-Za-z0-9][A-Za-z0-9_-]{15,}\b").unwrap()
});

static BEARER_TOKEN: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\bBearer\s+[A-Za-z0-9._\-]{20,}\b").unwrap());

const REDACTED_URL: &str = "[REDACTED_URL]";
const REDACTED_HEX: &str = "[REDACTED_HEX]";
const REDACTED_KEY: &str = "[REDACTED_KEY]";
const REDACTED_SECRET: &str = "[REDACTED_SECRET]";

/// Redact URLs with query params, hex/base58 key shapes, and common API-key patterns.
pub fn redact(input: &str) -> String {
    let mut out = input.to_string();
    out = URL_WITH_QUERY.replace_all(&out, REDACTED_URL).into_owned();
    out = BEARER_TOKEN.replace_all(&out, REDACTED_SECRET).into_owned();
    out = API_KEY_PREFIX.replace_all(&out, REDACTED_SECRET).into_owned();
    out = HEX_KEY.replace_all(&out, REDACTED_HEX).into_owned();
    out = BASE58_KEY.replace_all(&out, REDACTED_KEY).into_owned();
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn strips_url_query_params() {
        let raw = "see https://example.com/path?token=abc123&user=1 for detail";
        let out = redact(raw);
        assert!(!out.contains("token=abc123"));
        assert!(out.contains(REDACTED_URL));
    }

    #[test]
    fn strips_long_hex() {
        let raw = "key=deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef";
        let out = redact(raw);
        assert!(out.contains(REDACTED_HEX));
        assert!(!out.contains("deadbeefdeadbeef"));
    }

    #[test]
    fn strips_base58_shape() {
        let raw = "owner 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU signed";
        let out = redact(raw);
        assert!(out.contains(REDACTED_KEY));
    }

    #[test]
    fn strips_api_key_prefixes() {
        let raw = "auth sk-live-abcdefghijklmnopqrstuvwxyz failed";
        let out = redact(raw);
        assert!(out.contains(REDACTED_SECRET));
        assert!(!out.contains("sk-live"));
    }

    #[test]
    fn strips_bearer_token() {
        let raw = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.sig";
        let out = redact(raw);
        assert!(out.contains(REDACTED_SECRET));
        assert!(!out.contains("eyJhbGci"));
    }

    #[test]
    fn leaves_benign_text() {
        let raw = "Process heartbeat OK (demo fixture)";
        assert_eq!(redact(raw), raw);
    }
}
