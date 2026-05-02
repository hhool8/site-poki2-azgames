'use strict';

/**
 * Build blog pages:
 *  - dist/blog.html  (index)
 *  - dist/blog/*.html (10 posts, one per category)
 */

const fs   = require('fs');
const path = require('path');

const ROOT          = path.join(__dirname, '..');
const { seoData, gamesData } = require('./config');
const blogData      = JSON.parse(fs.readFileSync(path.join(ROOT, 'src/data/blog-posts.json'), 'utf8'));
const baseTemplate  = fs.readFileSync(path.join(ROOT, 'src/templates/base.html'), 'utf8');
const postTemplate  = fs.readFileSync(path.join(ROOT, 'src/templates/blog-post.html'), 'utf8');
const indexContent  = fs.readFileSync(path.join(ROOT, 'src/content/blog-index.html'), 'utf8');

const distDir     = path.join(ROOT, 'dist');
const distBlogDir = path.join(distDir, 'blog');
fs.mkdirSync(distBlogDir, { recursive: true });

const { categories } = gamesData;
const games = gamesData.games.filter(g => !g.hidden);
const catMap = Object.fromEntries(categories.map(c => [c.slug, c]));
const site   = seoData.site;
const siteNavItems = [
  { name: 'Home', url: `${site.domain}/` },
  { name: 'Games', url: `${site.domain}/category/clicker-games` },
  { name: 'Blog', url: `${site.domain}/blog.html` },
  { name: 'About', url: `${site.domain}/about.html` },
  { name: 'Contact', url: `${site.domain}/contact.html` }
];

