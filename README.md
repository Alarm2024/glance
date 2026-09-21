# Glance

Open-source honest status for Solana bot operators.

**Live demo:** [glance.elghaly.dev](https://glance.elghaly.dev/)

## Install

| Language | Path / package | Status |
|----------|----------------|--------|
| Rust | `lib/rust/glance-status` (`glance-status`) | pre-1.0 local path |
| Python | `lib/python` (`glance_status`) | pre-1.0 editable install |

```bash
# Rust — add to Cargo.toml
glance-status = { path = "lib/rust/glance-status" }

# Python
pip install -e lib/python
```

## Usage

```rust
use glance_status::{assert_no_overclaim, classify_fault, redact, ClassifierInput, DoctorStatus};

let status = classify_fault(ClassifierInput {
    blocking: false,
    message: "Hygiene checks passed",
    hygiene_phrases: &["hygiene"],
    fault_phrases: &["stale"],
    eyes_fault_phrases: &["observer fault"],
});
let safe = redact("see https://example.com/x?token=secret");
assert_no_overclaim(&safe, &["guaranteed profit"]).unwrap();
```

```python
from glance_status import classify_fault, redact, assert_no_overclaim

status = classify_fault(blocking=False, message="Feed stale", fault_phrases=["stale"])
safe = redact("auth sk-live-abcdefghijklmnopqrstuvwxyz")
assert_no_overclaim(safe, ["profit"])
```

## Examples

```bash
# Rust CLI
cd examples/rust-cli && cargo run -- demo

# Python CLI
cd lib/python && pip install -e . && python ../../examples/python-cli/glance_cli.py demo
```

## Demo fixture schema

Synthetic only — see [`demo/fixture.schema.md`](demo/fixture.schema.md).

Card order: **Online → Posture → Doctor → Feeds → Last signal → Build**

The live demo includes a **playground**: paste your own status JSON in the textarea (or leave it empty for the synthetic fixture). Rendering is client-side only — no backend call.

## Status badge

Embed a shields.io-style SVG badge in your README (requires Netlify or compatible deploy with serverless functions):

```markdown
![glance status](https://glance.elghaly.dev/badge?status=ok)
```

Supported `status` values: `ok`, `warn`, `blocking`.

## glance-check GitHub Action

Fail CI when status strings contain banned overclaim phrases:

```yaml
- uses: Alarm2024/glance/.github/actions/glance-check@main
  with:
    paths: |
      demo/fixture.json
      status.json
```

See [`.github/actions/glance-check/README.md`](.github/actions/glance-check/README.md) for inputs and behavior.

## Tests & CI

```bash
cd lib/rust/glance-status && cargo test
cd lib/python && pip install -e ".[dev]" && python -m pytest -v
cd examples/rust-cli && cargo run -- demo
```

GitHub Actions runs Rust + Python tests on every pull request.

## License

MIT — see [LICENSE](LICENSE). Free forever · no strategy or alpha included · synthetic demo data only.

Contact: [support@elghaly.dev](mailto:support@elghaly.dev)
