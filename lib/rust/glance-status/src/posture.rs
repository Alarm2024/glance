//! Eyes-only posture checks and read-only status summary for Glance fixtures.

use serde_json::Value;

/// Posture modes that satisfy dry / eyes-only compose.
pub const ALLOWED_POSTURE_MODES: &[&str] = &[
    "dry compose",
    "dry simulate",
    "observe-only",
    "eyes only",
    "eyes-only",
];

const BANNED_POSTURE_PHRASES: &[&str] = &[
    "armed",
    "auto-arm",
    "auto arm",
    "auto-send",
    "auto send",
    "clear+",
    "clear +",
    "live send",
    "live mode",
    "mint",
];

const BANNED_ACTION_SUGGESTIONS: &[&str] = &[
    "click clear",
    "press clear",
    "send now",
    "auto-send",
    "auto send",
    "enable send",
    "flip dry",
    "go live",
    "arm now",
    "mint",
    "mint now",
];

const READ_ONLY_CARD_KEYS: &[&str] = &["online", "doctor", "feeds", "last_signal", "build"];

/// One-line operator summary (read-only).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum StatusSummary {
    Ok,
    Degraded,
    Fault,
}

impl StatusSummary {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Ok => "OK",
            Self::Degraded => "DEGRADED",
            Self::Fault => "FAULT",
        }
    }
}

fn normalize_mode(mode: &str) -> String {
    mode.split_whitespace().collect::<Vec<_>>().join(" ").to_ascii_lowercase()
}

fn contains_banned_phrase(text: &str, phrase: &str) -> bool {
    let lower = text.to_lowercase();
    let needle = phrase.to_lowercase();
    let mut start = 0usize;
    while let Some(rel) = lower[start..].find(&needle) {
        let abs = start + rel;
        let before = &lower[..abs];
        if before.ends_with("no ") || before.ends_with("no-") {
            start = abs + needle.len();
            continue;
        }
        return true;
    }
    false
}

/// Return true when mode is an allowed dry / eyes-only posture label.
pub fn is_allowed_posture_mode(mode: &str) -> bool {
    let normalized = normalize_mode(mode);
    if ALLOWED_POSTURE_MODES.contains(&normalized.as_str()) {
        return true;
    }
    normalized.contains("dry") || normalized.contains("observe") || normalized.contains("eyes")
}

/// Return `Err` unless posture.mode is dry compose or equivalent.
pub fn assert_dry_posture(posture: &Value, label: &str) -> Result<(), String> {
    let mode = posture
        .get("mode")
        .and_then(Value::as_str)
        .map(str::trim)
        .filter(|s| !s.is_empty())
        .ok_or_else(|| format!("{label}: posture.mode must be a non-empty string"))?;

    if !is_allowed_posture_mode(mode) {
        return Err(format!(
            "{label}: posture.mode must be dry compose or equivalent, got {mode:?}"
        ));
    }

    let normalized = normalize_mode(mode);
    for phrase in BANNED_POSTURE_PHRASES {
        if contains_banned_phrase(&normalized, phrase) {
            return Err(format!(
                "{label}: posture.mode contains banned phrase {phrase:?}"
            ));
        }
    }

    if let Some(detail) = posture.get("detail").and_then(Value::as_str) {
        for phrase in BANNED_POSTURE_PHRASES {
            if contains_banned_phrase(detail, phrase) {
                return Err(format!(
                    "{label}: posture.detail contains banned phrase {phrase:?}"
                ));
            }
        }
    }

    Ok(())
}

fn collect_strings(value: &Value, out: &mut Vec<String>) {
    match value {
        Value::String(s) => out.push(s.clone()),
        Value::Object(map) => {
            for v in map.values() {
                collect_strings(v, out);
            }
        }
        Value::Array(items) => {
            for item in items {
                collect_strings(item, out);
            }
        }
        _ => {}
    }
}

