use regex::Regex;
use std::sync::LazyLock;

static URL_WITH_QUERY: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"https?://[^\s?]+(\?[^\s]*)").unwrap());

static HEX_KEY: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\b[0-9a-fA-F]{32,64}\b").unwrap());

static BASE58_KEY: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\b[1-9A-HJ-NP-Za-km-z]{32,44}\b").unwrap()
});

static API_KEY_PREFIX: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*\S+|bearer\s+\S+").unwrap()
});

static SK_PREFIX: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\bsk-[a-zA-Z0-9_-]{8,}\b").unwrap());

const REDACTED: &str = "[REDACTED]";

/// Strip sensitive fragments from free-form status text.
///
/// Removes or masks:
/// - URLs that include query parameters
/// - Key-shaped hex strings (32–64 chars)
/// - Key-shaped base58 strings (32–44 chars, Solana-style)
/// - Common wallet / API-key patterns (`api_key=…`, `Bearer …`, `sk-…`)
pub fn redact(input: &str) -> String {
    let mut out = input.to_string();
    out = URL_WITH_QUERY.replace_all(&out, REDACTED).into_owned();
    out = API_KEY_PREFIX.replace_all(&out, REDACTED).into_owned();
    out = SK_PREFIX.replace_all(&out, REDACTED).into_owned();
    out = HEX_KEY.replace_all(&out, REDACTED).into_owned();
    out = BASE58_KEY.replace_all(&out, REDACTED).into_owned();
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn strips_url_query_params() {
        let raw = "see https://api.example.com/v1/status?token=abc123 for detail";
        let cleaned = redact(raw);
        assert!(!cleaned.contains("token=abc123"));
        assert!(cleaned.contains(REDACTED));
    }

    #[test]
    fn strips_hex_keys() {
        let raw = "sig deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef";
        let cleaned = redact(raw);
        assert!(!cleaned.contains("deadbeef"));
        assert!(cleaned.contains(REDACTED));
    }

    #[test]
    fn strips_base58_shapes() {
        let raw = "owner 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU logged event";
        let cleaned = redact(raw);
        assert!(!cleaned.contains("7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"));
        assert!(cleaned.contains(REDACTED));
    }

    #[test]
    fn strips_api_key_shapes() {
        for raw in [
            "config api_key=supersecretvalue",
            "header Bearer eyJhbGciOiJIUzI1NiJ9.payload",
            "using secret: not-for-logs",
        ] {
            let cleaned = redact(raw);
            assert!(
                !cleaned.to_ascii_lowercase().contains("supersecret")
                    && !cleaned.contains("eyJhbGci")
                    && !cleaned.contains("not-for-logs"),
                "failed for: {raw}"
            );
            assert!(cleaned.contains(REDACTED), "failed for: {raw}");
        }
    }

    #[test]
    fn strips_sk_prefix() {
        let raw = "loaded sk-live-abcdefghijklmnopqrstuvwxyz";
        let cleaned = redact(raw);
        assert!(!cleaned.contains("sk-live"));
        assert!(cleaned.contains(REDACTED));
    }

    #[test]
    fn benign_text_unchanged() {
        let raw = "Process heartbeat OK (demo fixture)";
        assert_eq!(redact(raw), raw);
    }
}
