'use strict';

/**
 * game-remove.js  — remove game entries from src/data/games.json
 *
 * Usage:
 *   node scripts/game-remove.js --slug=snake
 *   node scripts/game-remove.js --slug=snake,tetris,pacman
 *   node scripts/game-remove.js --slug=snake --soft   # marks hidden:true instead of deleting
 */

const fs   = require('fs');
const path = require('path');

const ROOT      = path.join(__dirname, '..');
const JSON_FILE = path.join(ROOT, 'src/data/games.json');

const args = parseArgs(process.argv.slice(2));

if (!args.slug) {
  console.error('[game:remove] Missing required argument: --slug');
  console.error('Usage: node scripts/game-remove.js --slug=<slug>[,<slug>,...] [--soft]');
  process.exit(1);
}

const slugs   = args.slug.split(',').map(s => s.trim()).filter(Boolean);
const isSoft  = 'soft' in args;

const data = JSON.parse(fs.readFileSync(JSON_FILE, 'utf8'));

let removed = 0;
let notFound = [];

for (const slug of slugs) {
  const idx = data.games.findIndex(g => g.slug === slug);
  if (idx === -1) {
    notFound.push(slug);
    continue;
  }
  if (isSoft) {
    data.games[idx].hidden = true;
    console.log(`[game:remove] Soft-removed (hidden) "${slug}"`);
  } else {
    const title = data.games[idx].title;
    data.games.splice(idx, 1);
    console.log(`[game:remove] Deleted "${title}" (${slug})`);
  }
  removed++;
}

if (notFound.length) {
  console.warn(`[game:remove] Slugs not found: ${notFound.join(', ')}`);
}

if (removed > 0) {
  fs.writeFileSync(JSON_FILE, JSON.stringify(data, null, 2) + '\n', 'utf8');
  console.log(`[game:remove] Done. Total visible games: ${data.games.filter(g => !g.hidden).length}`);
} else {
  console.log('[game:remove] No changes made.');
  process.exit(notFound.length ? 1 : 0);
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function parseArgs(argv) {
  const result = {};
  for (const arg of argv) {
    const m = arg.match(/^--([^=]+)(?:=(.*))?$/s);
    if (m) result[m[1]] = m[2] !== undefined ? m[2] : true;
  }
  return result;
}
