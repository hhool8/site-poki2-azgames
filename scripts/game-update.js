'use strict';

/**
 * game-update.js  — update fields on an existing game entry in src/data/games.json
 *
 * Usage:
 *   node scripts/game-update.js --slug=snake --title="Super Snake"
 *   node scripts/game-update.js --slug=snake --description="New desc" --category=casual-games
 *   node scripts/game-update.js --slug=snake --hidden=false   # un-hide a soft-deleted game
 *
 * Updatable fields: title, description, thumbnail, category, hidden
 */

const fs   = require('fs');
const path = require('path');

const ROOT      = path.join(__dirname, '..');
const JSON_FILE = path.join(ROOT, 'src/data/games.json');

const UPDATABLE = ['title', 'description', 'thumbnail', 'category', 'hidden'];

const args = parseArgs(process.argv.slice(2));

if (!args.slug) {
  console.error('[game:update] Missing required argument: --slug');
  console.error(`Usage: node scripts/game-update.js --slug=<slug> [--${UPDATABLE.join('] [--')}]`);
  process.exit(1);
}

const { slug, ...rest } = args;
const updates = Object.fromEntries(
  Object.entries(rest).filter(([k]) => UPDATABLE.includes(k))
);

if (Object.keys(updates).length === 0) {
  console.error(`[game:update] No updatable fields provided. Updatable: ${UPDATABLE.join(', ')}`);
  process.exit(1);
}

const data = JSON.parse(fs.readFileSync(JSON_FILE, 'utf8'));

const game = data.games.find(g => g.slug === slug);
if (!game) {
  console.error(`[game:update] Slug "${slug}" not found in games.json`);
  process.exit(1);
}

// Validate category if being updated
if (updates.category) {
  const validCategories = data.categories.map(c => c.slug);
  if (!validCategories.includes(updates.category)) {
    console.error(`[game:update] Unknown category "${updates.category}". Valid:\n  ${validCategories.join('\n  ')}`);
    process.exit(1);
  }
}

// Coerce boolean strings
if ('hidden' in updates) {
  updates.hidden = updates.hidden === 'false' ? false : Boolean(updates.hidden);
}

Object.assign(game, updates);
fs.writeFileSync(JSON_FILE, JSON.stringify(data, null, 2) + '\n', 'utf8');

console.log(`[game:update] Updated "${slug}":`);
for (const [k, v] of Object.entries(updates)) {
  console.log(`  ${k} = ${JSON.stringify(v)}`);
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