// ── Article bodies (auto-generated SEO content) ────────────────────────────
const ARTICLE_BODIES = {
  'clicker-games': `
<p>Clicker games (also called idle games or incremental games) are one of the most popular browser game genres — and for good reason. They are satisfying, endlessly replayable, and require no complex setup. Whether you are waiting for class to start or taking a quick break at work, a good clicker game is always ready.</p>

<h2>What Makes a Great Clicker Game?</h2>
<p>The best clicker games share a few key traits:</p>
<ul>
  <li><strong>Fast early progress</strong> — numbers go up quickly at first, giving you an instant dopamine hit.</li>
  <li><strong>Meaningful upgrades</strong> — each purchase or upgrade feels impactful and changes the pace of the game.</li>
  <li><strong>Idle mechanics</strong> — the game keeps progressing even when you are not actively clicking.</li>
  <li><strong>Long-term goals</strong> — prestige systems, unlockable content, or milestones that keep you coming back.</li>
</ul>

<h2>Top Free Clicker Games at AZ Games</h2>
<p>On <a href="/category/clicker-games">AZ Games Clicker Games</a>, you will find a wide variety of incremental titles — from simple tap-to-earn games to deep idle simulations with dozens of upgrade trees. All titles run directly in your browser with no download required.</p>

<h2>Tips for Getting the Most Out of Clicker Games</h2>
<ul>
  <li>Focus upgrades that multiply your income, not just add to it.</li>
  <li>Use prestige/reset mechanics early — they give exponential bonuses.</li>
  <li>Leave idle games running in a background tab for passive income.</li>
  <li>Check achievement lists — many give multipliers when completed.</li>
</ul>

<h2>Play Clicker Games Free Online — No Download</h2>
<p>Every clicker game on AZ Games is 100% free and plays in your web browser on Windows, Mac, Chromebook, iOS, and Android. No login, no account, no download required. Just click and play.</p>
`,

  'io-games': `
<p>.IO games are browser-based multiplayer games where you compete against real players from around the world in real time. Named after the <em>.io</em> top-level domain where many originated (like Agar.io and Slither.io), these games are lightweight, addictive, and perfect for quick sessions.</p>

<h2>Why .IO Games Are So Popular</h2>
<p>Unlike traditional multiplayer games that require accounts, downloads, or high-end hardware, .IO games are instantly accessible. Open a browser, visit the page, enter a name (or stay anonymous), and you are dropped right into a live match with other players worldwide.</p>
<ul>
  <li><strong>No install, no login</strong> — play from any device with a browser.</li>
  <li><strong>Real competition</strong> — you are up against real players, not bots, making every session different.</li>
  <li><strong>Short sessions</strong> — most matches last 5–15 minutes, ideal for breaks.</li>
</ul>

<h2>Popular .IO Game Styles</h2>
<ul>
  <li><strong>Cell/blob games (Agar.io style)</strong> — grow your cell by eating smaller players.</li>
  <li><strong>Snake games (Slither.io style)</strong> — collect dots to grow, avoid crashing into other snakes.</li>
  <li><strong>Battle royale IO</strong> — last player standing wins.</li>
  <li><strong>Territory control (Paper.io style)</strong> — claim land while protecting your trail.</li>
</ul>

<h2>Play .IO Games Free at AZ Games</h2>
<p>Browse our full <a href="/category/io-games">.IO Games collection</a> and start playing instantly — no download, no account needed. Works on desktop and mobile browsers.</p>
`,

  'adventure-games': `
<p>Adventure games are one of the most beloved genres in gaming. From side-scrolling platformers to point-and-click mysteries, adventure games challenge you to explore, discover, and overcome. The best part? You can play hundreds of them free online right in your browser.</p>

<h2>What Defines an Adventure Game?</h2>
<ul>
  <li><strong>Exploration</strong> — large worlds or interconnected areas to discover.</li>
  <li><strong>Narrative</strong> — a story or quest driving your progress.</li>
  <li><strong>Problem-solving</strong> — puzzles, enemies, or obstacles requiring thought and skill.</li>
  <li><strong>Character progression</strong> — levels, upgrades, or inventory that grow over time.</li>
</ul>

<h2>Types of Adventure Games You Will Find at AZ Games</h2>
<ul>
  <li><strong>Platformers</strong> — run, jump, and fight your way through levels.</li>
  <li><strong>RPG-lite</strong> — light role-playing mechanics with combat and dialogue.</li>
  <li><strong>Action-adventure</strong> — combining combat with exploration.</li>
  <li><strong>Point-and-click</strong> — story-rich puzzle games driven by mouse clicks.</li>
</ul>

<h2>Play Free Adventure Games Online</h2>
<p>All adventure games on the <a href="/category/adventure-games">AZ Games Adventure Games page</a> run in your browser — no download, no login. Whether you are on a PC, Mac, or phone, you can start exploring in seconds.</p>
`,

  '2-player-games': `
<p>2 player games are a special treat — playing against a friend on the same screen brings out a competitive spirit that solo games simply cannot replicate. Whether you are challenging a sibling, a classmate, or a friend sitting next to you, these games turn any browser into a local multiplayer arena.</p>

<h2>How 2 Player Browser Games Work</h2>
<p>2 player browser games typically use split keyboard controls — each player uses a different section of the keyboard. Common setups are WASD for player one and arrow keys for player two. Some games also support gamepads.</p>

<h2>Best Types of 2 Player Games</h2>
<ul>
  <li><strong>Fighting games</strong> — head-to-head combat on a shared screen.</li>
  <li><strong>Racing games</strong> — split-screen or side-by-side racing.</li>
  <li><strong>Sports games</strong> — 1v1 basketball, soccer, or volleyball.</li>
  <li><strong>Platformers</strong> — cooperative or competitive platformer challenges.</li>
</ul>

<h2>Play 2 Player Games Free at AZ Games</h2>
<p>Browse the full <a href="/category/2-player-games">2 Player Games collection</a> on AZ Games. All titles run in your browser — gather a friend and start competing in seconds.</p>
`,

  'shooting-games': `
<p>Shooting games are among the most exciting browser game genres. From precision aim-trainer challenges to full-blown first-person shooters and top-down blasters, the genre offers something for every skill level and playstyle.</p>

<h2>Types of Free Browser Shooting Games</h2>
<ul>
  <li><strong>First-person shooters (FPS)</strong> — see the world through your character's eyes and aim with mouse precision.</li>
  <li><strong>Top-down shooters</strong> — overhead view with waves of enemies to blast through.</li>
  <li><strong>Aim trainers</strong> — practice and improve your accuracy with moving targets.</li>
  <li><strong>Side-scrolling shooters</strong> — run and gun adventures from a 2D perspective.</li>
</ul>

<h2>What Makes a Good Browser Shooting Game?</h2>
<ul>
  <li>Responsive controls — especially mouse aim sensitivity and movement.</li>
  <li>Clear feedback — visible hit effects and audio cues.</li>
  <li>Balanced difficulty — challenging but fair enemy AI or multiplayer opponents.</li>
</ul>

<h2>Play Free Shooting Games Online at AZ Games</h2>
<p>Explore the <a href="/category/shooting-games">Shooting Games section</a> on AZ Games and try dozens of free browser shooters — no download, no account, instant play.</p>
`,

  'sports-games': `
<p>Sports games let you experience the thrill of athletic competition from your browser. Whether you are shooting three-pointers, scoring free kicks, or teeing off on a virtual golf course, free online sports games bring the action to your screen in seconds.</p>

<h2>Popular Online Sports Game Categories</h2>
<ul>
  <li><strong>Basketball</strong> — from casual shooting games to full 2D simulation titles.</li>
  <li><strong>Soccer / Football</strong> — penalty shootouts, head-to-head matches, and goalkeeper challenges.</li>
  <li><strong>Golf</strong> — mini-golf and full-course 2D/3D golf games.</li>
  <li><strong>Athletics</strong> — track and field events, swimming, and more.</li>
</ul>

<h2>Why Play Sports Games in a Browser?</h2>
<p>Browser sports games play instantly — no large download, no setup. You can pick up a basketball game during a five-minute break and put it down equally quickly. They are also great for quick competitive sessions with friends using 2-player keyboard controls.</p>

<h2>Play Free Sports Games at AZ Games</h2>
<p>Browse the full <a href="/category/sports-games">Sports Games collection</a> on AZ Games. All games work in your browser on desktop and mobile.</p>
`,

  'car-games': `
<p>Car games have always been a browser gaming staple. From chaotic stunt arenas to realistic drift simulators, free online car games scratch that need for speed without requiring any Steam purchase or high-end GPU.</p>

<h2>Types of Free Browser Car Games</h2>
<ul>
  <li><strong>Racing games</strong> — circuit races or point-to-point sprints against AI or friends.</li>
  <li><strong>Drift games</strong> — score points by drifting around corners, controlling oversteer with precision.</li>
  <li><strong>Stunt games</strong> — ramps, loops, and destruction courses that defy physics.</li>
  <li><strong>Parking simulators</strong> — maneuver vehicles into tight spots under time pressure.</li>
</ul>

<h2>Tips for Browser Car Games</h2>
<ul>
  <li>Use analog controls (gamepad) if available — many support it for smoother steering.</li>
  <li>In drift games, trail-brake into corners and apply throttle mid-corner to maintain angle.</li>
  <li>Racing games often have rubber-band AI — stay clean and consistent rather than going for risky overtakes.</li>
</ul>

<h2>Play Car Games Free Online at AZ Games</h2>
<p>Find your next favorite racing or driving game in our <a href="/category/car-games">Car Games section</a> — free, instant play, no download required.</p>
`,

  'puzzle-games': `
<p>Puzzle games are the ultimate mental workout. They challenge your logic, spatial reasoning, and pattern recognition in ways that are satisfying and rewarding. The best browser puzzle games are easy to start but hard to master — perfect for all ages.</p>

<h2>Types of Online Puzzle Games</h2>
<ul>
  <li><strong>Logic puzzles</strong> — deductive reasoning challenges like Sudoku-style or grid-based problems.</li>
  <li><strong>Match-3 games</strong> — align three or more matching tiles to clear them from the board.</li>
  <li><strong>Physics puzzles</strong> — use real-world physics to move objects and solve challenges.</li>
  <li><strong>Word games</strong> — crosswords, word searches, and anagram challenges.</li>
  <li><strong>Number puzzles</strong> — 2048-style combinatorial challenges.</li>
</ul>

<h2>Benefits of Playing Puzzle Games</h2>
<p>Beyond entertainment, puzzle games offer genuine cognitive benefits. Regular play can improve short-term memory, concentration, and problem-solving speed. They are also a great low-stress break activity during a busy day.</p>

<h2>Play Free Puzzle Games Online at AZ Games</h2>
<p>Browse hundreds of free puzzle games on the <a href="/category/puzzle-games">Puzzle Games page</a> — all run directly in your browser, no download needed.</p>
`,

  'casual-games': `
<p>Casual games are defined by their accessibility: easy to learn, quick to play, yet hard to put down. They are the perfect companion for a five-minute break or a lazy Sunday afternoon. No complex tutorials, no demanding skill floors — just instant fun.</p>

<h2>What Are Casual Browser Games?</h2>
<p>Casual games include a wide range of styles — endless runners, hyper-casual mobile ports, simple skill games, and light strategy titles. The unifying feature is low entry barrier and high replayability. You can return to a casual game after days away and immediately know what to do.</p>

<h2>Most Popular Casual Game Types</h2>
<ul>
  <li><strong>Endless runners</strong> — run, jump, and slide forever while obstacles scrolls toward you.</li>
  <li><strong>Skill/reflex games</strong> — test your reaction time with simple but escalating challenges.</li>
  <li><strong>Tower defense</strong> — place units to stop waves of enemies from reaching your base.</li>
  <li><strong>Merge games</strong> — combine matching items to create more powerful ones.</li>
</ul>

<h2>Play Free Casual Games Online at AZ Games</h2>
<p>The <a href="/category/casual-games">Casual Games section</a> is the largest category on AZ Games with hundreds of titles ready to play instantly — no account, no download, just fun.</p>
`,

  'kids-games': `
<p>Children deserve games that are safe, age-appropriate, and genuinely fun. Free browser kids games tick all three boxes — they run on any device, require no downloads or accounts, and are carefully selected for younger audiences.</p>

<h2>What to Look for in Kids Browser Games</h2>
<ul>
  <li><strong>Age-appropriate content</strong> — no violence, adult themes, or scary imagery.</li>
  <li><strong>Simple controls</strong> — mouse clicks or arrow keys, easy for young fingers.</li>
  <li><strong>Educational value</strong> — many kids games sneak in counting, letter recognition, or color matching.</li>
  <li><strong>Short sessions</strong> — levels that complete in 1–3 minutes to match a child's attention span.</li>
</ul>

<h2>Types of Free Kids Games at AZ Games</h2>
<ul>
  <li><strong>Coloring games</strong> — fill shapes with colors and create digital artwork.</li>
  <li><strong>Matching games</strong> — find pairs of cards or match objects by category.</li>
  <li><strong>Friendly platformers</strong> — hop over obstacles in a cheerful, non-violent world.</li>
  <li><strong>Mini-games collections</strong> — variety packs of short, fun challenges.</li>
</ul>

<h2>Play Free Kids Games Online at AZ Games</h2>
<p>Every game in our <a href="/category/kids-games">Kids Games collection</a> is free, safe, and playable immediately in any browser — no download, no account, no in-app purchases.</p>
`
};

