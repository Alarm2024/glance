//! Glance status — fault-first doctor status, redaction, and anti-overclaim checks.

mod classify;
mod overclaim;
mod redact;
mod status;

pub use classify::{classify_fault, FaultClassifierConfig, FaultInput};
pub use overclaim::{assert_no_overclaim, OverclaimError};
pub use redact::redact;
pub use status::DoctorStatus;
