'use strict';

const fs   = require('fs');
const path = require('path');

const ROOT     = path.join(__dirname, '..');
const seoData  = JSON.parse(fs.readFileSync(path.join(ROOT, 'src/data/seo.json'),        'utf8'));
const gamesData = JSON.parse(fs.readFileSync(path.join(ROOT, 'src/data/games.json'),     'utf8'));
const blogData  = JSON.parse(fs.readFileSync(path.join(ROOT, 'src/data/blog-posts.json'),'utf8'));

// Apply SITE_DOMAIN override
if (process.env.SITE_DOMAIN) {
  const newDomain = process.env.SITE_DOMAIN.replace(/\/$/, '');
  const oldDomain = seoData.site.domain;
  seoData.site.domain   = newDomain;
  gamesData.site.domain = newDomain;
  for (const page of seoData.pages) {
    if (page.canonical) page.canonical = page.canonical.replace(oldDomain, newDomain);
  }
}

const distDir = path.join(ROOT, 'dist');
fs.mkdirSync(distDir, { recursive: true });

const today = new Date().toISOString().split('T')[0];
const entries = [];

// Static pages
for (const p of seoData.pages) {
  entries.push(urlTag(p.canonical, today, p.changefreq || 'monthly', p.priority || '0.5'));
}

// Game play pages
for (const g of gamesData.games) {
  entries.push(urlTag(`${gamesData.site.domain}/play/${g.slug}.html`, today, 'weekly', '0.8'));
}

// Category pages
for (const c of gamesData.categories) {
  entries.push(urlTag(`${gamesData.site.domain}/category/${c.slug}.html`, today, 'weekly', '0.9'));
}

// Blog index + posts
const blogDomain = gamesData.site.domain;
entries.push(urlTag(`${blogDomain}/blog.html`, today, 'weekly', '0.8'));
for (const post of blogData.posts) {
  const postCanonical = post.canonical.replace('https://azgames.poki2.online', blogDomain);
  entries.push(urlTag(postCanonical, post.date, 'monthly', '0.7'));
}

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${entries.join('\n')}
</urlset>
`;

fs.writeFileSync(path.join(distDir, 'sitemap.xml'), sitemap, 'utf8');
console.log(`Built: dist/sitemap.xml (${entries.length} URLs)`);

function urlTag(loc, lastmod, changefreq, priority) {
  return [
    '  <url>',
    `    <loc>${loc}</loc>`,
    `    <lastmod>${lastmod}</lastmod>`,
    `    <changefreq>${changefreq}</changefreq>`,
    `    <priority>${priority}</priority>`,
    '  </url>'
  ].join('\n');
}
