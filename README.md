# Glance

Honest status for Solana bots — open-source observability with fault-first doctor status, redaction, and anti-overclaim tests.

**Live demo:** [glance-35.elghaly.dev](https://glance-35.elghaly.dev/)

## Site files

| File | Purpose |
|------|---------|
| `index.html` | Landing page |
| `css/style.css` | Ink + gold theme (matches [elghaly.dev](https://elghaly.dev/)) |
| `app.js` | Renders status cards from fixture |
| `demo/fixture.json` | **Synthetic** demo data — not live bot data |
| `demo/fixture.schema.md` | JSON schema for fixture cards |
| `CNAME` | Custom domain for GitHub Pages |

## Card order

Online → Posture → Doctor → Feeds → Last signal → Build

## Libraries (M1 skeleton)

| Path | Package |
|------|---------|
| `lib/rust/glance-status` | `glance-status` crate |
| `lib/python` | `glance_status` PyPI-style stub |

### Rust usage

```toml
# Cargo.toml (local path until crates.io publish)
glance-status = { path = "lib/rust/glance-status" }
```

```rust
use glance_status::{
    assert_no_overclaim, classify_fault, redact, ClassifierInput, DoctorStatus,
};

let status = classify_fault(ClassifierInput {
    blocking: false,
    message: "Hygiene checks passed",
    hygiene_phrases: &["hygiene"],
    fault_phrases: &["stale", "timeout"],
    eyes_fault_phrases: &["observer fault"],
});
assert_eq!(status, DoctorStatus::Ok);

let safe = redact("see https://example.com/x?token=secret");
assert_no_overclaim(&safe, &["guaranteed profit"]).unwrap();
```

### Python usage

```bash
pip install -e lib/python
```

```python
from glance_status import classify_fault, redact, assert_no_overclaim, DoctorStatus

status = classify_fault(
    blocking=False,
    message="Feed stale for 47s",
    fault_phrases=["stale"],
)
assert status == DoctorStatus.WARN

safe = redact("auth sk-live-abcdefghijklmnopqrstuvwxyz")
assert_no_overclaim(safe, ["guaranteed", "profit"])
```

## Run tests locally

```bash
# Rust
cd lib/rust/glance-status && cargo test

# Python
cd lib/python && pip install -e ".[dev]" && pytest -v
```

CI runs both on every pull request (`.github/workflows/ci.yml`).

## License

MIT · free · no strategy or alpha included