/// Return `Err` if read-only cards suggest CLEAR, send, arm, or mint.
pub fn assert_no_send_suggestions(fixture: &Value, label: &str) -> Result<(), String> {
    let obj = fixture
        .as_object()
        .ok_or_else(|| format!("{label}: expected JSON object"))?;

    for key in READ_ONLY_CARD_KEYS {
        let Some(card) = obj.get(*key) else {
            continue;
        };
        let mut strings = Vec::new();
        collect_strings(card, &mut strings);
        for text in strings {
            for phrase in BANNED_ACTION_SUGGESTIONS {
                if contains_banned_phrase(&text, phrase) {
                    return Err(format!(
                        "{label}: {key} suggests action {phrase:?} in {text:?}"
                    ));
                }
            }
        }
    }
    Ok(())
}

/// Validate synthetic demo fixture stays eyes-only with dry posture.
pub fn assert_eyes_only_fixture(fixture: &Value, label: &str) -> Result<(), String> {
    let obj = fixture
        .as_object()
        .ok_or_else(|| format!("{label}: expected JSON object"))?;

    if obj.get("synthetic").and_then(Value::as_bool) != Some(true) {
        return Err(format!("{label}: synthetic must be true for demo fixtures"));
    }

    let banner = obj
        .get("label")
        .and_then(Value::as_str)
        .unwrap_or_default();
    if !banner.to_ascii_lowercase().contains("synthetic") {
        return Err(format!(
            "{label}: label must clearly mark synthetic demo data, got {banner:?}"
        ));
    }

    let posture = obj
        .get("posture")
        .ok_or_else(|| format!("{label}: missing posture object"))?;
    assert_dry_posture(posture, label)?;
    assert_no_send_suggestions(fixture, label)
}

/// One-line OK / DEGRADED / FAULT summary for operator status JSON (read-only).
pub fn summarize_status(fixture: &Value) -> StatusSummary {
    if let Some(doctor) = fixture.get("doctor") {
        if let Some(status) = doctor.get("status").and_then(Value::as_str) {
            match status.to_ascii_lowercase().as_str() {
                "blocking" | "eyes_fault" => return StatusSummary::Fault,
                "warn" => return StatusSummary::Degraded,
                _ => {}
            }
        }
    }

    if let Some(online) = fixture.get("online") {
        if let Some(status) = online.get("status").and_then(Value::as_str) {
            let lower = status.to_ascii_lowercase();
            if !lower.is_empty() && lower != "connected" && lower != "ok" {
                return StatusSummary::Fault;
            }
        }
    }

    if let Some(Value::Array(feeds)) = fixture.get("feeds") {
        for feed in feeds {
            if let Some(state) = feed.get("state").and_then(Value::as_str) {
                match state.to_ascii_lowercase().as_str() {
                    "fault" | "error" | "down" | "blocking" => return StatusSummary::Fault,
                    "stale" | "warn" | "degraded" | "unknown" => return StatusSummary::Degraded,
                    _ => {}
                }
            }
        }
    }

    StatusSummary::Ok
}

/// Extract posture fields from the DEMO_FIXTURE object in app.js for CI.
pub fn extract_demo_fixture_from_app_js(source: &str) -> Result<Value, String> {
    if !source.contains("DEMO_FIXTURE") {
        return Err("app.js: could not find DEMO_FIXTURE object".into());
    }
    if !source.contains("synthetic: true") && !source.contains("synthetic:true") {
        return Err("app.js: DEMO_FIXTURE must set synthetic: true".into());
    }

    let mode = extract_posture_mode_literal(source)
        .ok_or_else(|| "app.js: DEMO_FIXTURE missing posture.mode".to_string())?;

    let label = extract_quoted_value(source, "label").unwrap_or_default();

    Ok(serde_json::json!({
        "synthetic": true,
        "label": label,
        "posture": { "mode": mode, "detail": "" }
    }))
}

