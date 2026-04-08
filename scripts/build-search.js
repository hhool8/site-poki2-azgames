'use strict';

/**
 * build-search.js
 * Generates:
 *   dist/search-index.json  — lightweight client-side search data
 *   dist/search/index.html  — search results page
 */

const fs   = require('fs');
const path = require('path');

const ROOT         = path.join(__dirname, '..');
const { gamesData } = require('./config');
const baseTemplate = fs.readFileSync(path.join(ROOT, 'src/templates/base.html'),   'utf8');
const searchTpl    = fs.readFileSync(path.join(ROOT, 'src/templates/search.html'), 'utf8');

const distDir       = path.join(ROOT, 'dist');
const distSearchDir = path.join(distDir, 'search');
fs.mkdirSync(distSearchDir, { recursive: true });

const { site, games, categories } = gamesData;
const catMap = Object.fromEntries(categories.map(c => [c.slug, c]));

// ── Build search index ───────────────────────────────────────────────────────
const index = games.map(g => ({
  slug:        g.slug,
  title:       g.title,
  description: g.description,
  category:    g.category,
  catName:     (catMap[g.category] || {}).name || '',
  thumbnail:   g.thumbnail || '',
}));

fs.writeFileSync(
  path.join(distDir, 'search-index.json'),
  JSON.stringify(index),
  'utf8'
);
console.log(`Built: dist/search-index.json (${index.length} games)`);

// ── Build search page ────────────────────────────────────────────────────────
function escAttr(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

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
    .replace(/\{\{SCHEMA\}\}/g,               p.schema || '')
    .replace(/\{\{CONTENT\}\}/g,              p.content);
}

const canonicalUrl = `${site.domain}/search/`;
const title        = 'Search Games — AZ Games';
const description  = 'Search all free unblocked games on AZ Games. Find your favourite game instantly — no login, no VPN needed.';

const html = renderBase(baseTemplate, {
  title, description,
  keywords:    'search games, find games, unblocked games search, azgames search',
  canonical:   canonicalUrl,
  ogTitle:     title,
  ogDescription: description,
  ogUrl:       canonicalUrl,
  ogType:      'website',
  ogImage:     `${site.domain}/favicon.svg`,
  twitterCard: 'summary',
  twitterTitle: title,
  twitterDescription: description,
  twitterImage: `${site.domain}/favicon.svg`,
  bodyClass:   'search-page',
  schema:      '',
  content:     searchTpl,
});

fs.writeFileSync(path.join(distSearchDir, 'index.html'), html, 'utf8');
console.log('Built: dist/search/index.html');
