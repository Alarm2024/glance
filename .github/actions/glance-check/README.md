# glance-check

Composite GitHub Action that runs `assert_no_overclaim()` against status strings in your repository.

## Usage

Runnable as-is in a clone of this repo (`demo/fixture.json` ships with it):

```yaml
- uses: Alarm2024/glance/.github/actions/glance-check@main
  with:
    paths: |
      demo/fixture.json
    banned-phrases: guaranteed,profit,alpha
```

### Caller-created paths

`status.json` is not in this repo. List it when an earlier step in your job writes it; a listed path that does not exist fails the job with `requested path does not exist: status.json`.

```yaml
- run: ./your-bot --dump-status > status.json   # your step creates the file
- uses: Alarm2024/glance/.github/actions/glance-check@main
  with:
    paths: |
      status.json
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
- Fails the job when a path listed in `paths` is not a file. An empty `paths` input still skips default candidates that are absent.
