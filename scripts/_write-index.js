'use strict';
const fs = require('fs');
const path = require('path');
const OUT = path.join(__dirname, '../src/content/index.html');
const content = `<section class="homepage-rows">
  <div class="container">
    {{HOMEPAGE_GAME_ROWS}}
  </div>
</section>

<section class="features">
  <div class="container">
    <h2>Why AZ Games?</h2>
    <p class="section-sub">Fast, free, and ready to play wherever you are.</p>
    <div class="feature-grid">
      <div class="feature-card">
        <span class="feature-icon">&#x26A1;</span>
        <p class="feature-title">Instant Play</p>
        <p>No downloads, no installs. Click a game and it loads in your browser within seconds.</p>
      </div>
      <div class="feature-card">
        <span class="feature-icon">&#x1F193;</span>
        <p class="feature-title">Always Free</p>
        <p>Every game on AZ Games is 100% free. No paywalls, no subscriptions, no hidden fees.</p>
      </div>
      <div class="feature-card">
        <span class="feature-icon">&#x1F512;</span>
        <p class="feature-title">No Account Needed</p>
        <p>No sign-up, no email, no tracking. Just visit and play.</p>
      </div>
      <div class="feature-card">
        <span class="feature-icon">&#x1F4F1;</span>
        <p class="feature-title">Works Everywhere</p>
        <p>Play on desktop, laptop, tablet or phone. Most games support touch input.</p>
      </div>
    </div>
  </div>
</section>

<section class="faq">
  <div class="container">
    <h2>Frequently Asked Questions</h2>
    <p class="section-sub">Everything you need to know about AZ Games.</p>
    <details class="faq-item">
      <summary>What is AZ Games?</summary>
      <p>AZ Games is a free online gaming hub featuring 300+ browser games across 10 categories including clicker, IO, adventure, shooting, sports, car, puzzle, casual and kids games &mdash; playable without any download or login.</p>
    </details>
    <details class="faq-item">
      <summary>Are all games on AZ Games free?</summary>
      <p>Yes &mdash; every single game is completely free to play. The site is supported by advertising.</p>
    </details>
    <details class="faq-item">
      <summary>Do I need to create an account?</summary>
      <p>No account required. Visit the site, pick a game, and start playing immediately.</p>
    </details>
    <details class="faq-item">
      <summary>Do the games work on mobile?</summary>
      <p>Most games support touch input and work on smartphones and tablets.</p>
    </details>
    <details class="faq-item">
      <summary>Can I play AZ Games at school or work?</summary>
      <p>AZ Games runs entirely in your browser. Access depends on your network filtering rules.</p>
    </details>
  </div>
</section>

<section class="seo-intro">
  <div class="container">
    <h2>AZ Games: Your Free A-to-Z Online Gaming Destination</h2>
    <p>Welcome to <strong>AZ Games</strong> &mdash; a carefully curated library of <strong>300+ free browser games</strong> spanning every major genre. Whether you are into fast-paced <a href="/category/clicker-games.html">clicker games</a>, competitive <a href="/category/io-games.html">.IO multiplayer games</a>, story-driven <a href="/category/adventure-games.html">adventure games</a>, or relaxing <a href="/category/puzzle-games.html">puzzle games</a>, you will find something here in seconds &mdash; zero downloads, zero sign-ups.</p>
    <p>All games run natively in your web browser using modern HTML5 technology. Works on Windows, Mac, Chromebook, iOS, and Android.</p>
  </div>
</section>

<section class="seo-section">
  <div class="container">
    <h2>Browse All 10 Online Game Categories</h2>
    <ul class="seo-list">
      <li><strong><a href="/category/clicker-games.html">Clicker Games</a></strong> &mdash; Satisfying incremental and idle games where every click counts.</li>
      <li><strong><a href="/category/io-games.html">.IO Games</a></strong> &mdash; Lightweight multiplayer browser games. Compete in real time &mdash; no login needed.</li>
      <li><strong><a href="/category/adventure-games.html">Adventure Games</a></strong> &mdash; Explore worlds, solve puzzles, and defeat enemies in platformers and RPG-lite adventures.</li>
      <li><strong><a href="/category/2-player-games.html">2 Player Games</a></strong> &mdash; Play head-to-head with a friend on the same device.</li>
      <li><strong><a href="/category/shooting-games.html">Shooting Games</a></strong> &mdash; First-person shooters, top-down blasters, and aim-trainers.</li>
      <li><strong><a href="/category/sports-games.html">Sports Games</a></strong> &mdash; Basketball, soccer, golf, and athletics &mdash; all playable in your browser.</li>
      <li><strong><a href="/category/car-games.html">Car Games</a></strong> &mdash; Drift, race, and stunt your way through dozens of driving challenges.</li>
      <li><strong><a href="/category/puzzle-games.html">Puzzle Games</a></strong> &mdash; Brain teasers, match-3, word games, and logic puzzles for all skill levels.</li>
      <li><strong><a href="/category/casual-games.html">Casual Games</a></strong> &mdash; Easy to pick up, hard to put down. Hundreds of quick-session favourites.</li>
      <li><strong><a href="/category/kids-games.html">Kids Games</a></strong> &mdash; Age-appropriate fun for younger players.</li>
    </ul>
  </div>
</section>
`;
fs.writeFileSync(OUT, content, 'utf8');
console.log('Written', fs.statSync(OUT).size, 'bytes to', OUT);
