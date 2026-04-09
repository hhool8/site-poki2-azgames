'use strict';

const fs   = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const { seoData: data, gamesData } = require('./config');
const baseTemplate = fs.readFileSync(path.join(ROOT, 'src/templates/base.html'), 'utf8');
const distDir      = path.join(ROOT, 'dist');

fs.mkdirSync(distDir, { recursive: true });

const homepageGameRows = buildHomepageGameRows(gamesData.games, gamesData.categories);
const siteNavItems = [
  { name: 'Home', url: `${data.site.domain}/` },
  { name: 'Games', url: `${data.site.domain}/category/clicker-games.html` },
  { name: 'Blog', url: `${data.site.domain}/blog.html` },
  { name: 'About', url: `${data.site.domain}/about.html` },
  { name: 'Contact', url: `${data.site.domain}/contact.html` }
];

for (const page of data.pages) {
  const contentPath = path.join(ROOT, 'src/content', `${page.slug}.html`);
  let content       = fs.readFileSync(contentPath, 'utf8');
  if (page.slug === 'index') {
    content = content.replace('{{HOMEPAGE_GAME_ROWS}}', homepageGameRows);
  }
  const schema = buildSchema(page, data.site);

  const html = baseTemplate
    .replace(/\{\{TITLE\}\}/g,               escAttr(withBrand(page.title)))
    .replace(/\{\{DESCRIPTION\}\}/g,          escAttr(page.description))
    .replace(/\{\{KEYWORDS\}\}/g,             escAttr(page.keywords || ''))
    .replace(/\{\{CANONICAL\}\}/g,            escAttr(page.canonical))
    .replace(/\{\{ROBOTS_META\}\}/g,          robotsMeta(page.indexable !== false))
    .replace(/\{\{OG_TITLE\}\}/g,             escAttr(withBrand((page.og && page.og.title) || page.title)))
    .replace(/\{\{OG_DESCRIPTION\}\}/g,       escAttr((page.og && page.og.description) || page.description))
    .replace(/\{\{OG_URL\}\}/g,               escAttr((page.og && page.og.url)         || page.canonical))
    .replace(/\{\{OG_TYPE\}\}/g,              escAttr((page.og && page.og.type)        || 'website'))
    .replace(/\{\{OG_IMAGE\}\}/g,             escAttr((page.og && page.og.image)       || siteImage(data.site)))
    .replace(/\{\{TWITTER_CARD\}\}/g,         escAttr((page.twitter && page.twitter.card)        || 'summary_large_image'))
    .replace(/\{\{TWITTER_TITLE\}\}/g,        escAttr(withBrand((page.twitter && page.twitter.title) || page.title)))
    .replace(/\{\{TWITTER_DESCRIPTION\}\}/g,  escAttr((page.twitter && page.twitter.description) || page.description))
    .replace(/\{\{TWITTER_IMAGE\}\}/g,        escAttr((page.twitter && page.twitter.image)       || siteImage(data.site)))
    .replace(/\{\{BODY_CLASS\}\}/g,           escAttr(page.bodyClass))
    .replace(/\{\{SCHEMA\}\}/g,               schema)
    .replace(/\{\{CONTENT\}\}/g,              content);

  const outPath = path.join(distDir, page.outputFile);
  fs.writeFileSync(outPath, html, 'utf8');
  console.log(`Built: dist/${page.outputFile}`);
}

// Copy public/ → dist/
const publicDir = path.join(ROOT, 'public');
if (fs.existsSync(publicDir)) {
  copyDir(publicDir, distDir);
  console.log('Copied: public/ -> dist/');
}

// Copy css/ → dist/css/
const cssDir     = path.join(ROOT, 'css');
const distCssDir = path.join(distDir, 'css');
if (fs.existsSync(cssDir)) {
  fs.mkdirSync(distCssDir, { recursive: true });
  copyDir(cssDir, distCssDir);
  console.log('Copied: css/ -> dist/css/');
}

console.log('\nBuild complete.');

// ── Helpers ──────────────────────────────────────────────────────────────────
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

function siteImage(site) {
  return (site && site.faviconUrl) || 'https://azgames.poki2.online/favicon.svg';
}

function withBrand(title) {
  const value = String(title || '').trim();
  if (!value) return data.site.name;
  if (value.includes('AZ Games by Poki2')) return value;
  if (value.includes('AZ Games')) return value.replace(/AZ Games/g, 'AZ Games by Poki2');
  return `${value} | ${data.site.name}`;
}

