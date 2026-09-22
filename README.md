# Glance

Open-source honest status for Solana bot operators.

**Demo (synthetic):** [glance.elghaly.dev](https://glance.elghaly.dev/) · **CLEAR LAB proof:** [glance.elghaly.dev/proof/](https://glance.elghaly.dev/proof/)

## Install

| Language | Package | Status |
|----------|---------|--------|
| Rust | `glance-status` | pre-1.0 · path install ([crates.io](https://crates.io/crates/glance-status) not yet published) |
| Python | `glance-status` | pre-1.0 · editable install ([PyPI](https://pypi.org/project/glance-status/) not yet published) |

```bash
# Rust — local path (until crates.io publish)
glance-status = { path = "lib/rust/glance-status" }

# Python — editable install (until PyPI publish)
pip install -e lib/python
```

Target registry install after M1 publish:

```bash
# Rust — Cargo.toml (not live yet)
glance-status = "0.1.0"

# Python (not live yet)
pip install glance-status
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

Terms: [Glossary](docs/glossary.md) (Eyes, Doctor, Posture, CLEAR).

## CLEAR LAB — reproduce HOLD proof (stranger path)

Three synthetic cases show why the operator gate says **HOLD** — same decision and evidence hash on the page and in your terminal.
No keys, no network, fixtures only. Cases state what was observed and refused — never counterfactual outcomes.

```bash
git clone https://github.com/Alarm2024/glance && cd glance && python3 scripts/run_proof.py
```

You should see three `decision: HOLD` lines and evidence hashes matching [proof/](proof/index.html).
Same fixture in, same decision out — hash parity proves the case was not changed after the fact, not that the decision was right.

| Case | Reason code |
|------|-------------|
| stale-oracle | Oracle feed stale — price reference unreliable |
| thin-liquidity | Depth below $5,000 floor |
| refuse-to-classify | Doctor message unmatched — REFUSE TO CLASSIFY |

Fixtures: [`proof/fixtures/`](proof/fixtures/) · Gate logic: [`lib/python/glance_status/gate.py`](lib/python/glance_status/gate.py)

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

The demo (synthetic) includes a **playground**: paste your own status JSON in the textarea (or leave it empty for the synthetic fixture). Rendering is client-side only — no backend call.

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

GitHub Actions runs Rust + Python tests on every pull request. crates.io / PyPI publish is a post-M1 milestone.

## License

MIT — see [LICENSE](LICENSE). Free forever · no strategy or alpha included · synthetic demo data only.

Contact: [support@elghaly.dev](mailto:support@elghaly.dev)
