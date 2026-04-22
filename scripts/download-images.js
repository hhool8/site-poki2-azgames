'use strict';
/**
 * Download game thumbnails from azgames.io using Playwright (bypasses Cloudflare challenge).
 * Saves images to public/images/<filename>
 * Usage: npx playwright install chromium && node scripts/download-images.js
 */

const fs   = require('fs');
const path = require('path');

const ROOT      = path.join(__dirname, '..');
const GAMES_FILE = path.join(ROOT, 'src/data/games.json');
const OUT_DIR   = path.join(ROOT, 'public/images');

fs.mkdirSync(OUT_DIR, { recursive: true });

const { chromium } = require('playwright');

async function main() {
  const gamesRaw = JSON.parse(fs.readFileSync(GAMES_FILE, 'utf8'));
  const games = gamesRaw.games || gamesRaw;

  // Collect unique thumbnail URLs (azgames.io only)
  const urlSet = new Set();
  for (const g of games) {
    if (g.thumbnail && g.thumbnail.includes('azgames.io')) {
      urlSet.add(g.thumbnail);
    }
  }
  const urls = [...urlSet];
  console.log(`Found ${urls.length} unique azgames.io thumbnails to download`);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
  });

  // Warm up: visit azgames.io to get cookies/challenge cleared
  const warmPage = await context.newPage();
  console.log('Warming up browser on azgames.io ...');
  try {
    await warmPage.goto('https://azgames.io/', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await warmPage.waitForTimeout(3000);
  } catch (e) {
    console.warn('Warm-up page load warning:', e.message);
  }
  await warmPage.close();

  let ok = 0, fail = 0;

  // Download in batches of 5
  const BATCH = 5;
  for (let i = 0; i < urls.length; i += BATCH) {
    const batch = urls.slice(i, i + BATCH);
    await Promise.all(batch.map(async (url) => {
      const filename = path.basename(url);
      const outPath  = path.join(OUT_DIR, filename);
      if (fs.existsSync(outPath) && fs.statSync(outPath).size > 1024) {
        ok++;
        return; // already downloaded
      }
      const page = await context.newPage();
      try {
        const response = await page.goto(url, { waitUntil: 'load', timeout: 20000 });
        if (response && response.ok()) {
          const buf = await response.body();
          if (buf.length > 500) {
            fs.writeFileSync(outPath, buf);
            ok++;
            console.log(`OK [${ok}/${urls.length}]: ${filename}`);
          } else {
            fail++;
            console.warn(`SMALL [${fail}]: ${filename} (${buf.length} bytes)`);
          }
        } else {
          fail++;
          console.warn(`HTTP ${response?.status()} FAIL: ${filename}`);
        }
      } catch (e) {
        fail++;
        console.warn(`ERR: ${filename} — ${e.message}`);
      } finally {
        await page.close();
      }
    }));
  }

  await browser.close();
  console.log(`\nDone. OK: ${ok}, Failed: ${fail}`);
}

main().catch(e => { console.error(e); process.exit(1); });
