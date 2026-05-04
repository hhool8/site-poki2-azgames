'use strict';

/**
 * game-add.js  — add a new game entry to src/data/games.json
 *
 * Usage:
 *   node scripts/game-add.js \
 *     --slug=snake \
 *     --title="Snake Game" \
 *     --description="Classic snake game" \
 *     --category=casual-games \
 *     --thumbnail=/images/games/snake.png \
 *     [--validate]   # HEAD-check the embed URL before saving
 */

'use strict';

const fs    = require('fs');
const path  = require('path');
const https = require('https');
const { URL } = require('url');

const ROOT      = path.join(__dirname, '..');
const JSON_FILE = path.join(ROOT, 'src/data/games.json');

// ── Parse args ───────────────────────────────────────────────────────────────
const args = parseArgs(process.argv.slice(2));
const REQUIRED = ['slug', 'title', 'description', 'category', 'thumbnail'];

for (const key of REQUIRED) {
  if (!args[key]) {
    console.error(`[game:add] Missing required argument: --${key}`);
    console.error(`Usage: node scripts/game-add.js --slug=<slug> --title=<title> --description=<desc> --category=<cat> --thumbnail=<url>`);
    process.exit(1);
  }
}

const { slug, title, description, category, thumbnail } = args;
const doValidate = 'validate' in args;

// ── Load data ────────────────────────────────────────────────────────────────
const data = JSON.parse(fs.readFileSync(JSON_FILE, 'utf8'));

if (data.games.find(g => g.slug === slug)) {
  console.error(`[game:add] Slug "${slug}" already exists in games.json. Use game:update to modify it.`);
  process.exit(1);
}

const validCategories = data.categories.map(c => c.slug);
if (!validCategories.includes(category)) {
  console.error(`[game:add] Unknown category "${category}". Valid categories:\n  ${validCategories.join('\n  ')}`);
  process.exit(1);
}

// ── Optional embed validation ─────────────────────────────────────────────────
function checkEmbed(resourceSite, gameSlug) {
  return new Promise((resolve) => {
    const embedUrl = `${resourceSite}/${gameSlug}.embed`;
    let parsed;
    try { parsed = new URL(embedUrl); } catch { return resolve({ ok: false, status: 0, url: embedUrl }); }
    const options = {
      method: 'HEAD',
      hostname: parsed.hostname,
      path: parsed.pathname,
      timeout: 10000,
      headers: { 'User-Agent': 'h5games-template/1.0' },
    };
    const req = https.request(options, res => {
      resolve({ ok: res.statusCode < 400, status: res.statusCode, url: embedUrl });
    });
    req.on('error', () => resolve({ ok: false, status: 0, url: embedUrl }));
    req.on('timeout', () => { req.destroy(); resolve({ ok: false, status: 408, url: embedUrl }); });
    req.end();
  });
}

async function main() {
  if (doValidate) {
    const resourceSite = data.site.resourceSite || 'https://azgames.io';
    process.stdout.write(`[game:add] Validating embed URL for "${slug}"… `);
    const result = await checkEmbed(resourceSite, slug);
    if (!result.ok) {
      console.log(`FAILED (HTTP ${result.status})`);
      console.error(`[game:add] Embed URL not reachable: ${result.url}`);
      console.error('[game:add] Use without --validate to add anyway, or check the slug.');
      process.exit(1);
    }
    console.log(`OK (HTTP ${result.status})`);
  }

  const newGame = { slug, title, description, thumbnail, category };
  data.games.push(newGame);

  fs.writeFileSync(JSON_FILE, JSON.stringify(data, null, 2) + '\n', 'utf8');
  console.log(`[game:add] Added "${title}" (${slug}) to category "${category}"`);
  console.log(`[game:add] Total visible games: ${data.games.filter(g => !g.hidden).length}`);
}

main().catch(err => { console.error(err); process.exit(1); });

// ── Helpers ───────────────────────────────────────────────────────────────────
function parseArgs(argv) {
  const result = {};
  for (const arg of argv) {
    const m = arg.match(/^--([^=]+)(?:=(.*))?$/s);
    if (m) result[m[1]] = m[2] !== undefined ? m[2] : true;
  }
  return result;
}
