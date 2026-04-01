'use strict';

const fs   = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const { seoData: data, navGamesHtml } = require('./config');
const baseTemplate = fs.readFileSync(path.join(ROOT, 'src/templates/base.html'), 'utf8');
const distDir      = path.join(ROOT, 'dist');

fs.mkdirSync(distDir, { recursive: true });

for (const page of data.pages) {
  const contentPath = path.join(ROOT, 'src/content', `${page.slug}.html`);
  const content     = fs.readFileSync(contentPath, 'utf8');
  const schema      = buildSchema(page, data.site);

  const html = baseTemplate
    .replace(/\{\{TITLE\}\}/g,               escAttr(page.title))
    .replace(/\{\{DESCRIPTION\}\}/g,          escAttr(page.description))
    .replace(/\{\{KEYWORDS\}\}/g,             escAttr(page.keywords || ''))
    .replace(/\{\{CANONICAL\}\}/g,            escAttr(page.canonical))
    .replace(/\{\{OG_TITLE\}\}/g,             escAttr((page.og && page.og.title)       || page.title))
    .replace(/\{\{OG_DESCRIPTION\}\}/g,       escAttr((page.og && page.og.description) || page.description))
    .replace(/\{\{OG_URL\}\}/g,               escAttr((page.og && page.og.url)         || page.canonical))
    .replace(/\{\{OG_TYPE\}\}/g,              escAttr((page.og && page.og.type)        || 'website'))
    .replace(/\{\{OG_IMAGE\}\}/g,             escAttr((page.og && page.og.image)       || siteImage(data.site)))
    .replace(/\{\{TWITTER_CARD\}\}/g,         escAttr((page.twitter && page.twitter.card)        || 'summary_large_image'))
    .replace(/\{\{TWITTER_TITLE\}\}/g,        escAttr((page.twitter && page.twitter.title)       || page.title))
    .replace(/\{\{TWITTER_DESCRIPTION\}\}/g,  escAttr((page.twitter && page.twitter.description) || page.description))
    .replace(/\{\{TWITTER_IMAGE\}\}/g,        escAttr((page.twitter && page.twitter.image)       || siteImage(data.site)))
    .replace(/\{\{BODY_CLASS\}\}/g,           escAttr(page.bodyClass))
    .replace(/\{\{SCHEMA\}\}/g,               schema)
    .replace(/\{\{CONTENT\}\}/g,              content)
    .replace(/\{\{NAV_GAMES\}\}/g,            navGamesHtml);

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

function siteImage(site) {
  return (site && site.faviconUrl) || 'https://azgames.poki2.online/favicon.svg';
}

function buildSchema(page, site) {
  const schemas = [];

  schemas.push({
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    url: site.domain + '/',
    name: site.name,
    publisher: { '@type': 'Organization', name: site.name, url: site.domain + '/' }
  });

  if (page.slug === 'index') {
    schemas.push({
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: [
        {
          '@type': 'Question',
          name: 'What is AZ Games?',
          acceptedAnswer: { '@type': 'Answer', text: 'AZ Games is a free online gaming hub featuring 300+ browser games across 10 categories — no downloads, no login required.' }
        },
        {
          '@type': 'Question',
          name: 'Are all games on AZ Games free?',
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