fn extract_posture_mode_literal(source: &str) -> Option<String> {
    let posture = source.find("posture:")?;
    extract_quoted_value(&source[posture..], "mode")
}

fn extract_quoted_value(source: &str, key: &str) -> Option<String> {
    for quote in ['\'', '"'] {
        let needle = format!("{key}: {quote}");
        let start = source.find(&needle)? + needle.len();
        let rest = &source[start..];
        let end = rest.find(quote)?;
        return Some(rest[..end].to_string());
    }
    None
}

/// CI helper: fixture file, embedded page JSON, and static HTML stay eyes-only.
pub fn assert_page_sources_dry(
    fixture_json: &str,
    app_js: &str,
    index_html: &str,
) -> Result<(), String> {
    let fixture: Value = serde_json::from_str(fixture_json)
        .map_err(|e| format!("demo/fixture.json parse error: {e}"))?;
    assert_eyes_only_fixture(&fixture, "demo/fixture.json")?;

    let embedded = extract_demo_fixture_from_app_js(app_js)?;
    assert_eyes_only_fixture(&embedded, "app.js DEMO_FIXTURE")?;

    let file_mode = normalize_mode(
        fixture
            .get("posture")
            .and_then(|p| p.get("mode"))
            .and_then(Value::as_str)
            .unwrap_or_default(),
    );
    let embedded_mode = normalize_mode(
        embedded
            .get("posture")
            .and_then(|p| p.get("mode"))
            .and_then(Value::as_str)
            .unwrap_or_default(),
    );
    if file_mode != embedded_mode {
        return Err(format!(
            "app.js DEMO_FIXTURE posture.mode {embedded_mode:?} != demo/fixture.json {file_mode:?}"
        ));
    }

    let html_lower = index_html.to_ascii_lowercase();
    if !html_lower.contains("dry compose") {
        return Err("index.html: static posture badge must show dry compose".into());
    }
    if !html_lower.contains("synthetic") && !html_lower.contains("demo") {
        return Err(
            "index.html: must clearly label synthetic demo (banner or hint)".into(),
        );
    }

    let banned_in_html = ["send now", "click clear", "enable send", "go live", "armed"];
    for phrase in banned_in_html {
        if html_lower.contains(phrase) {
            return Err(format!(
                "index.html: contains banned action phrase {phrase:?}"
            ));
        }
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn demo_fixture() -> Value {
        serde_json::from_str(include_str!("../../../../demo/fixture.json")).unwrap()
    }

    #[test]
    fn demo_fixture_passes_eyes_only() {
        assert_eyes_only_fixture(&demo_fixture(), "demo/fixture.json").unwrap();
    }

    #[test]
    fn rejects_live_posture_mode() {
        let posture = serde_json::json!({"mode": "live send", "detail": "armed"});
        assert!(assert_dry_posture(&posture, "test").is_err());
    }

    #[test]
    fn summarize_demo_fixture_ok_or_degraded() {
        let summary = summarize_status(&demo_fixture());
        assert!(matches!(
            summary,
            StatusSummary::Ok | StatusSummary::Degraded
        ));
    }

    #[test]
    fn allowed_modes_include_dry_compose() {
        assert!(ALLOWED_POSTURE_MODES.contains(&"dry compose"));
    }

    #[test]
    fn rejects_bare_mint_button_label() {
        let mut fixture = demo_fixture();
        fixture["doctor"] = serde_json::json!({"status": "warn", "summary": "Mint"});
        let err = assert_no_send_suggestions(&fixture, "test").unwrap_err();
        assert!(err.contains("mint"), "expected mint ban, got {err}");
    }

    #[test]
    fn allows_negated_mint_suggestion() {
        let mut fixture = demo_fixture();
        fixture["doctor"] =
            serde_json::json!({"status": "warn", "summary": "no mint — eyes-only demo"});
        assert_no_send_suggestions(&fixture, "test").unwrap();
    }
}
