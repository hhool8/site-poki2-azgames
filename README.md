# AZ Games — azgames.poki2.online

Static rebuild of the AZ Games subdomain, generated from the game catalogue the
previous build of this domain already published.

Live: <https://azgames.poki2.online/>

## What this replaces

The folder used to hold an unused Node proxy prototype (`server/proxy-azgames.js`,
one placeholder entry in `proxies.json`, a `list.html` debug page). None of that
ever produced the live site. It is kept under `legacy/` for reference and is not
part of the build.

The live site it replaces had 291 game pages, an **empty `sitemap.xml`**
(`<urlset>` with no `<loc>`), an `ads.txt` that returned the homepage with a 200
status, no ads, and three FAQ answers per game that were identical across the
whole catalogue apart from the game name.

## Design

The stylesheet is `poki2.online`'s, unchanged — same CSS variables
(`--bg: #0b0b18`, `--primary: #22d3ee`, `--accent: #a855f7`), same
`.featured-card` / `.site-card` / `.hero` / `.section-title` components, same nav
and footer markup. `src/styles/extra.css` only adds what this site needs and the
main site does not have: a game player, a metadata bar, pagination, the search
box, and a mobile header fix (the shared nav keeps a 170–220px search field at
every width, which squeezes the logo into the hamburger at 390px).

Fonts, colours and spacing therefore match the main portal; only the copy and
the catalogue differ.

## Build

```bash
python3 tools/extract_azgames.py --workers 10   # data/catalog.json  (~25 s)
python3 tools/fetch_images.py --workers 14      # data/img/*.webp    (291 imgs, 5 MB)
python3 tools/build_site.py                     # dist/              (~2 s)
```

Output: **316 pages, 291 images, 9.5 MB**.

| path | pages |
|---|---|
| `/` | home |
| `/play/<slug>/` | 291 game pages |
| `/category/<slug>/` | 10 categories, unpaginated |
| `/games/` + `/games/page/N/` | full catalogue, 48 per page |
| `/search/` | client-side filter over `search-index.json` |
| `/about`, `/contact`, `/privacy`, `/terms`, `/dmca` | static (written as `.html`; Pages maps `/about` → `/about.html`) |

## Data

Game data is crawled from the domain's own previous build
(`azgames.poki2.online/play/<slug>`): title, cover image, one-line description,
category membership, and the embed URL (`https://azgames.io/<slug>.embed`).
Category membership comes from the category pages themselves, so the shelves
match what visitors already had bookmarked.

`azgames.io` serves its `.embed` documents with **no `X-Frame-Options` and no
CSP**, so the games frame correctly — unlike `static.hahagames.com`, which
returns 403 + `X-Frame-Options: SAMEORIGIN` and had to be dropped from an
earlier network build.

## Player

Click to play. The iframe is created on click, not on load: 291 game pages each
pulling a third-party embed (and whatever ad stack it brings) before the visitor
asks for it is a cost with no benefit. `<noscript>` and the play button's
`data-src` both keep the game reachable without JS.

## Ads

`src/config.json` → `ads`. AdSense client `ca-pub-5676206764686662` (the same
account as `poki2.online` and `play.poki2.online`), Auto ads only, plus a
generated `ads.txt`.

Three manual slot keys exist (`homeMid`, `gameUnderPlayer`, `listInline`) but
default to empty — an empty slot reserves no space and fires an unfilled request,
which is worse than shipping no unit. Fill a key with a real `data-ad-slot` id
and rebuild to pin a unit to a position.

## Deploy

This machine is logged into more than one Cloudflare account, so the account
must be explicit or `wrangler` aborts in non-interactive mode:

```bash
export CLOUDFLARE_ACCOUNT_ID=$(cat ~/.poki2-cf-account)
wrangler pages deploy dist --project-name azgames-poki2-site --branch main
```

`azgames.poki2.online` is already attached to that project — no domain or DNS
step is needed for a redeploy.

## Known gaps

1. **Copy is thin.** Every game description comes from one sentence in the
   previous build. Pages are structurally complete (breadcrumb, metadata,
   player, FAQ, related games) but 291 one-sentence intros will not rank on their
   own; this needs an editorial pass before it is treated as a content site
   rather than a directory.
2. **Games are third-party embeds.** Nothing is hosted here. If `azgames.io`
   changes its framing policy or removes a game, the page still loads and the
   frame goes blank; `_headers` cannot help, the check happens upstream.
3. **No blog.** The previous build's `/blog.html` returned a 308 to a page that
   did not exist; those paths now 301 to `/games/`.

## CI

`.github/workflows/build.yml` runs two jobs:

- **build** — every push, every pull request, and manual dispatch. Runs
  `check_gate_single_source.py`, `build_site.py` and `check_lastmod_truthful.py`,
  then uploads `dist/` as a 7-day artifact. Never touches a secret.
- **deploy** — only on a push to `main` in this repository itself. Rebuilds,
  re-runs both gates, then ships `dist/` via `wrangler-action` with the commit
  hash and message recorded on the Pages deployment, so "did this commit go
  live?" is answerable afterwards.

Delivery is therefore push-to-`main`, not a manual `wrangler pages deploy`. The
local command still works and is the fallback when Actions is unavailable.

### Credentials

The deploy job needs the repository secrets `CLOUDFLARE_ACCOUNT_ID` and
`CLOUDFLARE_API_TOKEN` (the same credentials the local direct-upload path uses).
This repository is **public**, so the token lives only in Actions secrets and is
never written into a tracked file. Two things keep it from leaking to code the
maintainers did not write: GitHub withholds secrets from fork pull requests, and
the deploy job is additionally gated on `event_name == push`,
`ref == refs/heads/main`, and `github.repository == hhool8/site-poki2-azgames`.
Do not add `pull_request_target` to this workflow — that trigger does expose
secrets to fork code and would undo both protections.

Note that the Pages project is a **Direct Upload** project (`source: null`), not
a Git-integrated one. CI deploys into it by API; Cloudflare does not build this
repository itself. Migrating the project to Git integration is a separate,
one-way move that needs the Cloudflare GitHub App authorised for this repo.
