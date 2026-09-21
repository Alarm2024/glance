# Add Glance in 15 minutes

Quick path to honest status checks in your operator tooling.

## 1. Install

**Rust** (pre-1.0 path install — crates.io publish pending)

```toml
glance-status = { path = "lib/rust/glance-status" }
```

**Python** (pre-1.0 editable — PyPI publish pending)

```bash
pip install -e lib/python
```

## 2. Classify doctor messages

Supply your own hygiene and fault phrase lists — Glance never hardcodes your strategy vocabulary.

```rust
let status = classify(&ClassifyInput {
    blocking_flag: false,
    hygiene_phrases: vec!["hygiene".into(), "passed".into()],
    fault_phrases: vec!["stale".into(), "timeout".into()],
    raw_message: message.to_string(),
});
```

Order: `blocking_flag` → hygiene exclusion → fault allowlist → `Unknown`.

## 3. Redact before display

```rust
let safe = redact(&raw_status_line);
```

Strips URLs with query params, hex/base58 key shapes, and common API-key patterns.

## 4. Block overclaim language

```rust
assert_no_overclaim(&safe, &["guaranteed".into(), "profit".into(), "alpha".into()])?;
```

## 5. Wire to your dashboard

Emit JSON matching the [demo fixture schema](../demo/fixture.schema.md) and render with the Glance dashboard template at [glance.elghaly.dev](https://glance.elghaly.dev/).

MIT · synthetic demo data only · no strategy included.
