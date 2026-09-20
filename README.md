# Glance

Honest status for Solana bots — open-source observability with fault-first doctor status, redaction, and anti-overclaim tests.

**Live demo:** [glance-35.elghaly.dev](https://glance-35.elghaly.dev/)

## Libraries

| Path | Package | Status |
|------|---------|--------|
| `lib/rust/glance-status` | `glance-status` | M1 skeleton |
| `lib/python/glance_status` | `glance_status` | Thin Python mirror |

## Rust usage

```toml
# Cargo.toml (path dep until crates.io publish)
glance-status = { path = "lib/rust/glance-status" }
```

```rust
use glance_status::{
    assert_no_overclaim, classify_fault, redact, DoctorStatus, FaultClassifierConfig, FaultInput,
};

let status = classify_fault(
    &FaultInput {
        blocking_flag: false,
        lines: &["price-oracle stale feed detected"],
    },
    &FaultClassifierConfig {
        hygiene_phrases: &["heartbeat ok"],
        fault_phrases: &["stale feed", "eyes desync"],
    },
);
assert_eq!(status, DoctorStatus::Warn);

let safe = redact("see https://api.example.com/v1?token=secret");
assert_no_overclaim("No blocking flags", &["guaranteed profit"]).unwrap();
```

### Run Rust tests

```bash
cd lib/rust/glance-status
cargo test
```

## Python usage

```bash
cd lib/python/glance_status
pip install -e ".[dev]"
```

```python
from glance_status import DoctorStatus, assert_no_overclaim, classify_fault, redact

status = classify_fault(
    blocking_flag=False,
    lines=["price-oracle stale feed detected"],
    hygiene_phrases=["heartbeat ok"],
    fault_phrases=["stale feed", "eyes desync"],
)
assert status == DoctorStatus.WARN

safe = redact("see https://api.example.com/v1?token=secret")
assert_no_overclaim("No blocking flags", ["guaranteed profit"])
```

### Run Python tests

```bash
cd lib/python/glance_status
pytest -q
```

## Site files

| File | Purpose |
|------|---------|
| `index.html` | Landing page |
| `css/style.css` | Ink + gold theme (matches [elghaly.dev](https://elghaly.dev/)) |
| `app.js` | Renders status cards from fixture |
| `demo/fixture.json` | **Synthetic** demo data — not live bot data |
| `demo/SCHEMA.md` | Fixture JSON schema for status cards |
| `CNAME` | Custom domain for GitHub Pages |

## Card order

Online → Posture → Doctor → Feeds → Last signal → Build

## CI

GitHub Actions runs `cargo test` and `pytest` on every pull request (see [`.github/workflows/ci.yml`](.github/workflows/ci.yml)).

## License

MIT · free · no strategy or alpha included
