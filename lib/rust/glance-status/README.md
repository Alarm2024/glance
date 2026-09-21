# glance-status

Rust library for Glance honest status: doctor classification, redaction, and anti-overclaim checks.

**Status:** pre-1.0 · not yet on [crates.io](https://crates.io/crates/glance-status).

## Install

From this repository:

```toml
glance-status = { path = "lib/rust/glance-status" }
```

After publish (not live yet):

```toml
glance-status = "0.1.0"
```

## Usage

```rust
use glance_status::{assert_no_overclaim, classify, redact, ClassifyInput, DoctorStatus};

let status = classify(&ClassifyInput {
    blocking_flag: false,
    hygiene_phrases: vec!["hygiene".into()],
    fault_phrases: vec!["stale".into()],
    raw_message: "Feed stale for 47s".into(),
});
assert_eq!(status, DoctorStatus::Warn);

let safe = redact("see https://example.com/x?token=secret");
assert_no_overclaim(&safe, &["guaranteed".into()]).unwrap();
```

## Guide

See [Add Glance in 15 minutes](https://github.com/Alarm2024/glance/blob/main/docs/add-glance-in-15-minutes.md).

## License

MIT
