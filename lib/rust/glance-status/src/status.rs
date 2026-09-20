use std::fmt;
use std::str::FromStr;

/// Doctor panel status — ordered from healthy to most severe.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum DoctorStatus {
    Ok,
    Warn,
    EyesFault,
    Blocking,
    Unknown,
}

impl DoctorStatus {
    /// Wire / JSON string for demo fixtures and dashboards.
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
    fn round_trip_wire_values() {
        for value in ["ok", "warn", "eyes_fault", "blocking", "unknown"] {
            let status: DoctorStatus = value.parse().unwrap();
            assert_eq!(status.as_str(), value);
            assert_eq!(status.to_string(), value);
        }
    }

    #[test]
    fn invalid_wire_value() {
        assert!("not-a-status".parse::<DoctorStatus>().is_err());
    }
}
