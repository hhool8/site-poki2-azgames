'use strict';

/**
 * Shared build configuration for AZ Games.
 * Domain and resource-site can be overridden at build time via env vars:
 *
 *   SITE_DOMAIN=https://azgames.poki2.online npm run build
 *   RESOURCE_SITE=https://azgames.io npm run build
 */

const fs   = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');

const seoData   = JSON.parse(fs.readFileSync(path.join(ROOT, 'src/data/seo.json'),   'utf8'));
const gamesData = JSON.parse(fs.readFileSync(path.join(ROOT, 'src/data/games.json'), 'utf8'));

// ── Apply env-var overrides ──────────────────────────────────────────────────
if (process.env.SITE_DOMAIN) {
  const newDomain = process.env.SITE_DOMAIN.replace(/\/$/, '');
  const oldDomain = seoData.site.domain;

  seoData.site.domain     = newDomain;
  seoData.site.faviconUrl = newDomain + '/favicon.svg';
  gamesData.site.domain   = newDomain;

  for (const page of seoData.pages) {
    if (page.canonical)           page.canonical           = page.canonical.replace(oldDomain, newDomain);
    if (page.og && page.og.url)   page.og.url              = page.og.url.replace(oldDomain, newDomain);
    if (page.og && page.og.image) page.og.image            = page.og.image.replace(oldDomain, newDomain);
    if (page.twitter && page.twitter.image)
                                  page.twitter.image       = page.twitter.image.replace(oldDomain, newDomain);
  }

  console.log(`[config] SITE_DOMAIN override: ${newDomain}`);
}

if (process.env.RESOURCE_SITE) {
  const newResource = process.env.RESOURCE_SITE.replace(/\/$/, '');
  gamesData.site.resourceSite = newResource;
  console.log(`[config] RESOURCE_SITE override: ${newResource}`);
}

// ── Build nav games dropdown HTML ────────────────────────────────────────────
const { games, categories } = gamesData;

const navGamesHtml = (function () {
  const groups = categories.map(cat => {
    const catGames = games.filter(g => g.category === cat.slug);
    const links = catGames.slice(0, 6).map(g =>
      `          <li><a href="/play/${g.slug}">${escHtml(g.title)}</a></li>`
    ).join('\n');
    return [
      `      <div class="nav-games-group">`,
      `        <a class="nav-games-cat" href="/category/${cat.slug}">${cat.emoji} ${escHtml(cat.name)}</a>`,
      `        <ul>`,
      links,
      `        </ul>`,
      `      </div>`
    ].join('\n');
  }).join('\n');

  return [
    `<div class="nav-games-wrap">`,
    `  <button class="cta-btn nav-games-btn" id="nav-games-btn" aria-haspopup="true" aria-expanded="false">`,
    `    Play Games &#x25BE;`,
    `  </button>`,
    `  <div class="nav-games-dropdown" id="nav-games-dropdown" aria-label="Game categories">`,
    `    <div class="nav-games-grid">`,
    groups,
    `    </div>`,
    `  </div>`,
    `</div>`
  ].join('\n');
})();

module.exports = { seoData, gamesData, navGamesHtml };

function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}
