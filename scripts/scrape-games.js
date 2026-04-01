'use strict';

/**
 * Scrape game data from azgames.io for all 300 games in azgames-embed-urls.txt
 * Writes src/data/games.json
 *
 * Usage:  node scripts/scrape-games.js
 */

const fs    = require('fs');
const path  = require('path');
const https = require('https');

const ROOT        = path.join(__dirname, '..');
const EMBED_FILE  = path.join(ROOT, 'azgames-embed-urls.txt');
const OUT_FILE    = path.join(ROOT, 'src/data/games.json');
const CONCURRENCY = 8;
const RETRY_MAX   = 2;
const TIMEOUT_MS  = 15000;

// ── Category metadata ────────────────────────────────────────────────────────
const CATEGORIES = [
  { slug: 'clicker-games',   name: 'Clicker Games',   emoji: '🖱️',  description: 'Satisfying incremental and idle clicker games. Click, tap, and automate your way to billions.' },
  { slug: 'io-games',        name: '.IO Games',        emoji: '🌐',  description: 'Lightweight browser multiplayer games. Compete against real players in real time — no login needed.' },
  { slug: 'adventure-games', name: 'Adventure Games',  emoji: '🗺️',  description: 'Explore worlds, defeat enemies, and solve puzzles in thrilling browser adventure games.' },
  { slug: '2-player-games',  name: '2 Player Games',   emoji: '👥',  description: 'Play head-to-head with a friend on the same device. Fighter, racing, and skill-based multiplayer.' },
  { slug: 'shooting-games',  name: 'Shooting Games',   emoji: '🎯',  description: 'First-person shooters, top-down blasters, and aim trainers. Lock and load.' },
  { slug: 'sports-games',    name: 'Sports Games',     emoji: '🏆',  description: 'Basketball, soccer, golf, and athletics — all playable in your browser for free.' },
  { slug: 'car-games',       name: 'Car Games',        emoji: '🚗',  description: 'Drift, race, and stunt your way through dozens of driving challenges in the browser.' },
  { slug: 'puzzle-games',    name: 'Puzzle Games',     emoji: '🧩',  description: 'Brain teasers, match-3, logic puzzles, and word games for every skill level.' },
  { slug: 'casual-games',    name: 'Casual Games',     emoji: '🎮',  description: 'Easy to pick up, hard to put down. Quick-session favourites for every mood.' },
  { slug: 'kids-games',      name: 'Kids Games',       emoji: '🧒',  description: 'Age-appropriate fun for younger players — coloring, matching, and friendly platformers.' }
];
const VALID_CAT_SLUGS = new Set(CATEGORIES.map(c => c.slug));
const DEFAULT_CAT     = 'casual-games'; // fallback

// ── Read embed URLs and extract slugs ────────────────────────────────────────
const lines  = fs.readFileSync(EMBED_FILE, 'utf8').trim().split('\n');
const slugs  = lines
  .map(l => l.trim())
  .filter(Boolean)
  .map(url => url.replace(/^https?:\/\/azgames\.io\//, '').replace(/\.embed$/, ''));

console.log(`Scraping ${slugs.length} games…`);

// ── HTTP helper ───────────────────────────────────────────────────────────────
function fetchPage(url) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; AZGamesScraper/1.0)',
        'Accept': 'text/html'
      },
      timeout: TIMEOUT_MS
    }, (res) => {
      // Follow up to 2 redirects
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        res.resume();
        return fetchPage(res.headers.location).then(resolve).catch(reject);
      }
      if (res.statusCode !== 200) {
        res.resume();
        return reject(new Error(`HTTP ${res.statusCode} for ${url}`));
      }
      const chunks = [];
      res.on('data', c => chunks.push(c));
      res.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
      res.on('error', reject);
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error(`Timeout: ${url}`)); });
  });
}

