# Glance

Open-source honest status for Solana bot operators.

**Demo (synthetic):** [glance.elghaly.dev](https://glance.elghaly.dev/) · **CLEAR LAB proof:** [glance.elghaly.dev/proof/](https://glance.elghaly.dev/proof/)

## Install

| Language | Package | Status |
|----------|---------|--------|
| Rust | `glance-status` | pre-1.0 · path install ([crates.io](https://crates.io/crates/glance-status) not yet published) |
| Python | `glance-status` | pre-1.0 · editable install ([PyPI](https://pypi.org/project/glance-status/) not yet published) |

Rust — in your Cargo.toml (until crates.io publish). `path` is relative to that Cargo.toml, not to this repo; [`examples/rust-cli/Cargo.toml`](examples/rust-cli/Cargo.toml) uses `../../lib/rust/glance-status` from its own directory.

```toml
[dependencies]
glance-status = { path = "lib/rust/glance-status" }
```

Python — editable install (until PyPI publish), from the repo root:

```bash
# Seen failing on stock Ubuntu 22.04 system packages (python3-pip 22.0.2 + python3-setuptools 59.6.0):
# "missing the 'build_editable' hook". pip 22.0.2 inside a fresh venv worked when tested. Upgrading pip in the venv avoids it either way.
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e lib/python
# Without installing: PYTHONPATH=lib/python python3 scripts/posture_selftest.py
```

Target registry install after M1 publish (not live yet):

Rust — in your Cargo.toml:

```toml
[dependencies]
glance-status = "0.1.0"
```

Python:

```bash
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

Synthetic proof cases show why the operator gate says **HOLD** — same decision and evidence hash on the page and in your terminal.
No keys, no network, fixtures only. Cases state what was observed and refused — never counterfactual outcomes.

```bash
git clone https://github.com/Alarm2024/glance && cd glance && python3 scripts/run_proof.py
```

The git clone gives you the main branch.

You should see each `decision: HOLD` line and evidence hashes matching [proof/](proof/index.html).
Same evidence in, same hash out — the hash covers the checks, thresholds and reason code, so parity proves those were not changed after the fact. It does not cover the rest of the fixture file, and does not prove the decision was right.

| Case | Reason code |
|------|-------------|
| stale-oracle | Oracle feed stale — price reference unreliable |
| thin-liquidity | Depth below $5,000 floor |
| refuse-to-classify | Doctor message unmatched — REFUSE TO CLASSIFY |
| all-green | All indicators green — no running process observed |
| mostly-green | No fault on board — no running process observed |
| fault-board | At least one indicator in a fault state |

Fixtures: [`proof/fixtures/`](proof/fixtures/) · Gate logic: [`lib/python/glance_status/gate.py`](lib/python/glance_status/gate.py)

## Deployment receipt

Read-only checker for declared public deployment assets — fetches each URL, hashes the bytes, and prints one JSON record per asset. Manifest: [`proof/deployment-receipt.json`](proof/deployment-receipt.json) · Runner: [`scripts/deployment_receipt.py`](scripts/deployment_receipt.py).

The hostname is resolved during validation and again when connecting. A hostile resolver can answer with a public address and then a private one. This is not closed. Closing it requires pinning the resolved address and connecting to it directly.

## Examples

Each command runs in a subshell from the repo root, so they can be pasted together or run independently. The venv line is not in a subshell on purpose: the activation has to persist for the `pip install -e` that follows.

```bash
# Rust CLI
(cd examples/rust-cli && cargo run -- demo)

# Python CLI
# Seen failing on stock Ubuntu 22.04 system packages (python3-pip 22.0.2 + python3-setuptools 59.6.0):
# "missing the 'build_editable' hook". pip 22.0.2 inside a fresh venv worked when tested. Upgrading pip in the venv avoids it either way.
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
(cd lib/python && pip install -e . && python ../../examples/python-cli/glance_cli.py demo)
```

## Demo fixture schema

Synthetic only — see [`demo/fixture.schema.md`](demo/fixture.schema.md).

Card order: **Online → Posture → Doctor → Feeds → Last signal → Build**

The demo (synthetic) includes a **playground**: paste your own status JSON in the textarea (or leave it empty for the synthetic fixture). Rendering is client-side only — no backend call.

## Status badge

[`netlify/functions/badge.mjs`](netlify/functions/badge.mjs) returns a shields.io-style SVG. GitHub Pages, which serves glance.elghaly.dev, does not run that function, so `https://glance.elghaly.dev/badge?status=ok` is a 404. The snippet below is a template for a host that runs the function (Netlify applies the `/badge` redirect in [`netlify.toml`](netlify.toml)):

```markdown
![glance status](https://<your-function-host>/badge?status=ok)
```

Supported `status` values: `ok`, `warn`, `blocking`.

## glance-check GitHub Action

Fail CI when status strings contain banned overclaim phrases:

Runnable as-is in a clone of this repo (`demo/fixture.json` ships with it):

```yaml
- uses: Alarm2024/glance/.github/actions/glance-check@main
  with:
    paths: |
      demo/fixture.json
```

In your own repo, list the status files your pipeline writes. `status.json` below is a placeholder for a file **you create** before this step; it is not in this repo. Since #27, any listed path that does not exist fails the job (`requested path does not exist: status.json`):

```yaml
- run: ./your-bot --dump-status > status.json   # caller-created: your step writes this file
- uses: Alarm2024/glance/.github/actions/glance-check@main
  with:
    paths: |
      status.json
```

glance-check scans only the files it is given. When `paths` is set, that list is the whole scan: a green result covers those files and no others. When `paths` is empty or only whitespace, the only files it may scan are `demo/fixture.json` and `status.json`, and only when the file exists.

Set `paths`. If it is empty and no default file (`demo/fixture.json`, `status.json`) exists, zero files are scanned and the job fails with ``glance: no files to scan - set `paths` `` — the gate fails closed instead of passing silently. Draft notes for 0.1.0, including that break: [docs/v0.1.0.md](docs/v0.1.0.md).

See [`.github/actions/glance-check/README.md`](.github/actions/glance-check/README.md) for inputs and behavior.

## Tests & CI

From the repo root. The venv line is not in a subshell so the activation persists for the `pip install -e` that follows.

```bash
(cd lib/rust/glance-status && cargo test)
# Seen failing on stock Ubuntu 22.04 system packages (python3-pip 22.0.2 + python3-setuptools 59.6.0):
# "missing the 'build_editable' hook". pip 22.0.2 inside a fresh venv worked when tested. Upgrading pip in the venv avoids it either way.
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
(cd lib/python && pip install -e ".[dev]" && python -m pytest -v)
(cd examples/rust-cli && cargo run -- demo)
```

GitHub Actions runs Rust + Python tests on every pull request. crates.io / PyPI publish is a post-M1 milestone.

## License

MIT — see [LICENSE](LICENSE). Free forever · no strategy or alpha included · synthetic demo data only.

Contact: [support@elghaly.dev](mailto:support@elghaly.dev)
