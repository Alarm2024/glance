# glance-35.elghaly.dev redirect

Retire the old subdomain by deploying this folder as a **separate** GitHub Pages site:

1. Create a private repo (e.g. `glance-35-redirect`) or enable Pages on a orphan branch.
2. Copy `index.html`, `CNAME`, and `.nojekyll` to the repo root.
3. Enable GitHub Pages (Actions or branch deploy).
4. In DNS, point `glance-35.elghaly.dev` CNAME to `YOUR_USER.github.io`.

The main `glance` site also includes a hostname redirect in `index.html` when both domains share one deployment.
