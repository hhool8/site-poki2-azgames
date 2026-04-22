#!/usr/bin/env python3
"""
Download 35 missing game thumbnails from azgames.io using DrissionPage
(uses real Chrome to bypass Cloudflare challenge).
"""

import os
import time
from pathlib import Path

from DrissionPage import ChromiumPage, ChromiumOptions

ROOT = Path(__file__).parent.parent
OUT_DIR = ROOT / "public/images/games"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MISSING = {
    "age-of-war":              "https://azgames.io/upload/imgs/ageofwar.jpg",
    "bottle-jump":             "https://azgames.io/upload/imgs/bottlejump2.png",
    "bounce-path":             "https://azgames.io/upload/imgs/bouncepath1.png",
    "bounce-up":               "https://azgames.io/upload/imgs/bounceup3.png",
    "chicken-flip":            "https://azgames.io/upload/imgs/chickenflip4.png",
    "color-jump":              "https://azgames.io/upload/imgs/colorjump3.png",
    "crazy-bull-city":         "https://azgames.io/upload/imgs/crazybullcity1.png",
    "cuby-road-halloween":     "https://azgames.io/upload/imgs/cubyroadhalloween.png",
    "dino-dash-3d":            "https://azgames.io/upload/imgs/dinodash3d1.png",
    "duck-life":               "https://azgames.io/upload/imgs/ducklife.png",
    "escape-bear":             "https://azgames.io/upload/imgs/escapebear.png",
    "flamy-dash":              "https://azgames.io/upload/imgs/flamydash3.png",
    "flying-kong":             "https://azgames.io/upload/imgs/flyingkong1.png",
    "forest-mouse":            "https://azgames.io/upload/imgs/forestmouse.png",
    "hill-climb-race":         "https://azgames.io/upload/imgs/thumbnail-512.png",
    "loot-and-scoot":          "https://azgames.io/upload/imgs/lootandscoot3.png",
    "madness-lab":             "https://azgames.io/upload/imgs/madnesslab3.png",
    "mamas-cookeria":          "https://azgames.io/upload/imgs/mamascookeria3.png",
    "neon-leap":               "https://azgames.io/upload/imgs/neonleap3.png",
    "omnom-jump":              "https://azgames.io/upload/imgs/omnomjump11.png",
    "orbit-dash":              "https://azgames.io/upload/imgs/orbitdash.png",
    "pacman-30th-anniversary": "https://azgames.io/upload/imgs/pacman.jpg",
    "papas-freezeria":         "https://azgames.io/upload/imgs/papasfreezeria.png",
    "red-rush":                "https://azgames.io/upload/imgs/redrush2.png",
    "santa-run":               "https://azgames.io/upload/imgs/santarun3.png",
    "sprunki-jump":            "https://azgames.io/upload/imgs/sprunkijump.png",
    "stickman-slash":          "https://azgames.io/upload/imgs/stickmanslash3.png",
    "tap-road-beat":           "https://azgames.io/upload/imgs/taproadbeat2.png",
    "tap-rush":                "https://azgames.io/upload/imgs/taprush2.png",
    "wacky-nursery-2":         "https://azgames.io/upload/imgs/wackynursery23.png",
    "wyrmdash":                "https://azgames.io/upload/imgs/wyrmdash.png",
    "ziggy-road":              "https://azgames.io/upload/imgs/ziggyroad1.png",
}


def main():
    co = ChromiumOptions()
    co.headless(False)  # visible browser to bypass CF challenge
    page = ChromiumPage(addr_or_opts=co)

    # Step 1: warm up on azgames.io to pass CF challenge
    print("Warming up on azgames.io ...")
    page.get("https://azgames.io/")
    time.sleep(5)  # wait for CF JS challenge
    print(f"Title: {page.title}")

    ok = 0
    fail = 0
    failed = []

    for slug, url in MISSING.items():
        ext = url.rsplit(".", 1)[-1]
        out_path = OUT_DIR / f"{slug}.{ext}"

        if out_path.exists() and out_path.stat().st_size > 1024:
            print(f"SKIP: {slug} already exists")
            ok += 1
            continue

        # Navigate directly to the image URL
        try:
            page.get(url)
            time.sleep(1)

            # Get image bytes via JS canvas trick
            img_bytes = page.run_js("""
                return new Promise((resolve, reject) => {
                    const img = document.querySelector('img') || document.body.firstChild;
                    if (!img || img.tagName !== 'IMG') {
                        // Try document body as image
                        fetch(location.href)
                            .then(r => r.arrayBuffer())
                            .then(buf => {
                                const bytes = Array.from(new Uint8Array(buf));
                                resolve(bytes);
                            }).catch(reject);
                        return;
                    }
                    const canvas = document.createElement('canvas');
                    canvas.width = img.naturalWidth || img.width;
                    canvas.height = img.naturalHeight || img.height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0);
                    canvas.toBlob(blob => {
                        blob.arrayBuffer().then(buf => {
                            resolve(Array.from(new Uint8Array(buf)));
                        });
                    }, 'image/png');
                });
            """, timeout=15)

            if img_bytes and len(img_bytes) > 500:
                out_path.write_bytes(bytes(img_bytes))
                ok += 1
                print(f"OK [{ok}]: {slug}.{ext} ({len(img_bytes)} bytes)")
            else:
                # Fallback: direct fetch via requests using cookies from browser
                cookies = {c['name']: c['value'] for c in page.cookies()}
                import requests
                headers = {
                    'Referer': 'https://azgames.io/',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                }
                r = requests.get(url, headers=headers, cookies=cookies, timeout=15)
                ct = r.headers.get('content-type', '')
                if r.status_code == 200 and 'image' in ct and len(r.content) > 500:
                    out_path.write_bytes(r.content)
                    ok += 1
                    print(f"OK-REQ [{ok}]: {slug}.{ext} ({len(r.content)} bytes)")
                else:
                    fail += 1
                    failed.append(slug)
                    print(f"FAIL: {slug} status={r.status_code} ct={ct} size={len(r.content)}")

        except Exception as e:
            fail += 1
            failed.append(slug)
            print(f"ERR: {slug} — {e}")

    page.quit()
    print(f"\nDone. OK: {ok}, Failed: {fail}")
    if failed:
        print("Failed:", ", ".join(failed))


if __name__ == "__main__":
    main()
