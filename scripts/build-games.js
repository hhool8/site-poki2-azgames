'use strict';

const fs   = require('fs');
const path = require('path');

const ROOT            = path.join(__dirname, '..');
const { gamesData } = require('./config');
const baseTemplate    = fs.readFileSync(path.join(ROOT, 'src/templates/base.html'),     'utf8');
const playTemplate    = fs.readFileSync(path.join(ROOT, 'src/templates/play.html'),     'utf8');
const categoryTemplate = fs.readFileSync(path.join(ROOT, 'src/templates/category.html'), 'utf8');

const distDir         = path.join(ROOT, 'dist');
const distPlayDir     = path.join(distDir, 'play');
const distCategoryDir = path.join(distDir, 'category');

fs.mkdirSync(distPlayDir,     { recursive: true });
fs.mkdirSync(distCategoryDir, { recursive: true });

const { site, games, categories } = gamesData;
const catMap = Object.fromEntries(categories.map(c => [c.slug, c]));

// ── Play pages ───────────────────────────────────────────────────────────────

for (const game of games) {
  const cat         = catMap[game.category] || categories[categories.length - 1];
  const canonicalUrl = `${site.domain}/play/${game.slug}.html`;
  // AZ Games embed URL pattern: https://azgames.io/{slug}.embed
  const resourceUrl  = `${site.resourceSite}/${game.slug}.embed`;
  const thumbUrl     = game.thumbnail;

  const schema = buildSchema([
    {
      '@context': 'https://schema.org',
      '@type': 'VideoGame',
      name: game.title,
      description: game.description,
      url: canonicalUrl,
      genre: cat.name,
      gamePlatform: 'Browser',
      applicationCategory: 'Game',
      operatingSystem: 'Any',
      offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' }
    }
  ]);

  const content = playTemplate
    .replace(/\{\{GAME_TITLE\}\}/g,    game.title)
    .replace(/\{\{GAME_SLUG\}\}/g,     game.slug)
    .replace(/\{\{GAME_DESCRIPTION\}\}/g, game.description)
    .replace(/\{\{CATEGORY_SLUG\}\}/g, cat.slug)
    .replace(/\{\{CATEGORY_NAME\}\}/g, cat.name)
    .replace(/\{\{RESOURCE_URL\}\}/g,  resourceUrl);

  const title       = `Play ${game.title} Free Online — No Download | AZ Games`;
  const description = `Play ${game.title} for free in your browser. ${game.description} No download, no login — instant play on AZ Games!`;

  const html = renderBase(baseTemplate, {
    title, description,
    keywords:     `${game.title}, ${game.title} online, ${game.title} free, play ${game.title}`,
    canonical:    canonicalUrl,
    ogTitle:      title,
    ogDescription: description,
    ogUrl:        canonicalUrl,
    ogType:       'website',
    ogImage:      thumbUrl,
    twitterCard:  'summary_large_image',
    twitterTitle: title,
    twitterDescription: description,
    twitterImage: thumbUrl,
    bodyClass:    'game-play-page',
    schema,
    content
  });

  fs.writeFileSync(path.join(distPlayDir, `${game.slug}.html`), html, 'utf8');
  console.log(`Built: dist/play/${game.slug}.html`);
}

// ── Category pages ────────────────────────────────────────────────────────────

