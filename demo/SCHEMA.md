# Demo fixture schema

`demo/fixture.json` drives the live status cards at [glance-35.elghaly.dev](https://glance-35.elghaly.dev/).

**All fixtures must stay synthetic.** Set `"synthetic": true` and a clear `"label"` — never ship real bot data.

## Top level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `synthetic` | boolean | yes | Must be `true` for demo fixtures |
| `label` | string | yes | Banner text, e.g. `DEMO / SYNTHETIC — not live bot data` |
| `generated_at` | string (ISO-8601) | yes | When the fixture was generated |
| `online` | object | yes | Online card |
| `posture` | object | yes | Posture card |
| `doctor` | object | yes | Doctor card |
| `feeds` | array | yes | Feeds card (list of feed rows) |
| `last_signal` | object | yes | Last signal card |
| `build` | object | yes | Build card |

## Card order (render)

Online → Posture → Doctor → Feeds → Last signal → Build

## `online`

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | e.g. `connected` |
| `uptime` | string | Human-readable uptime |
| `detail` | string | Free-form detail line |

## `posture`

| Field | Type | Description |
|-------|------|-------------|
| `mode` | string | e.g. `observe-only` |
| `detail` | string | Free-form detail line |

## `doctor`

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | One of `ok`, `warn`, `eyes_fault`, `blocking`, `unknown` (see `glance-status`) |
| `summary` | string | Short headline for the card |
| `detail` | string | Secondary detail line |

## `feeds[]`

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Feed identifier |
| `state` | string | e.g. `ok`, `stale` |
| `age` | string | Human-readable age, e.g. `1.2s` |

## `last_signal`

| Field | Type | Description |
|-------|------|-------------|
| `kind` | string | Signal kind, e.g. `heartbeat` |
| `ago` | string | Human-readable recency |
| `detail` | string | Free-form detail line |

## `build`

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Semver or demo tag |
| `commit` | string | Short commit or fixture tag |
| `detail` | string | Free-form detail line |

## Example

See [`fixture.json`](fixture.json) in this directory.