// ── Parse a game page ─────────────────────────────────────────────────────────
function parsePage(html, slug) {
  // Title: from <title> tag, strip " - Play ... on A-Z Games" / " - A-Z Games"
  const titleTagM = html.match(/<title>([^<]+)<\/title>/i);
  let title = slug.split('-').map(w => w[0].toUpperCase() + w.slice(1)).join(' '); // slug fallback
  if (titleTagM) {
    title = titleTagM[1]
      .replace(/\s*-\s*Play\s+.+$/i, '')
      .replace(/\s*-\s*A-Z Games$/i, '')
      .replace(/\s*\|\s*.+$/, '')
      .trim() || title;
  }

  // Description
  const descM = html.match(/<meta\s+name=["']description["']\s+content=["']([^"']+)/i);
  const description = descM ? descM[1].trim() : `Play ${title} free online.`;

  // Thumbnail: og:image (may be relative)
  const imgM = html.match(/property=["']og:image["'][^>]+content=["']([^"']+)/i)
             || html.match(/content=["']([^"']+)["'][^>]*property=["']og:image["']/i)
             || html.match(/name=["']twitter:image["'][^>]+content=["']([^"']+)/i);
  let thumbnail = '';
  if (imgM) {
    thumbnail = imgM[1].trim();
    if (thumbnail.startsWith('/')) thumbnail = 'https://azgames.io' + thumbnail;
  }
  if (!thumbnail) thumbnail = `https://azgames.io/upload/imgs/${slug.replace(/-/g,'')}.png`;

  // Category: collect ALL candidate slugs from breadcrumb + us-sticker elements,
  // then pick by priority (rarest/most specific category first).
  // Nav lists all 10 categories first — must collect only content-area tags.
  const CAT_PRIORITY = [
    'io-games', '2-player-games', 'shooting-games', 'car-games',
    'sports-games', 'clicker-games', 'puzzle-games', 'kids-games',
    'adventure-games', 'casual-games'
  ];

  const catCandidates = new Set();

  // Breadcrumb: <... class="bread-crumb-item..." href="/category/X" ...>
  // Attribute order may vary — match both orders
  const breadRe1 = /class="bread-crumb-item[^"]*"[^>]*href="\/category\/([a-z0-9-]+)"/gi;
  const breadRe2 = /href="\/category\/([a-z0-9-]+)"[^>]*class="bread-crumb-item[^"]*"/gi;
  let m;
  while ((m = breadRe1.exec(html)) !== null) {
    if (VALID_CAT_SLUGS.has(m[1])) catCandidates.add(m[1]);
  }
  while ((m = breadRe2.exec(html)) !== null) {
    if (VALID_CAT_SLUGS.has(m[1])) catCandidates.add(m[1]);
  }

  // US-sticker: <a class="us-sticker..." href="/category/X"> — attribute order may vary
  const stickerRe1 = /class="us-sticker[^"]*"[^>]*href="\/category\/([a-z0-9-]+)"/gi;
  const stickerRe2 = /href="\/category\/([a-z0-9-]+)"[^>]*class="us-sticker[^"]*"/gi;
  while ((m = stickerRe1.exec(html)) !== null) {
    if (VALID_CAT_SLUGS.has(m[1])) catCandidates.add(m[1]);
  }
  while ((m = stickerRe2.exec(html)) !== null) {
    if (VALID_CAT_SLUGS.has(m[1])) catCandidates.add(m[1]);
  }

  // Pick highest-priority (rarest) category
  let category = DEFAULT_CAT;
  for (const catSlug of CAT_PRIORITY) {
    if (catCandidates.has(catSlug)) {
      category = catSlug;
      break;
    }
  }

  return { slug, title, description, thumbnail, category };
}

// ── Scrape one slug with retries ──────────────────────────────────────────────
async function scrapeSlug(slug) {
  const url = `https://azgames.io/${slug}`;
  let lastErr;
  for (let attempt = 0; attempt <= RETRY_MAX; attempt++) {
    try {
      const html = await fetchPage(url);
      return parsePage(html, slug);
    } catch (err) {
      lastErr = err;
      if (attempt < RETRY_MAX) {
        await new Promise(r => setTimeout(r, 1200 * (attempt + 1)));
      }
    }
  }
  console.warn(`  ✗ Failed ${slug}: ${lastErr.message}`);
  // Return minimal fallback entry
  const title = slug.split('-').map(w => w[0].toUpperCase() + w.slice(1)).join(' ');
  return {
    slug,
    title,
    description: `Play ${title} free online.`,
    thumbnail: `https://azgames.io/upload/imgs/${slug.replace(/-/g,'')}.png`,
    category: DEFAULT_CAT
  };
}

// ── Concurrent queue ──────────────────────────────────────────────────────────
async function runConcurrent(items, fn, concurrency) {
  const results = new Array(items.length);
  let idx = 0;
  let done = 0;

  async function worker() {
    while (idx < items.length) {
      const i = idx++;
      results[i] = await fn(items[i]);
      done++;
      if (done % 20 === 0) console.log(`  Progress: ${done}/${items.length}`);
    }
  }

  const workers = Array.from({ length: concurrency }, () => worker());
  await Promise.all(workers);
  return results;
}

// ── Main ──────────────────────────────────────────────────────────────────────
(async () => {
  const games = await runConcurrent(slugs, scrapeSlug, CONCURRENCY);

  const output = {
    site: {
      name: 'AZ Games',
      domain: 'https://azgames.poki2.online',
      resourceSite: 'https://azgames.io'
    },
    categories: CATEGORIES,
    games
  };

  fs.mkdirSync(path.join(ROOT, 'src/data'), { recursive: true });
  fs.writeFileSync(OUT_FILE, JSON.stringify(output, null, 2), 'utf8');

  // Summary
  const catCounts = {};
  for (const g of games) catCounts[g.category] = (catCounts[g.category] || 0) + 1;
  console.log('\nCategory distribution:');
  for (const [cat, count] of Object.entries(catCounts)) console.log(`  ${cat}: ${count}`);
  console.log(`\nWrote ${games.length} games → ${OUT_FILE}`);
})();
