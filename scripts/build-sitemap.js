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

const today = new Date().toISOString();
const entries = [];

function fileLastModIso(filePath) {
  try {
    const stat = fs.statSync(filePath);
    // use full ISO datetime so search engines get precise lastmod
    return stat.mtime.toISOString();
  } catch (err) {
    return today;
  }
}

// Static pages
for (const p of seoData.pages) {
  if (p.indexable === false) continue;
  // try to read generated file mtime in dist
  const outPath = path.join(distDir, p.outputFile || (p.canonical.replace(/https?:\/\//, '').replace(new URL(p.canonical).origin, '').replace(/^\//, '') ) );
  const lastmod = fileLastModIso(outPath);
  entries.push(urlTag(p.canonical, lastmod, p.changefreq || 'monthly', p.priority || '0.5'));
}

// Game play pages
for (const g of gamesData.games.filter(g => !g.hidden)) {
  // prefer directory index if present
  const indexPath = path.join(distDir, 'play', g.slug, 'index.html');
  const flatPath = path.join(distDir, 'play', `${g.slug}.html`);
  const lastmod = fs.existsSync(indexPath) ? fileLastModIso(indexPath) : fileLastModIso(flatPath);
  entries.push(urlTag(`${gamesData.site.domain}/play/${g.slug}`, lastmod, 'weekly', '0.8'));
}

// Category pages
for (const c of gamesData.categories) {
  const catPath = path.join(distDir, 'category', `${c.slug}.html`);
  const lastmod = fileLastModIso(catPath);
  entries.push(urlTag(`${gamesData.site.domain}/category/${c.slug}`, lastmod, 'weekly', '0.9'));
}

// Blog index + posts
const blogDomain = gamesData.site.domain;
const blogIndexPath = path.join(distDir, 'blog.html');
entries.push(urlTag(`${blogDomain}/blog.html`, fileLastModIso(blogIndexPath), 'weekly', '0.8'));
for (const post of blogData.posts) {
  const postCanonical = post.canonical.replace('https://azgames.poki2.online', blogDomain);
  // try to find dist/blog/{slug}.html
  const slug = postCanonical.replace(/.*\/blog\//, '').replace(/\/?$/, '');
  const postPath = path.join(distDir, 'blog', `${slug}.html`);
  const lastmod = fileLastModIso(postPath) || post.date;
  entries.push(urlTag(postCanonical, lastmod, 'monthly', '0.7'));
}

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${entries.join('\n')}
</urlset>
`;

fs.writeFileSync(path.join(distDir, 'sitemap.xml'), sitemap, 'utf8');
console.log(`Built: dist/sitemap.xml (${entries.length} URLs)`);

function urlTag(loc, lastmod, changefreq, priority) {
  const normalizedLoc = loc.replace(/\.html$/, '');
  return [
    '  <url>',
    `    <loc>${normalizedLoc}</loc>`,
    `    <lastmod>${lastmod}</lastmod>`,
    `    <changefreq>${changefreq}</changefreq>`,
    `    <priority>${priority}</priority>`,
    '  </url>'
  ].join('\n');
}
