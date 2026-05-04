'use strict';
/**
 * Regenerates all favicon PNGs and favicon.ico from public/favicon.svg
 */

const sharp = require('sharp');
const toIco = require('to-ico');
const fs    = require('fs');
const path  = require('path');

const PUB = path.join(__dirname, '..', 'public');
const SVG = fs.readFileSync(path.join(PUB, 'favicon.svg'));

async function renderPng(size) {
  return sharp(SVG).resize(size, size).png().toBuffer();
}

async function main() {
  const sizes = [16, 32, 48, 180, 192, 512];
  const buffers = {};
  for (const s of sizes) buffers[s] = await renderPng(s);

  const pngMap = {
    'favicon-16.png':       buffers[16],
    'favicon-32.png':       buffers[32],
    'favicon-48.png':       buffers[48],
    'favicon-192.png':      buffers[192],
    'favicon-512.png':      buffers[512],
    'apple-touch-icon.png': buffers[180],
  };

  for (const [name, buf] of Object.entries(pngMap)) {
    fs.writeFileSync(path.join(PUB, name), buf);
    console.log(`  ✓ ${name} (${buf.length} bytes)`);
  }

  const ico = await toIco([buffers[16], buffers[32], buffers[48]]);
  fs.writeFileSync(path.join(PUB, 'favicon.ico'), ico);
  console.log(`  ✓ favicon.ico (${ico.length} bytes)`);
  console.log('Done.');
}

main().catch(err => { console.error('✗', err.message); process.exit(1); });