for (const cat of categories) {
  const catGames     = games.filter(g => g.category === cat.slug);
  const canonicalUrl = `${site.domain}/category/${cat.slug}.html`;
  const thumbUrl     = `${site.domain}/favicon.svg`;

  const gamesHtml = catGames.map(game =>
    `      <a class="game-card" href="/play/${game.slug}.html" aria-label="${escAttr('Play ' + game.title + ' free online')}">
        <img src="${escAttr(game.thumbnail)}" alt="${escAttr(game.title)}" loading="lazy">
        <span class="game-card-label">${escHtml(game.title)}</span>
      </a>`
  ).join('\n');

  const schema = buildSchema([
    {
      '@context': 'https://schema.org',
      '@type': 'CollectionPage',
      name: `${cat.name} Games — AZ Games`,
      description: cat.description,
      url: canonicalUrl,
      hasPart: catGames.map(g => ({
        '@type': 'VideoGame',
        name: g.title,
        url: `${site.domain}/play/${g.slug}.html`
      }))
    }
  ]);

  const content = categoryTemplate
    .replace(/\{\{CATEGORY_TITLE\}\}/g,       cat.name)
    .replace(/\{\{CATEGORY_EMOJI\}\}/g,        cat.emoji)
    .replace(/\{\{CATEGORY_DESCRIPTION\}\}/g,  cat.description)
    .replace(/\{\{GAME_COUNT\}\}/g,            catGames.length)
    .replace(/\{\{GAMES_HTML\}\}/g,            gamesHtml);

  const title       = `${cat.name} — Play Free Online, No Download | AZ Games`;
  const description = `Play ${catGames.length} free ${cat.name} games online at AZ Games. ${cat.description} No download, no login — instant browser play!`;

  const html = renderBase(baseTemplate, {
    title, description,
    keywords:     `${cat.name.toLowerCase()} online free, play ${cat.name.toLowerCase()}, free ${cat.name.toLowerCase()} no download, az games ${cat.name.toLowerCase()}, browser ${cat.name.toLowerCase()}`,
    canonical:    canonicalUrl,
    ogTitle:      title,
    ogDescription: description,
    ogUrl:        canonicalUrl,
    ogType:       'website',
    ogImage:      thumbUrl,
    twitterCard:  'summary_large_image',
    twitterTitle: title,
    twitterDescription: description,
    twitterImage: thumbUrl,
    bodyClass:    'category-page',
    schema,
    content
  });

  fs.writeFileSync(path.join(distCategoryDir, `${cat.slug}.html`), html, 'utf8');
  console.log(`Built: dist/category/${cat.slug}.html`);
}

console.log(`\nBuild complete: ${games.length} play pages, ${categories.length} category pages.`);

// ── Helpers ───────────────────────────────────────────────────────────────────

function renderBase(template, p) {
  return template
    .replace(/\{\{TITLE\}\}/g,               escAttr(p.title))
    .replace(/\{\{DESCRIPTION\}\}/g,          escAttr(p.description))
    .replace(/\{\{KEYWORDS\}\}/g,             escAttr(p.keywords || ''))
    .replace(/\{\{CANONICAL\}\}/g,            escAttr(p.canonical))
    .replace(/\{\{OG_TITLE\}\}/g,             escAttr(p.ogTitle))
    .replace(/\{\{OG_DESCRIPTION\}\}/g,       escAttr(p.ogDescription))
    .replace(/\{\{OG_URL\}\}/g,               escAttr(p.ogUrl))
    .replace(/\{\{OG_TYPE\}\}/g,              escAttr(p.ogType))
    .replace(/\{\{OG_IMAGE\}\}/g,             escAttr(p.ogImage))
    .replace(/\{\{TWITTER_CARD\}\}/g,         escAttr(p.twitterCard))
    .replace(/\{\{TWITTER_TITLE\}\}/g,        escAttr(p.twitterTitle))
    .replace(/\{\{TWITTER_DESCRIPTION\}\}/g,  escAttr(p.twitterDescription))
    .replace(/\{\{TWITTER_IMAGE\}\}/g,        escAttr(p.twitterImage))
    .replace(/\{\{BODY_CLASS\}\}/g,           escAttr(p.bodyClass))
    .replace(/\{\{SCHEMA\}\}/g,               p.schema)
    .replace(/\{\{CONTENT\}\}/g,              p.content);
}

function buildSchema(schemas) {
  return schemas.map(s =>
    `<script type="application/ld+json">\n${JSON.stringify(s, null, 2)}\n</script>`
  ).join('\n');
}

function escAttr(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}
