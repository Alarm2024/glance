# glance-check

Composite GitHub Action that runs `assert_no_overclaim()` against status strings in your repository.

## Usage

```yaml
- uses: Alarm2024/glance/.github/actions/glance-check@main
  with:
    paths: |
      demo/fixture.json
      status.json
    banned-phrases: guaranteed,profit,alpha
```

## Inputs

| Input | Default | Description |
|-------|---------|-------------|
| `paths` | *(auto)* | Newline-separated files to scan. When empty, scans `demo/fixture.json` and `status.json` if present. |
| `banned-phrases` | `guaranteed,profit,alpha` | Comma-separated banned phrases (case-insensitive). |
| `python-version` | `3.11` | Python runtime for the checker. |

## Behavior

- JSON files: every string value in the document is checked.
- Plain-text files: each non-empty line is checked.
- Fails the job when any string contains a banned phrase.
