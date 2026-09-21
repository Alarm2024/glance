# Glance

Honest status for Solana bots — open-source observability with fault-first doctor status, redaction, and anti-overclaim tests.

**Live demo:** [glance-35.elghaly.dev](https://glance-35.elghaly.dev/)

## Run tests

```bash
# Rust
cd lib/rust/glance-status && cargo test

# Python
cd python/glance_status && pip install -e ".[dev]" && pytest -q
```

CI runs both on every pull request (`.github/workflows/ci.yml`).

## Rust usage (pre-1.0)

```toml
# Cargo.toml
glance-status = { path = "lib/rust/glance-status" }
```

```rust
use glance_status::{
    assert_no_overclaim, classify_fault, redact, ClassifyInput, DoctorStatus,
};

let status = classify_fault(
    &ClassifyInput {
        blocking: false,
        lines: &["slot lag detected", "info: heartbeat ok"],
    },
    &["info:"],           // hygiene/info exclusion
    &["slot lag"],        // fault-phrase allowlist
);
assert_eq!(status, DoctorStatus::EyesFault);

let safe = redact("see https://api.example.com/v1?token=secret");
assert_no_overclaim(&safe, &["guaranteed", "profit"]).unwrap();
```

## Python usage (pre-1.0)

```bash
pip install -e python/glance_status
```

```python
from glance_status import (
    ClassifyInput,
    DoctorStatus,
    assert_no_overclaim,
    classify_fault,
    redact,
)

status = classify_fault(
    ClassifyInput(blocking=False, lines=["slot lag detected"]),
    hygiene_patterns=["info:"],
    fault_phrases=["slot lag"],
)
assert status is DoctorStatus.EYES_FAULT

safe = redact("see https://api.example.com/v1?token=secret")
assert_no_overclaim(safe, ["guaranteed", "profit"])
```

## `demo/fixture.json` schema

Synthetic demo data only — **not live bot data**. Top-level fields:

| Field | Type | Card | Description |
|-------|------|------|-------------|
| `synthetic` | `bool` | — | Must be `true` for demo fixtures |
| `label` | `string` | — | Banner text (e.g. `DEMO / SYNTHETIC — not live bot data`) |
| `generated_at` | `string` (ISO-8601) | — | Fixture generation timestamp |
| `online` | `object` | Online | `status`, `uptime`, `detail` |
| `posture` | `object` | Posture | `mode`, `detail` |
| `doctor` | `object` | Doctor | `status` (`ok` \| `warn` \| `eyes_fault` \| `blocking` \| `unknown`), `summary`, `detail` |
| `feeds` | `array` | Feeds | Items with `name`, `state`, `age` |
| `last_signal` | `object` | Last signal | `kind`, `ago`, `detail` |
| `build` | `object` | Build | `version`, `commit`, `detail` |

Card render order: **Online → Posture → Doctor → Feeds → Last signal → Build**

## Site files

| File | Purpose |
|------|---------|
| `index.html` | Landing page |
| `css/style.css` | Ink + gold theme (matches [elghaly.dev](https://elghaly.dev/)) |
| `app.js` | Renders status cards from fixture |
| `demo/fixture.json` | **Synthetic** demo data — not live bot data |
| `CNAME` | Custom domain for GitHub Pages |
| `lib/rust/glance-status/` | Rust crate — doctor status, redaction, overclaim guard |
| `python/glance_status/` | Python mirror stub with the same API names |

## License

MIT · free · no strategy or alpha included
