'use strict';

/**
 * init-site.js  — initialize this template for a new site / domain
 *
 * Updates:
 *   - src/data/seo.json  (site.domain + all canonical / og / twitter URLs)
 *   - src/data/games.json (site.domain, site.name)
 *   - public/CNAME
 *   - wrangler.pages.toml  (project name)
 *
 * Usage:
 *   node scripts/init-site.js \
 *     --domain=https://mygames.example.com \
 *     --project-name=mygames-cf \
 *     [--site-name="My Games"]           # optional display name
 *     [--resource-site=https://azgames.io]  # optional, default kept if omitted
 *
 * Run once after cloning. Re-run to migrate to a different domain.
 */

const fs   = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');

// ── Parse args ────────────────────────────────────────────────────────────────
const args = parseArgs(process.argv.slice(2));

const newDomain      = (args.domain || '').replace(/\/$/, '');
const projectName    = args['project-name'] || args['projectName'] || '';
const newSiteName    = args['site-name'] || args['siteName'] || '';
const newResourceSite = (args['resource-site'] || args['resourceSite'] || '').replace(/\/$/, '');

if (!newDomain || !projectName) {
  console.error('[site:init] Missing required arguments: --domain and --project-name');
  console.error('Usage: node scripts/init-site.js --domain=https://example.com --project-name=my-cf-project [--site-name="My Games"] [--resource-site=https://azgames.io]');
  process.exit(1);
}

// Basic URL validation
try { new URL(newDomain); } catch {
  console.error(`[site:init] Invalid --domain value: "${newDomain}". Provide a full URL like https://mygames.example.com`);
  process.exit(1);
}

// ── seo.json ──────────────────────────────────────────────────────────────────
const seoPath = path.join(ROOT, 'src/data/seo.json');
const seo     = JSON.parse(fs.readFileSync(seoPath, 'utf8'));

const oldDomain = seo.site.domain.replace(/\/$/, '');

function replaceDomain(str) {
  if (typeof str !== 'string') return str;
  return str.replaceAll(oldDomain, newDomain);
}

seo.site.domain    = newDomain;
seo.site.faviconUrl = newDomain + '/favicon.svg';
if (newSiteName) {
  seo.site.name      = newSiteName;
  seo.site.shortName = newSiteName;
}

for (const page of seo.pages) {
  if (page.canonical)                    page.canonical             = replaceDomain(page.canonical);
  if (page.og) {
    if (page.og.url)                     page.og.url                = replaceDomain(page.og.url);
    if (page.og.image)                   page.og.image              = replaceDomain(page.og.image);
    if (page.og.title && newSiteName)    page.og.title              = page.og.title.replace(seo.site.name, newSiteName);
  }
  if (page.twitter) {
    if (page.twitter.image)              page.twitter.image         = replaceDomain(page.twitter.image);
  }
}

fs.writeFileSync(seoPath, JSON.stringify(seo, null, 2) + '\n', 'utf8');
console.log(`[site:init] seo.json updated (${oldDomain} → ${newDomain})`);

// ── games.json ────────────────────────────────────────────────────────────────
const gamesPath = path.join(ROOT, 'src/data/games.json');
const games     = JSON.parse(fs.readFileSync(gamesPath, 'utf8'));

games.site.domain = newDomain;
if (newSiteName)       games.site.name = newSiteName;
if (newResourceSite)   games.site.resourceSite = newResourceSite;

fs.writeFileSync(gamesPath, JSON.stringify(games, null, 2) + '\n', 'utf8');
console.log(`[site:init] games.json updated`);

// ── public/CNAME ──────────────────────────────────────────────────────────────
const cnamePath  = path.join(ROOT, 'public/CNAME');
const hostname   = new URL(newDomain).hostname;
fs.writeFileSync(cnamePath, hostname + '\n', 'utf8');
console.log(`[site:init] public/CNAME → ${hostname}`);

// ── wrangler.pages.toml ───────────────────────────────────────────────────────
const wranglerPath = path.join(ROOT, 'wrangler.pages.toml');
let wrangler = fs.readFileSync(wranglerPath, 'utf8');
wrangler = wrangler.replace(/^name\s*=\s*.+$/m, `name = "${projectName}"`);
fs.writeFileSync(wranglerPath, wrangler, 'utf8');
console.log(`[site:init] wrangler.pages.toml → name = "${projectName}"`);

// ── DNS guidance ─────────────────────────────────────────────────────────────
console.log(`
─────────────────────────────────────────────────
  Site initialized: ${newDomain}
  Cloudflare project: ${projectName}
─────────────────────────────────────────────────

Next steps:

1. Set GitHub repo variables (Settings → Variables → Actions):
     SITE_DOMAIN    = ${newDomain}
     CF_PROJECT_NAME = ${projectName}

2. Set GitHub repo secrets (Settings → Secrets → Actions):
     CF_API_TOKEN   = <your Cloudflare API token>
     CF_ACCOUNT_ID  = <your Cloudflare account ID>

3. DNS (for custom domain on Cloudflare Pages):
   Add a CNAME record in your DNS provider:
     ${hostname}  →  ${projectName}.pages.dev

   Then in Cloudflare Pages dashboard:
     Project → Custom domains → Add "${hostname}"
     Cloudflare will provision TLS automatically.

4. DNS (for GitHub Pages fallback):
   Add a CNAME record:
     ${hostname}  →  <your-github-username>.github.io

5. Push to main to trigger CI deploy.
─────────────────────────────────────────────────
`);

// ── Helpers ───────────────────────────────────────────────────────────────────
function parseArgs(argv) {
  const result = {};
  for (const arg of argv) {
    const m = arg.match(/^--([^=]+)(?:=(.*))?$/s);
    if (m) result[m[1]] = m[2] !== undefined ? m[2] : true;
  }
  return result;
}
