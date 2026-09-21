# demo/fixture.json schema

**Synthetic demo data only** — never live bot payloads. The site banner and top-level
`synthetic` / `label` fields must stay present.

Card render order (matches site): **Online → Posture → Doctor → Feeds → Last signal → Build**

## Top level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `synthetic` | boolean | yes | Must be `true` for demo fixtures |
| `label` | string | yes | Banner text, e.g. `DEMO / SYNTHETIC — not live bot data` |
| `generated_at` | string (ISO-8601) | yes | Fixture generation timestamp |
| `online` | object | yes | Online card |
| `posture` | object | yes | Posture card |
| `doctor` | object | yes | Doctor card |
| `feeds` | array | yes | Feeds card (list of feed objects) |
| `last_signal` | object | yes | Last signal card |
| `build` | object | yes | Build card |

## `online`

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | e.g. `connected` |
| `uptime` | string | Human-readable uptime |
| `detail` | string | Optional detail line |

## `posture`

| Field | Type | Description |
|-------|------|-------------|
| `mode` | string | e.g. `observe-only` |
| `detail` | string | Optional detail line |

## `doctor`

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | One of: `ok`, `warn`, `eyes_fault`, `blocking`, `unknown` |
| `summary` | string | Short headline |
| `detail` | string | Optional detail line |

## `feeds[]`

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Feed identifier |
| `state` | string | e.g. `ok`, `stale`, `unknown` |
| `age` | string | Human-readable age |

## `last_signal`

| Field | Type | Description |
|-------|------|-------------|
| `kind` | string | Signal type, e.g. `heartbeat` |
| `ago` | string | Human-readable recency |
| `detail` | string | Optional detail line |

## `build`

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Build / crate version label |
| `commit` | string | Short commit or fixture tag |
| `detail` | string | Optional detail line |
