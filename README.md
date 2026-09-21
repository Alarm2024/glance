# Glance

Open-source honest status for Solana bot operators.

**Live demo:** [glance.elghaly.dev](https://glance.elghaly.dev/)

## Install

| Language | Package | Registry |
|----------|---------|----------|
| Rust | `glance-status` | [crates.io/crates/glance-status](https://crates.io/crates/glance-status) |
| Python | `glance-status` | [pypi.org/project/glance-status](https://pypi.org/project/glance-status/) |

```bash
# Rust — Cargo.toml
glance-status = "0.1.0"

# Python
pip install glance-status
```

Local development:

```bash
# Rust path dependency
glance-status = { path = "lib/rust/glance-status" }

# Python editable
pip install -e lib/python
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

```python
from glance_status import ClassifyInput, DoctorStatus, assert_no_overclaim, classify, redact

status = classify(
    ClassifyInput(
        blocking_flag=False,
        raw_message="Feed stale for 47s",
        fault_phrases=["stale"],
    )
)
assert status == DoctorStatus.WARN

safe = redact("auth sk-live-abcdefghijklmnopqrstuvwxyz")
assert_no_overclaim(safe, ["profit"])
```

See [Add Glance in 15 minutes](docs/add-glance-in-15-minutes.md) for a quick integration guide.

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

GitHub Actions runs Rust + Python tests on every pull request. Releases publish to crates.io and PyPI.

## License

MIT — see [LICENSE](LICENSE). Free forever · no strategy or alpha included · synthetic demo data only.

Contact: [support@elghaly.dev](mailto:support@elghaly.dev)
