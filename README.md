# H5Games Template — AZ Games Edition

A reusable static HTML games-collection template. Clone it, point it at any domain, and deploy to Cloudflare Pages or GitHub Pages in minutes.

> **Default site:** azgames.poki2.online — 300+ free browser games powered by [azgames.io](https://azgames.io)

---

## Quickstart — embed a game in 3 steps

```bash
# 1. Install deps
npm install

# 2. Add a game (slug must match azgames.io embed URL)
npm run game:add -- --slug=snake --title="Snake Game" \
  --description="Classic snake game" \
  --category=casual-games \
  --thumbnail=/images/games/snake.png

# 3. Build and preview locally
SITE_DOMAIN=http://localhost:3457 npm run build
python3 -m http.server 3457 --directory dist
# open http://localhost:3457/play/snake
```

---

## npm Command Reference

| Command | Description |
|---------|-------------|
| `npm run game:add -- --slug=... --title=... --description=... --category=... --thumbnail=...` | Add a game. Append `--validate` to HEAD-check the embed URL first. |
| `npm run game:remove -- --slug=snake` | Physically delete a game entry. |
| `npm run game:remove -- --slug=snake --soft` | Soft-delete (sets `hidden:true`, game stays in JSON). |
| `npm run game:update -- --slug=snake --title="New Title"` | Update any field: `title`, `description`, `thumbnail`, `category`, `hidden`. |
| `npm run validate` | HEAD-check all embed URLs. Reports invalid slugs. Append `--patch` to auto-mark them `deprecated:true`. |
| `npm run scrape` | Scrape metadata for all slugs in `azgames-embed-urls.txt` → `src/data/games.json`. |
| `npm run build` | Build full static site → `dist/`. |
| `npm run deploy` | Deploy `dist/` to Cloudflare Pages (uses `$PROJECT_NAME` env var). |
| `npm run site:init -- --domain=... --project-name=...` | Initialize for a new domain (see Domain Migration below). |
| `npm run clean` | Delete `dist/`. |

---

## Project Structure

```
azgames-embed-urls.txt   # Source-of-truth slug list for scraping
css/style.css            # Orange dark-theme stylesheet
public/
  CNAME                  # Custom domain (updated by site:init)
  _headers               # Cloudflare Pages response headers
  robots.txt
  favicon.svg
src/
  templates/             # base.html, play.html, category.html
  data/
    seo.json             # Static page metadata (title, og, canonical, …)
    games.json           # Game catalog — edit directly or via game:* scripts
  content/               # index, about, privacy, terms, contact HTML fragments
scripts/
  config.js              # Shared config: reads seo.json + games.json, applies env-var overrides
  scrape-games.js        # Populate games.json from azgames.io
  build-pages.js         # Build static pages (index, about, …)
  build-games.js         # Build play/ and category/ pages
  build-sitemap.js       # Build sitemap.xml
  build-blog.js          # Build blog pages
  build-search.js        # Build search index
  validate-embeds.js     # HEAD-check all embed URLs
  game-add.js            # CLI: add a game
  game-remove.js         # CLI: remove a game
  game-update.js         # CLI: update a game
  init-site.js           # CLI: initialize for a new domain
dist/                    # Build output (git-ignored)
.github/workflows/
  cloudflare-deploy.yml  # Cloudflare Pages CI (primary)
  deploy.yml             # GitHub Pages CI (fallback)
```

---

## Deploy to Cloudflare Pages

### Manual

```bash
# Set project name (default: azgames-poki2-site)
PROJECT_NAME=my-cf-project npm run deploy
```

### CI (GitHub Actions) — primary

1. Create a Cloudflare API token with **Cloudflare Pages: Edit** permission.
2. In your GitHub repo → **Settings → Secrets → Actions**, add:
   - `CF_API_TOKEN` — your Cloudflare API token
   - `CF_ACCOUNT_ID` — your Cloudflare account ID
3. In **Settings → Variables → Actions**, add:
   - `SITE_DOMAIN` — e.g. `https://mygames.example.com`
   - `CF_PROJECT_NAME` — e.g. `my-cf-project`
   - `RESOURCE_SITE` — (optional) default `https://azgames.io`
4. Push to `main` — `.github/workflows/cloudflare-deploy.yml` runs automatically.

---

## Deploy to GitHub Pages (fallback)

1. In **Settings → Variables → Actions**, add:
   - `SITE_DOMAIN` — e.g. `https://yourname.github.io/repo`
2. Enable GitHub Pages in repo settings (source: **GitHub Actions**).
3. Push to `main` — `.github/workflows/deploy.yml` runs automatically.

---

## Domain Migration (Multi-site)

To launch a second site from the same codebase:

```bash
# 1. Clone the repo
git clone <this-repo> mynewsite && cd mynewsite

# 2. Install deps
npm install

# 3. Initialize for the new domain (updates seo.json, games.json, CNAME, wrangler.pages.toml)
npm run site:init -- \
  --domain=https://mygames.example.com \
  --project-name=mygames-cf \
  --site-name="My Games"

# 4. Set GitHub secrets + variables (see CI section above), then push
git add -A && git commit -m "init: mygames.example.com" && git push
```

The script prints DNS setup instructions. Summary:

| Provider | Record type | Name | Value |
|----------|-------------|------|-------|
| Cloudflare Pages | CNAME | `mygames.example.com` | `mygames-cf.pages.dev` |
| GitHub Pages | CNAME | `mygames.example.com` | `<user>.github.io` |

Then add the custom domain in **Cloudflare Pages → Project → Custom domains** — TLS is provisioned automatically.

---

## Env Var Reference

| Var | Description | Default |
|-----|-------------|---------|
| `SITE_DOMAIN` | Canonical domain used in all URLs | value in `seo.json` |
| `RESOURCE_SITE` | Embed iframe base URL | value in `games.json` |
| `PROJECT_NAME` | Cloudflare Pages project name for `npm run deploy` | `azgames-poki2-site` |

## Game Embed Pattern

```
https://azgames.io/{slug}.embed
```

Override per-build with `RESOURCE_SITE=https://other-source.io npm run build`.

---

## License

Site code © 2026 AZ Games. Game content belongs to their respective owners.
