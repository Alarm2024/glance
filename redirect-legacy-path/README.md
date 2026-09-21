# Legacy subdomain redirect

Pure HTTP redirect to [glance.elghaly.dev](https://glance.elghaly.dev/). No app content, no bot internals.

Deploy this folder as a **separate** GitHub Pages site when a legacy hostname still resolves in DNS:

1. Copy `index.html`, `CNAME`, and `.nojekyll` to the redirect repo root.
2. Enable GitHub Pages on that repo.
3. Point the legacy hostname CNAME at `alarm2024.github.io`.

The main site also redirects known legacy hostnames in `index.html` when they share one Pages deployment.

## Verify

```bash
curl -sSIL https://glance-35.elghaly.dev/   # expect redirect or DNS failure — not the old landing
curl -s https://glance.elghaly.dev/ | head -5
```
