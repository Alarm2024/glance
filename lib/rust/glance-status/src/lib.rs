//! Glance status primitives — doctor classification, redaction, anti-overclaim checks.
//!
//! Pre-1.0 M1 skeleton. Synthetic demo data only; no live bot wiring.

mod classifier;
mod overclaim;
mod redact;

pub use classifier::{classify_fault, ClassifierInput, DoctorStatus};
pub use overclaim::{assert_no_overclaim, OverclaimError};
pub use redact::redact;

#[cfg(test)]
mod integration_tests {
    use super::*;

    #[test]
    fn doctor_status_variants_as_str() {
        assert_eq!(DoctorStatus::Ok.as_str(), "ok");
        assert_eq!(DoctorStatus::Warn.as_str(), "warn");
        assert_eq!(DoctorStatus::EyesFault.as_str(), "eyes_fault");
        assert_eq!(DoctorStatus::Blocking.as_str(), "blocking");
        assert_eq!(DoctorStatus::Unknown.as_str(), "unknown");
    }

    #[test]
    fn end_to_end_fixture_doctor_line() {
        let status = classify_fault(ClassifierInput {
            blocking: false,
            message: "Hygiene checks passed · config exclusions applied",
            hygiene_phrases: &["hygiene", "config exclusion"],
            fault_phrases: &["fault", "error", "stale feed"],
            eyes_fault_phrases: &["eyes offline", "observer fault"],
        });
        assert_eq!(status, DoctorStatus::Ok);

        let redacted = redact("detail ok");
        assert_no_overclaim(&redacted, &["guaranteed profit", "alpha leak"]).unwrap();
    }
}
