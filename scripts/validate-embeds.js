'use strict';

/**
 * validate-embeds.js
 * Reads azgames-embed-urls.txt, skips non-game pages, then HEAD-checks
 * each embed URL against azgames.io.  Reports valid / invalid slugs and
 * optionally marks invalid entries as deprecated:true in src/data/games.json.
 *
 * Usage:
 *   node scripts/validate-embeds.js           # dry-run report
 *   node scripts/validate-embeds.js --patch   # also patches games.json
 */

const fs      = require('fs');
const path    = require('path');
const https   = require('https');
const { URL } = require('url');

// ── Non-game page slugs to skip ──────────────────────────────────────────────
const SKIP_SLUGS = new Set([
  'contact-us',
  'copyright-infringement-notice-procedure',
  'privacy-policy',
  'term-of-use',
  'popular-games',
  'new-games',
  'hot-games',
  'trending-games',
]);

const ROOT      = path.join(__dirname, '..');
const TXT_FILE  = path.join(ROOT, 'azgames-embed-urls.txt');
const JSON_FILE = path.join(ROOT, 'src/data/games.json');
const PATCH     = process.argv.includes('--patch');
const CONCURRENCY = 10;  // simultaneous requests
const TIMEOUT_MS  = 12000;

// ── Read & filter URL list ───────────────────────────────────────────────────
const rawLines = fs.readFileSync(TXT_FILE, 'utf8')
  .split('\n')
  .map(l => l.trim())
  .filter(Boolean);

const entries = rawLines.map(url => {
  const slug = new URL(url).pathname.replace(/^\//, '').replace(/\.embed$/, '');
  return { url, slug };
}).filter(({ slug }) => !SKIP_SLUGS.has(slug));

console.log(`Checking ${entries.length} embed URLs (${CONCURRENCY} concurrent)…\n`);

// ── HEAD request helper ──────────────────────────────────────────────────────
function headRequest({ url, slug }) {
  return new Promise(resolve => {
    const req = https.request(url, { method: 'HEAD', timeout: TIMEOUT_MS }, res => {
      const status = res.statusCode;
      resolve({ slug, url, status, ok: status >= 200 && status < 400 });
    });
    req.on('timeout', () => { req.destroy(); resolve({ slug, url, status: 'TIMEOUT', ok: false }); });
    req.on('error',   () =>                  resolve({ slug, url, status: 'ERROR',   ok: false }));
    req.end();
  });
}

// ── Concurrent pool ──────────────────────────────────────────────────────────
async function runPool(items, concurrency, fn) {
  const results = [];
  let idx = 0;
  async function worker() {
    while (idx < items.length) {
      const item = items[idx++];
      results.push(await fn(item));
    }
  }
  await Promise.all(Array.from({ length: concurrency }, worker));
  return results;
}

(async () => {
  const results = await runPool(entries, CONCURRENCY, headRequest);

  const valid   = results.filter(r => r.ok);
  const invalid = results.filter(r => !r.ok);

  console.log('=== VALID (' + valid.length + ') ===');
  valid.forEach(r => console.log(`  ✓ ${r.slug}  [${r.status}]`));

  console.log('\n=== INVALID / UNREACHABLE (' + invalid.length + ') ===');
  if (invalid.length === 0) {
    console.log('  (none)');
  } else {
    invalid.forEach(r => console.log(`  ✗ ${r.slug}  [${r.status}]`));
  }

  console.log(`\nSummary: ${valid.length} valid, ${invalid.length} invalid out of ${entries.length} checked.`);

  // ── Optional: patch games.json ────────────────────────────────────────────
  if (PATCH && invalid.length > 0) {
    const gamesData = JSON.parse(fs.readFileSync(JSON_FILE, 'utf8'));
    const invalidSet = new Set(invalid.map(r => r.slug));
    let patched = 0;
    for (const game of gamesData.games) {
      if (invalidSet.has(game.slug)) {
        game.deprecated = true;
        patched++;
      }
    }
    fs.writeFileSync(JSON_FILE, JSON.stringify(gamesData, null, 2) + '\n', 'utf8');
    console.log(`\nPatched ${patched} games as deprecated:true in src/data/games.json`);
  } else if (PATCH) {
    console.log('\nNo invalid games — games.json unchanged.');
  }
})();
