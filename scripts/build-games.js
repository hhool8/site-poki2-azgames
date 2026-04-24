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
const siteNavItems = [
  { name: 'Home', url: `${site.domain}/` },
  { name: 'Games', url: `${site.domain}/category/clicker-games` },
  { name: 'Blog', url: `${site.domain}/blog.html` },
  { name: 'About', url: `${site.domain}/about.html` },
  { name: 'Contact', url: `${site.domain}/contact.html` }
];

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
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Home', item: `${site.domain}/` },
        { '@type': 'ListItem', position: 2, name: cat.name, item: `${site.domain}/category/${cat.slug}` },
        { '@type': 'ListItem', position: 3, name: game.title, item: canonicalUrl }
      ]
    },
    {
      '@context': 'https://schema.org',
      '@type': 'VideoGame',
      name: game.title,
      description: game.description,
      url: canonicalUrl,
      mainEntityOfPage: canonicalUrl,
      image: thumbUrl,
      genre: cat.name,
      gamePlatform: 'Browser',
      applicationCategory: 'Game',
      operatingSystem: 'Any',
      isFamilyFriendly: true,
      offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' }
    },
    {
      '@context': 'https://schema.org',
      '@type': 'ItemList',
      name: 'Primary site navigation',
      itemListElement: siteNavItems.map((item, index) => ({
        '@type': 'SiteNavigationElement',
        position: index + 1,
        name: item.name,
        url: item.url
      }))
    }
  ]);

  const content = playTemplate
    .replace(/\{\{GAME_TITLE\}\}/g,    game.title)
    .replace(/\{\{GAME_SLUG\}\}/g,     game.slug)
    .replace(/\{\{GAME_DESCRIPTION\}\}/g, game.description)
    .replace(/\{\{CATEGORY_SLUG\}\}/g, cat.slug)
    .replace(/\{\{CATEGORY_NAME\}\}/g, cat.name)
    .replace(/\{\{RESOURCE_URL\}\}/g,  resourceUrl);

  const title       = withBrand(`Play ${game.title} Unblocked — Free, No VPN`);
  const description = `Play ${game.title} unblocked on Chromebook — no VPN, no download, no login. ${game.description} Instant free browser play on AZ Games by Poki2.`;

  const html = renderBase(baseTemplate, {
    title, description,
    keywords:     `${game.title}, ${game.title} unblocked, ${game.title} unblocked chromebook, play ${game.title} no vpn, ${game.title} free online no download`,
    canonical:    canonicalUrl,
    robotsMeta:   robotsMeta(true),
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
  const canonicalUrl = `${site.domain}/category/${cat.slug}`;
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
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Home', item: `${site.domain}/` },
        { '@type': 'ListItem', position: 2, name: `${cat.name} Games`, item: canonicalUrl }
      ]
    },
    {
      '@context': 'https://schema.org',
      '@type': 'CollectionPage',
      name: `${cat.name} Games — ${site.name}`,
      description: cat.description,
      url: canonicalUrl,
      mainEntity: {
        '@type': 'ItemList',
        itemListElement: catGames.slice(0, 24).map((g, index) => ({
          '@type': 'ListItem',
          position: index + 1,
          url: `${site.domain}/play/${g.slug}.html`,
          name: g.title
        }))
      }
    },
    {
      '@context': 'https://schema.org',
      '@type': 'ItemList',
      name: 'Primary site navigation',
      itemListElement: siteNavItems.map((item, index) => ({
        '@type': 'SiteNavigationElement',
        position: index + 1,
        name: item.name,
        url: item.url
      }))
    },
    {
      '@context': 'https://schema.org',
      '@type': 'ItemList',
      name: `${cat.name} games list`,
      itemListElement: catGames.slice(0, 24).map((g, index) => ({
        '@type': 'ListItem',
        position: index + 1,
        item: {
        '@type': 'VideoGame',
        name: g.title,
        url: `${site.domain}/play/${g.slug}.html`
        }
      }))
    }
  ]);

  const content = categoryTemplate
    .replace(/\{\{CATEGORY_TITLE\}\}/g,       cat.name)
    .replace(/\{\{CATEGORY_EMOJI\}\}/g,        cat.emoji)
    .replace(/\{\{CATEGORY_DESCRIPTION\}\}/g,  cat.description)
    .replace(/\{\{GAME_COUNT\}\}/g,            catGames.length)
    .replace(/\{\{GAMES_HTML\}\}/g,            gamesHtml);

  const title       = withBrand(`${cat.name} Games — Play Free Online, No Download`);
  const description = `Play ${catGames.length} free ${cat.name} games online at AZ Games by Poki2. ${cat.description} No download, no login — instant browser play.`;

  const html = renderBase(baseTemplate, {
    title, description,
    keywords:     ({
      'clicker-games':   'italian brainrot clicker, labubu clicker game, brainrot clicker, clicker games online free, free clicker games no download',
      'io-games':        'brainrot games online, io games online free, play io games free, free io games no download, browser io games',
      'car-games':       'escape road game online, car games free online, drift car games, free car games no download, browser car games',
      'adventure-games': 'escape road game online, adventure games free online, free adventure games no download, browser adventure games',
      '2-player-games':  '2 player games no download, two player games online free, free 2 player games browser, multiplayer browser games',
      'shooting-games':  'shooting games free online, free shooting games no download, browser shooting games, online shooting games',
      'sports-games':    'sports games free online, free sports games no download, browser sports games, online sports games',
      'puzzle-games':    'puzzle games free online, free puzzle games no download, brain puzzle games browser, puzzle games no login',
      'casual-games':    'casual games free online, free casual games no download, browser casual games, casual games no login',
      'kids-games':      'kids games free online, free kids games no download, safe kids browser games, kids games no login',
    })[cat.slug] || `${cat.name.toLowerCase()} online free, play ${cat.name.toLowerCase()}, free ${cat.name.toLowerCase()} no download`,
    canonical:    canonicalUrl,
    robotsMeta:   robotsMeta(true),
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
    .replace(/\{\{ROBOTS_META\}\}/g,          p.robotsMeta)
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

function withBrand(title) {
  const value = String(title || '').trim();
  if (!value) return site.name;
  if (value.includes(site.name)) return value;
  if (value.includes('AZ Games')) return value.replace(/AZ Games/g, site.name);
  return `${value} | ${site.name}`;
}

function robotsMeta(indexable) {
  return `<meta name="robots" content="${indexable ? 'index,follow' : 'noindex,follow'}">`;
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
