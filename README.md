# AZ Games — azgames.poki2.online

Free online games hub powered by [azgames.io](https://azgames.io), deployed as a static site on Cloudflare Pages.

## Features

- 300+ browser games across 10 categories (Clicker, IO, Adventure, 2 Player, Shooting, Sports, Car, Puzzle, Casual, Kids)
- Game metadata scraped from azgames.io (title, description, thumbnail, category)
- Static HTML build — no server required
- SEO-ready: canonical URLs, Open Graph, JSON-LD schema, sitemap
- Configurable domain via `SITE_DOMAIN` env var

## Project Structure

```
azgames-embed-urls.txt   # 300 game slugs (source of truth)
css/style.css            # Orange dark-theme stylesheet
public/                  # CNAME, _headers, robots.txt, favicon.svg
src/
  templates/             # base.html, play.html, category.html
  data/seo.json          # Static page metadata
  data/games.json        # Scraped game data (auto-generated, not committed)
  content/               # index, about, privacy, terms, contact HTML fragments
scripts/
  scrape-games.js        # Fetch metadata for all 300 games from azgames.io
  config.js              # Shared config + env-var overrides
  build-pages.js         # Build static pages (index, about, …)
  build-games.js         # Build play/ and category/ pages
  build-sitemap.js       # Build sitemap.xml
dist/                    # Build output (git-ignored)
```

## Setup

```bash
# Install dependencies (only wrangler needed)
npm install

# Scrape game metadata from azgames.io → src/data/games.json
npm run scrape

# Build static site → dist/
npm run build

# Local preview (default domain)
python3 -m http.server 3457 --directory dist

# Local preview with localhost canonical URLs
SITE_DOMAIN=http://localhost:3457 npm run build
python3 -m http.server 3457 --directory dist
```

## Deploy

```bash
# Deploy to Cloudflare Pages
npm run deploy
```

## Configuration

| Env Var | Description | Default |
|---|---|---|
| `SITE_DOMAIN` | Override canonical domain | `https://azgames.poki2.online` |
| `RESOURCE_SITE` | Override game embed base URL | `https://azgames.io` |

## Game Embed Pattern

Games are embedded as iframes using the azgames.io embed URL pattern:

```
https://azgames.io/{slug}.embed
```

## License

Site code © 2026 AZ Games. Game content belongs to their respective owners.
