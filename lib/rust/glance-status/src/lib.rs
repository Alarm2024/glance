//! Glance status helpers — fault-first doctor classification, redaction, anti-overclaim.

mod classify;
mod overclaim;
mod redact;

pub use classify::{classify_fault, ClassifyInput};
pub use overclaim::{assert_no_overclaim, OverclaimError};
pub use redact::redact;

use std::fmt;
use std::str::FromStr;

/// Doctor card status values matching the demo fixture schema.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum DoctorStatus {
    Ok,
    Warn,
    EyesFault,
    Blocking,
    Unknown,
}

impl DoctorStatus {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Ok => "ok",
            Self::Warn => "warn",
            Self::EyesFault => "eyes_fault",
            Self::Blocking => "blocking",
            Self::Unknown => "unknown",
        }
    }
}

impl fmt::Display for DoctorStatus {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(self.as_str())
    }
}

impl FromStr for DoctorStatus {
    type Err = ();

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "ok" => Ok(Self::Ok),
            "warn" => Ok(Self::Warn),
            "eyes_fault" => Ok(Self::EyesFault),
            "blocking" => Ok(Self::Blocking),
            "unknown" => Ok(Self::Unknown),
            _ => Err(()),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn doctor_status_roundtrip_strings() {
        for variant in [
            DoctorStatus::Ok,
            DoctorStatus::Warn,
            DoctorStatus::EyesFault,
            DoctorStatus::Blocking,
            DoctorStatus::Unknown,
        ] {
            let s = variant.as_str();
            assert_eq!(DoctorStatus::from_str(s).unwrap(), variant);
        }
    }

    #[test]
    fn doctor_status_unknown_for_invalid() {
        assert!(DoctorStatus::from_str("profit").is_err());
    }
}
