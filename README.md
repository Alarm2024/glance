# Glance

Open-source honest status for Solana bot operators.

- Live demo: https://glance.elghaly.dev/
- License: MIT
- Contact: support@elghaly.dev

## Libraries

- `lib/rust/glance-status` — Rust crate
- `lib/python` — Python package `glance_status`

```bash
cd lib/rust/glance-status && cargo test
cd lib/python && pip install -e ".[dev]" && python -m pytest -v
```

## Demo fixture

Synthetic only — `demo/fixture.json` is labeled DEMO / SYNTHETIC.

## Hard rules

No trading strategy, sizes, pins, wallets, RPCs, or secrets in this repo.