function robotsMeta(indexable) {
  return `<meta name="robots" content="${indexable ? 'index,follow' : 'noindex,follow'}">`;
}

function buildSchema(page, site) {
  const schemas = [];

  schemas.push({
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: site.name,
    alternateName: site.shortName || site.name,
    url: site.domain + '/',
    logo: siteImage(site),
    contactPoint: [{
      '@type': 'ContactPoint',
      contactType: 'customer support',
      email: site.email,
      url: `${site.domain}/contact.html`
    }]
  });

  schemas.push({
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    url: site.domain + '/',
    name: site.name,
    alternateName: site.shortName || site.name,
    publisher: { '@type': 'Organization', name: site.name, url: site.domain + '/' },
    potentialAction: {
      '@type': 'SearchAction',
      target: `${site.domain}/search/?q={search_term_string}`,
      'query-input': 'required name=search_term_string'
    }
  });

  schemas.push({
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: 'Primary site navigation',
    itemListElement: siteNavItems.map((item, index) => ({
      '@type': 'SiteNavigationElement',
      position: index + 1,
      name: item.name,
      url: item.url
    }))
  });

  if (page.slug === 'index') {
    schemas.push({
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: [
        {
          '@type': 'Question',
          name: 'What is AZ Games by Poki2?',
          acceptedAnswer: { '@type': 'Answer', text: 'AZ Games by Poki2 is a free online gaming hub featuring 300+ browser games across 10 categories — no downloads, no login required.' }
        },
        {
          '@type': 'Question',
          name: 'Are all games on AZ Games by Poki2 free?',
          acceptedAnswer: { '@type': 'Answer', text: 'Yes. Every game is completely free to play. The site is supported by advertising.' }
        },
        {
          '@type': 'Question',
          name: 'Do I need to create an account?',
          acceptedAnswer: { '@type': 'Answer', text: 'No account required. Visit the site and click any game to start playing immediately.' }
        },
        {
          '@type': 'Question',
          name: 'Do games work on mobile?',
          acceptedAnswer: { '@type': 'Answer', text: 'Most games support touch input and work on smartphones and tablets.' }
        }
      ]
    });
  } else if (page.slug === 'about') {
    schemas.push({ '@context': 'https://schema.org', '@type': 'AboutPage', url: page.canonical, name: page.title, inLanguage: 'en' });
  } else if (page.slug === 'contact') {
    schemas.push({ '@context': 'https://schema.org', '@type': 'ContactPage', url: page.canonical, name: page.title, inLanguage: 'en' });
  } else {
    schemas.push({ '@context': 'https://schema.org', '@type': 'WebPage', url: page.canonical, name: page.title, inLanguage: 'en' });
  }

  if (page.slug !== 'index') {
    schemas.push({
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Home', item: site.domain + '/' },
        { '@type': 'ListItem', position: 2, name: page.h1 || page.title, item: page.canonical }
      ]
    });
  }

  return schemas
    .map(s => `  <script type="application/ld+json">${JSON.stringify(s)}</script>`)
    .join('\n');
}

// ── Homepage game rows ──────────────────────────────────────────────────────
function buildHomepageGameRows(games, categories) {
  return categories.map(cat => {
    const catGames = games.filter(g => g.category === cat.slug).slice(0, 12);
    if (catGames.length === 0) return '';
    const cardsHtml = catGames.map(game =>
      `      <a class="game-card" href="/play/${game.slug}.html" aria-label="Play ${escAttr(game.title)} free online">
        <img src="${escAttr(game.thumbnail)}" alt="${escAttr(game.title)}" loading="lazy" width="180" height="135">
        <span class="game-card-label">${escHtml(game.title)}</span>
      </a>`
    ).join('\n');
    return `<div class="game-row">
  <div class="game-row-header">
    <h2><a href="/category/${cat.slug}.html">${cat.emoji} ${escHtml(cat.name)}</a></h2>
    <a class="game-row-viewall" href="/category/${cat.slug}.html">View all &rsaquo;</a>
  </div>
  <div class="game-row-grid">
${cardsHtml}
  </div>
</div>`;
  }).filter(Boolean).join('\n\n');
}

function copyDir(src, dest) {
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const srcPath  = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      fs.mkdirSync(destPath, { recursive: true });
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}
