//! Minimal CLI demo for classify, redact, and assert_no_overclaim.

use glance_status::{assert_no_overclaim, classify, redact, ClassifyInput, DoctorStatus};
use std::env;
use std::process;

fn main() {
    let mut args = env::args().skip(1);
    let cmd = args.next().unwrap_or_else(|| usage());

    match cmd.as_str() {
        "classify" => {
            let message = args.next().unwrap_or_else(|| "Hygiene checks passed".to_string());
            let status = classify(&ClassifyInput {
                blocking_flag: false,
                hygiene_phrases: vec!["hygiene".into(), "passed".into()],
                fault_phrases: vec!["stale".into(), "timeout".into(), "degraded".into()],
                raw_message: message,
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
            let banned: Vec<String> = if args.len() > 0 {
                args.collect()
            } else {
                vec![
                    "guaranteed".into(),
                    "profit".into(),
                    "alpha".into(),
                ]
            };
            match assert_no_overclaim(&status, &banned) {
                Ok(()) => println!("ok"),
                Err(e) => {
                    eprintln!("{e}");
                    process::exit(1);
                }
            }
        }
        "demo" => {
            let status = classify(&ClassifyInput {
                blocking_flag: false,
                hygiene_phrases: vec!["hygiene".into()],
                fault_phrases: vec!["stale".into()],
                raw_message: "Feed stale for 47s".into(),
            });
            assert_eq!(status, DoctorStatus::Warn);
            let safe = redact("see https://example.com/x?token=secret");
            assert_no_overclaim(&safe, &["guaranteed profit".into()]).unwrap();
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
