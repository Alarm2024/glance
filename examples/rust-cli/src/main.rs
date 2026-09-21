//! Minimal CLI demo for classify_fault, redact, and assert_no_overclaim.

use glance_status::{assert_no_overclaim, classify_fault, redact, ClassifierInput, DoctorStatus};
use std::env;
use std::process;

fn main() {
    let mut args = env::args().skip(1);
    let cmd = args.next().unwrap_or_else(|| usage());

    match cmd.as_str() {
        "classify" => {
            let message = args.next().unwrap_or_else(|| "Hygiene checks passed".to_string());
            let status = classify_fault(ClassifierInput {
                blocking: false,
                message: &message,
                hygiene_phrases: &["hygiene", "passed"],
                fault_phrases: &["stale", "timeout", "degraded"],
                eyes_fault_phrases: &["observer fault", "eyes offline"],
            });
            println!("{}", status.as_str());
        }
        "redact" => {
            let input = args.collect::<Vec<_>>().join(" ");
            if input.is_empty() {
                eprintln!("usage: glance-status-cli redact <text>");
                process::exit(1);
            }
            println!("{}", redact(&input));
        }
        "assert-no-overclaim" => {
            let status = args.next().unwrap_or_else(|| {
                eprintln!("usage: glance-status-cli assert-no-overclaim <status> [banned...]");
                process::exit(1);
            });
            let banned: Vec<String> = args.collect();
            let default = ["guaranteed", "profit", "alpha"];
            let phrases: Vec<&str> = if banned.is_empty() {
                default.to_vec()
            } else {
                banned.iter().map(String::as_str).collect()
            };
            match assert_no_overclaim(&status, &phrases) {
                Ok(()) => println!("ok"),
                Err(e) => {
                    eprintln!("{e}");
                    process::exit(1);
                }
            }
        }
        "demo" => {
            let status = classify_fault(ClassifierInput {
                blocking: false,
                message: "Feed stale for 47s",
                hygiene_phrases: &["hygiene"],
                fault_phrases: &["stale"],
                eyes_fault_phrases: &["observer fault"],
            });
            assert_eq!(status, DoctorStatus::Warn);
            let safe = redact("see https://example.com/x?token=secret");
            assert_no_overclaim(&safe, &["guaranteed profit"]).unwrap();
            println!("demo ok · status={} · redacted={safe}", status.as_str());
        }
        _ => usage(),
    }
}

fn usage() -> ! {
    eprintln!(
        "usage: glance-status-cli {{classify|redact|assert-no-overclaim|demo}} [args...]"
    );
    process::exit(1);
}
