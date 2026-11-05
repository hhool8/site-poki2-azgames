#!/usr/bin/env python3
"""Download the azgames thumbnails and normalise them to 400px WebP.

The source serves 512x512 PNGs (~180 KB each); 291 of those would be a 52 MB
payload for a grid whose largest rendered cell is ~190 CSS px wide. WebP at
400px covers 2x DPR and lands around 20 KB.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ORIGIN = "https://azgames.poki2.online"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/150.0.0.0 Safari/537.36"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "img"
SIZE = 400
QUALITY = "80"


def fetch_bytes(url: str, tries: int = 3) -> bytes:
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read()
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(1.2 * (attempt + 1))
    raise RuntimeError(f"{url}: {last}")


def convert(raw: bytes, dest: Path) -> int:
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "src.bin"
        src.write_bytes(raw)
        png = Path(tmp) / "src.png"
        # sips re-encodes anything it can decode (PNG/JPEG/AVIF/HEIC), which
        # keeps this pipeline from depending on the upload's actual container.
        proc = subprocess.run(
            ["sips", "-s", "format", "png", "-Z", str(SIZE), str(src), "--out", str(png)],
            capture_output=True,
        )
        if proc.returncode != 0 or not png.exists():
            raise RuntimeError("sips: " + proc.stderr.decode()[:160])
        enc = subprocess.run(
            ["cwebp", "-quiet", "-q", QUALITY, str(png), "-o", str(dest)],
            capture_output=True,
        )
        if enc.returncode != 0:
            raise RuntimeError("cwebp: " + enc.stderr.decode()[:160])
    return dest.stat().st_size


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    catalog = json.loads((ROOT / "data" / "catalog.json").read_text())
    games = catalog["games"]
    if args.limit:
        games = games[: args.limit]

    todo = [g for g in games if args.force or not (OUT / f"{g['slug']}.webp").exists()]
    print(f"images: {len(games)} games, {len(todo)} to fetch")
    failures: list[dict] = []

    def work(game: dict) -> None:
        url = game["image"]
        if url.startswith("/"):
            url = ORIGIN + url
        try:
            size = convert(fetch_bytes(url), OUT / f"{game['slug']}.webp")
            if size < 1200:
                raise RuntimeError(f"suspiciously small ({size} B)")
        except Exception as exc:  # noqa: BLE001
            failures.append({"slug": game["slug"], "url": url, "error": str(exc)[:180]})

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for i, _ in enumerate(pool.map(work, todo), 1):
            if i % 40 == 0 or i == len(todo):
                print(f"  {i}/{len(todo)}", flush=True)

    if failures:
        (ROOT / "data" / "img-failures.json").write_text(json.dumps(failures, indent=1))

    total = sum(p.stat().st_size for p in OUT.glob("*.webp"))
    print(f"done: {len(list(OUT.glob('*.webp')))} files, {total / 1e6:.1f} MB, {len(failures)} failures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
