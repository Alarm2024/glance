# Glance glossary

One-page definitions for terms used across the site, proof lab, and libraries.
Everything else links here.

## Eyes

**Glance eyes** — fault-first health cards (Online, Posture, Doctor, Feeds, Last signal, Build).
Read-only observability: what the operator sees before any action. Eyes never send, arm, or mint.

## Doctor

**Doctor** — the classifier layer that turns raw operator/daemon messages into status:
`ok`, `warn`, `eyes_fault`, `blocking`, or `unknown`.

Evaluation order is fixed:

1. `blocking_flag`
2. hygiene phrase exclusion (caller-supplied allowlist)
3. fault phrase allowlist (caller-supplied)
4. `unknown` when nothing matches — **REFUSE TO CLASSIFY**

See [`lib/python/glance_status/__init__.py`](../lib/python/glance_status/__init__.py) (`classify`).

## Posture

**Posture** — how the process is configured to behave: dry compose, dry simulate, observe-only, eyes-only.
Posture must stay dry on public demos — no auto-send, armed, or mint language.

See [`demo/fixture.schema.md`](../demo/fixture.schema.md) and [`lib/python/glance_status/posture.py`](../lib/python/glance_status/posture.py).

## CLEAR

**Operator CLEAR** — explicit human gate. The system may evaluate gates and say HOLD or CLEAR,
but only a human operator may CLEAR. No auto-send. HOLD means wait for human review.

The [CLEAR LAB proof page](../proof/index.html) shows synthetic cases where the gate stays HOLD.
Cases state what was observed and what was refused — never what would have happened if a trade had landed.

## HOLD

**HOLD** — gate decision: do not proceed. Reasons include stale oracle feeds, thin liquidity below floor,
unclassified doctor messages, or blocking/warn doctor status. Thresholds are fixed in
[`lib/python/glance_status/gate.py`](../lib/python/glance_status/gate.py).

## Evidence hash

**Evidence hash** — SHA-256 of canonical JSON listing which gates ran, threshold values, and check results.
Reproducible via `python3 scripts/run_proof.py` — no keys, no network, fixtures only — must match the proof page.

Same fixture in, same decision out. This proves the case was not changed after the fact.
It does not prove the decision was right.

Case copy gates live in [`lib/python/glance_status/case_wording.py`](../lib/python/glance_status/case_wording.py).
Cases that reference an earn schedule cannot ship until page 35 states what a credit is for.
