# glance-35.elghaly.dev — retired

This subdomain is **retired**. Preferred outcomes:

| State | How |
|-------|-----|
| **Down (recommended)** | Remove the `glance-35.elghaly.dev` DNS record at your registrar. Confirmed: no public DNS A/CNAME records (NXDOMAIN). |
| **Redirect** | Deploy this folder as a separate GitHub Pages site with `CNAME` = `glance-35.elghaly.dev`, DNS CNAME → `alarm2024.github.io`. |
| **Same build** | Add `glance-35.elghaly.dev` as a second custom domain on the main `glance` repo Pages settings; `index.html` already redirects that hostname to `glance.elghaly.dev`. |

## Verify retirement

```bash
# Expect: no DNS answer
dig +short glance-35.elghaly.dev

# Expect: connection/DNS failure (not the old site)
curl -sSIL https://glance-35.elghaly.dev/

# If DNS still points at GitHub Pages without a registered domain, expect HTTP 404
curl -sI --resolve "glance-35.elghaly.dev:443:185.199.108.153" https://glance-35.elghaly.dev/
```

The old "35 GLANCE" landing is not served from this repository's Pages deployment.