// ── Build blog post pages ──────────────────────────────────────────────────
for (const post of blogData.posts) {
  const cat       = catMap[post.category] || { slug: 'casual-games', name: 'Casual Games' };
  const body      = ARTICLE_BODIES[post.category] || `<p>Coming soon.</p>`;
  const catGames  = games.filter(g => g.category === post.category).slice(0, 6);

  // Related games section
  const relatedHtml = catGames.length > 0 ? `
<h2>Play These ${escHtml(cat.name)} Right Now</h2>
<div class="blog-related-games">
  ${catGames.map(g => `
  <a class="game-card" href="/play/${g.slug}" aria-label="Play ${escAttr(g.title)}">
    <img src="${escAttr(g.thumbnail)}" alt="${escAttr(g.title)}" loading="lazy" width="180" height="135">
    <span class="game-card-label">${escHtml(g.title)}</span>
  </a>`).join('')}
</div>
` : '';

  const postContent = postTemplate
    .replace(/\{\{POST_H1\}\}/g,             escHtml(post.h1))
    .replace(/\{\{POST_DATE\}\}/g,           post.date)
    .replace(/\{\{POST_CATEGORY_SLUG\}\}/g,  cat.slug)
    .replace(/\{\{POST_CATEGORY_NAME\}\}/g,  escHtml(cat.name))
    .replace(/\{\{POST_BODY\}\}/g,           body + relatedHtml);

  const schema = buildSchema([
    {
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Home', item: `${site.domain}/` },
        { '@type': 'ListItem', position: 2, name: 'Blog', item: `${site.domain}/blog.html` },
        { '@type': 'ListItem', position: 3, name: post.h1, item: post.canonical }
      ]
    },
    { '@context': 'https://schema.org', '@type': 'BlogPosting',
      headline: post.h1, description: post.description,
      url: post.canonical, datePublished: post.date,
      mainEntityOfPage: post.canonical,
      author: { '@type': 'Organization', name: site.name, url: site.domain + '/' },
      publisher: { '@type': 'Organization', name: site.name, url: site.domain + '/' }
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

  const html = render(baseTemplate, {
    title: withBrand(post.title), description: post.description,
    keywords: post.keywords, canonical: post.canonical,
    robotsMeta: robotsMeta(true),
    ogTitle: withBrand(post.title), ogDescription: post.description,
    ogUrl: post.canonical, ogType: 'article',
    ogImage: site.faviconUrl,
    twitterCard: 'summary_large_image', twitterTitle: withBrand(post.title),
    twitterDescription: post.description, twitterImage: site.faviconUrl,
    bodyClass: 'blog-post-page',
    schema, content: postContent
  });

  fs.writeFileSync(path.join(distBlogDir, `${post.slug}.html`), html, 'utf8');
  console.log(`Built: dist/blog/${post.slug}.html`);
}

// ── Build blog index page ──────────────────────────────────────────────────
const postsHtml = blogData.posts.map(post => {
  const cat = catMap[post.category] || { slug: 'casual-games', name: 'Casual Games', emoji: '🎮' };
  return `<a class="blog-card" href="/blog/${post.slug}.html">
  <div class="blog-card-meta">
    <span class="blog-card-cat">${cat.emoji} ${escHtml(cat.name)}</span>
    <span class="blog-card-date">${post.date}</span>
  </div>
  <h2 class="blog-card-title">${escHtml(post.h1)}</h2>
  <p class="blog-card-desc">${escHtml(post.description)}</p>
</a>`;
}).join('\n');

const indexFull = indexContent.replace('{{BLOG_POSTS_HTML}}', postsHtml);

const blogIdxSchema = buildSchema([
  { '@context': 'https://schema.org', '@type': 'Blog',
    name: 'AZ Games by Poki2 Blog', url: blogData.index.canonical,
    description: blogData.index.description,
    publisher: { '@type': 'Organization', name: site.name, url: site.domain + '/' }
  },
  {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home', item: `${site.domain}/` },
      { '@type': 'ListItem', position: 2, name: 'Blog', item: blogData.index.canonical }
    ]
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

const idxHtml = render(baseTemplate, {
  title: withBrand(blogData.index.title), description: blogData.index.description,
  keywords: blogData.index.keywords, canonical: blogData.index.canonical,
  robotsMeta: robotsMeta(true),
  ogTitle: withBrand(blogData.index.title), ogDescription: blogData.index.description,
  ogUrl: blogData.index.canonical, ogType: 'website',
  ogImage: site.faviconUrl,
  twitterCard: 'summary_large_image', twitterTitle: withBrand(blogData.index.title),
  twitterDescription: blogData.index.description, twitterImage: site.faviconUrl,
  bodyClass: blogData.index.bodyClass,
  schema: blogIdxSchema, content: indexFull
});

fs.writeFileSync(path.join(distDir, 'blog.html'), idxHtml, 'utf8');
console.log('Built: dist/blog.html');
console.log(`\nBlog build complete: ${blogData.posts.length} posts + index.`);

// ── Helpers ────────────────────────────────────────────────────────────────
function render(template, p) {
  return template
    .replace(/\{\{TITLE\}\}/g,              escAttr(p.title))
    .replace(/\{\{DESCRIPTION\}\}/g,         escAttr(p.description))
    .replace(/\{\{KEYWORDS\}\}/g,            escAttr(p.keywords || ''))
    .replace(/\{\{CANONICAL\}\}/g,           escAttr(p.canonical))
    .replace(/\{\{ROBOTS_META\}\}/g,         p.robotsMeta)
    .replace(/\{\{OG_TITLE\}\}/g,            escAttr(p.ogTitle))
    .replace(/\{\{OG_DESCRIPTION\}\}/g,      escAttr(p.ogDescription))
    .replace(/\{\{OG_URL\}\}/g,              escAttr(p.ogUrl))
    .replace(/\{\{OG_TYPE\}\}/g,             escAttr(p.ogType))
    .replace(/\{\{OG_IMAGE\}\}/g,            escAttr(p.ogImage))
    .replace(/\{\{TWITTER_CARD\}\}/g,        escAttr(p.twitterCard))
    .replace(/\{\{TWITTER_TITLE\}\}/g,       escAttr(p.twitterTitle))
    .replace(/\{\{TWITTER_DESCRIPTION\}\}/g, escAttr(p.twitterDescription))
    .replace(/\{\{TWITTER_IMAGE\}\}/g,       escAttr(p.twitterImage))
    .replace(/\{\{BODY_CLASS\}\}/g,          escAttr(p.bodyClass))
    .replace(/\{\{SCHEMA\}\}/g,              p.schema)
    .replace(/\{\{CONTENT\}\}/g,             p.content);
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
  return String(str).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function escHtml(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
