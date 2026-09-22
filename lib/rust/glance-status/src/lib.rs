//! Glance status primitives — doctor classification, redaction, anti-overclaim checks.
//!
//! Synthetic demo data only; no live bot wiring.

mod classifier;
mod overclaim;
mod posture;
mod redact;

pub use classifier::{classify, ClassifyInput, DoctorStatus};
pub use overclaim::assert_no_overclaim;
pub use posture::{
    assert_dry_posture, assert_eyes_only_fixture, assert_no_send_suggestions,
    assert_page_sources_dry, extract_demo_fixture_from_app_js, is_allowed_posture_mode,
    summarize_status, StatusSummary, ALLOWED_POSTURE_MODES,
};
pub use redact::redact;

#[cfg(test)]
mod integration_tests {
    use super::*;
    use std::path::Path;

    #[test]
    fn doctor_status_variants_as_str() {
        assert_eq!(DoctorStatus::Ok.as_str(), "ok");
        assert_eq!(DoctorStatus::Warn.as_str(), "warn");
        assert_eq!(DoctorStatus::EyesFault.as_str(), "eyes_fault");
        assert_eq!(DoctorStatus::Blocking.as_str(), "blocking");
        assert_eq!(DoctorStatus::Unknown.as_str(), "unknown");
    }

    #[test]
    fn posture_selftest_page_sources_dry() {
        let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../..");
        let fixture = std::fs::read_to_string(root.join("demo/fixture.json")).unwrap();
        let app_js = std::fs::read_to_string(root.join("app.js")).unwrap();
        let index_html = std::fs::read_to_string(root.join("index.html")).unwrap();
        assert_page_sources_dry(&fixture, &app_js, &index_html).unwrap();
    }

    #[test]
    fn end_to_end_fixture_doctor_line() {
        let status = classify(&ClassifyInput {
            blocking_flag: false,
            hygiene_phrases: vec![
                "hygiene".into(),
                "config exclusion".into(),
            ],
            fault_phrases: vec![
                "fault".into(),
                "error".into(),
                "stale feed".into(),
            ],
            raw_message: "Hygiene checks passed · config exclusions applied".into(),
        });
        assert_eq!(status, DoctorStatus::Ok);

        let redacted = redact("detail ok");
        assert_no_overclaim(
            &redacted,
            &["guaranteed profit".into(), "alpha leak".into()],
        )
        .unwrap();
    }
}
