'use strict';
/**
 * Download the 35 remaining game thumbnails using Playwright browser fetch
 * (bypasses Cloudflare JS challenge by loading site first and fetching images in-page).
 */

const fs   = require('fs');
const path = require('path');

const ROOT    = path.join(__dirname, '..');
const OUT_DIR = path.join(ROOT, 'public/images/games');
fs.mkdirSync(OUT_DIR, { recursive: true });

const { chromium } = require('playwright');

// The 35 missing games: slug -> remote URL
const MISSING = {
  'age-of-war':           'https://azgames.io/upload/imgs/ageofwar.jpg',
  'bitlife':              'https://azgames.io/upload/imgs/bitlifegamebanner1.png',
  'bottle-jump':          'https://azgames.io/upload/imgs/bottlejump2.png',
  'bounce-path':          'https://azgames.io/upload/imgs/bouncepath1.png',
  'bounce-up':            'https://azgames.io/upload/imgs/bounceup3.png',
  'chicken-flip':         'https://azgames.io/upload/imgs/chickenflip4.png',
  'color-jump':           'https://azgames.io/upload/imgs/colorjump3.png',
  'crazy-bull-city':      'https://azgames.io/upload/imgs/crazybullcity1.png',
  'crossy-road':          'https://azgames.io/upload/imgs/crossyroad1.png',
  'cuby-road-halloween':  'https://azgames.io/upload/imgs/cubyroadhalloween.png',
  'dino-dash-3d':         'https://azgames.io/upload/imgs/dinodash3d1.png',
  'duck-life':            'https://azgames.io/upload/imgs/ducklife.png',
  'escape-bear':          'https://azgames.io/upload/imgs/escapebear.png',
  'flamy-dash':           'https://azgames.io/upload/imgs/flamydash3.png',
  'flying-kong':          'https://azgames.io/upload/imgs/flyingkong1.png',
  'forest-mouse':         'https://azgames.io/upload/imgs/forestmouse.png',
  'hill-climb-race':      'https://azgames.io/upload/imgs/thumbnail-512.png',
  'loot-and-scoot':       'https://azgames.io/upload/imgs/lootandscoot3.png',
  'madness-lab':          'https://azgames.io/upload/imgs/madnesslab3.png',
  'mamas-cookeria':       'https://azgames.io/upload/imgs/mamascookeria3.png',
  'neon-leap':            'https://azgames.io/upload/imgs/neonleap3.png',
  'omnom-jump':           'https://azgames.io/upload/imgs/omnomjump11.png',
  'orbit-dash':           'https://azgames.io/upload/imgs/orbitdash.png',
  'pacman-30th-anniversary': 'https://azgames.io/upload/imgs/pacman.jpg',
  'papas-freezeria':      'https://azgames.io/upload/imgs/papasfreezeria.png',
  'red-rush':             'https://azgames.io/upload/imgs/redrush2.png',
  'santa-run':            'https://azgames.io/upload/imgs/santarun3.png',
  'sprunki-jump':         'https://azgames.io/upload/imgs/sprunkijump.png',
  'stickman-slash':       'https://azgames.io/upload/imgs/stickmanslash3.png',
  'tap-road-beat':        'https://azgames.io/upload/imgs/taproadbeat2.png',
  'tap-rush':             'https://azgames.io/upload/imgs/taprush2.png',
  'tiny-fishing':         'https://azgames.io/upload/imgs/tinyfishing.jpg',
  'wacky-nursery-2':      'https://azgames.io/upload/imgs/wackynursery23.png',
  'wyrmdash':             'https://azgames.io/upload/imgs/wyrmdash.png',
  'ziggy-road':           'https://azgames.io/upload/imgs/ziggyroad1.png',
};

async function main() {
  const browser = await chromium.launch({ headless: false }); // non-headless to bypass CF bot detection
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    extraHTTPHeaders: {
      'Accept-Language': 'en-US,en;q=0.9',
    }
  });

  // Step 1: visit a game page to solve CF challenge and get cookies
  const warmSlug = Object.keys(MISSING)[0];
  console.log(`Warming up: visiting azgames.io/${warmSlug} ...`);
  const warmPage = await context.newPage();
  try {
    await warmPage.goto(`https://azgames.io/${warmSlug}`, { waitUntil: 'domcontentloaded', timeout: 45000 });
    // Wait for CF challenge to resolve
    await warmPage.waitForTimeout(5000);
    const title = await warmPage.title();
    console.log('Game page title:', title);
  } catch (e) {
    console.warn('Warm-up warning:', e.message);
  }
  await warmPage.close();

  let ok = 0, fail = 0;
  const failed = [];

  for (const [slug, url] of Object.entries(MISSING)) {
    const ext = url.split('.').pop();
    const outPath = path.join(OUT_DIR, `${slug}.${ext}`);
    if (fs.existsSync(outPath) && fs.statSync(outPath).size > 1024) {
      console.log(`SKIP: ${slug} already exists`);
      ok++;
      continue;
    }

    // Navigate directly to image URL — uses cookies from warm-up
    const page = await context.newPage();
    let imgBuf = null;
    page.on('response', async (response) => {
      if (response.url() === url && response.ok()) {
        try { imgBuf = await response.body(); } catch (_) {}
      }
    });
    try {
      const resp = await page.goto(url, { waitUntil: 'load', timeout: 20000 });
      await page.waitForTimeout(1000);
      if (!imgBuf && resp && resp.ok()) {
        imgBuf = await resp.body();
      }
      if (imgBuf && imgBuf.length > 500) {
        fs.writeFileSync(outPath, imgBuf);
        ok++;
        console.log(`OK [${ok}]: ${slug}.${ext} (${imgBuf.length} bytes)`);
      } else {
        const status = resp ? resp.status() : '?';
        fail++;
        failed.push(slug);
        console.warn(`FAIL HTTP ${status}: ${slug} (buf=${imgBuf ? imgBuf.length : 0} bytes)`);
      }
    } catch (e) {
      fail++;
      failed.push(slug);
      console.warn(`ERR: ${slug} — ${e.message}`);
    } finally {
      await page.close();
    }
  }

  await browser.close();
  console.log(`\nDone. OK: ${ok}, Failed: ${fail}`);
  if (failed.length) console.log('Failed slugs:', failed.join(', '));
}

main().catch(e => { console.error(e); process.exit(1); });
