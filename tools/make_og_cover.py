#!/usr/bin/env python3
"""Build the 1200x630 social preview card for azgames.poki2.online.

Dev-only tool: Pillow is required to regenerate the committed PNG, but the
normal CI build only copies `data/og-cover.png` into dist and has no Pillow
dependency. All artwork comes from the site's own game covers; no external
images are fetched.

Usage:
  python3 tools/make_og_cover.py
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = DATA / "og-cover.png"
W, H = 1200, 630
COVERS = ("2048.webp", "tetris.webp", "bitlife.webp", "stickman-hook.webp")
FONT_REGULAR = (
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
)
FONT_BOLD = (
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
)


def font(candidates: tuple[str, ...], size: int) -> ImageFont.FreeTypeFont:
    for path in candidates:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def rounded(image: Image.Image, radius: int) -> Image.Image:
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, image.width - 1, image.height - 1), radius, fill=255)
    image.putalpha(mask)
    return image


def main() -> None:
    catalog = json.loads((DATA / "catalog.json").read_text())
    count = len(catalog["games"])

    card = Image.new("RGB", (W, H), "#0b0b18")
    px = card.load()
    for y in range(H):
        t = y / H
        r = int(11 + 18 * t)
        g = int(11 + 8 * t)
        b = int(24 + 38 * t)
        for x in range(W):
            px[x, y] = (r, g, b)

    draw = ImageDraw.Draw(card, "RGBA")
    draw.ellipse((-180, -260, 520, 440), fill=(168, 85, 247, 28))
    draw.ellipse((760, 360, 1420, 920), fill=(56, 189, 248, 20))

    title_font = font(FONT_BOLD, 108)
    sub_font = font(FONT_BOLD, 39)
    body_font = font(FONT_REGULAR, 27)
    small_font = font(FONT_REGULAR, 22)
    badge_font = font(FONT_BOLD, 20)

    draw.text((72, 128), "AZ", font=title_font, fill="#ffffff")
    az_width = draw.textbbox((0, 0), "AZ", font=title_font)[2]
    draw.text((72 + az_width + 20, 128), "Games", font=title_font, fill="#c084fc")
    draw.text((72, 270), f"{count} free browser games", font=sub_font, fill="#e9e9f5")
    draw.text((72, 332), "One click to play. No download, no sign-up.", font=body_font, fill="#b8b8cf")

    badge = "FREE  ·  INSTANT PLAY"
    bb = draw.textbbox((0, 0), badge, font=badge_font)
    bw, bh = bb[2] - bb[0], bb[3] - bb[1]
    draw.rounded_rectangle((72, 398, 72 + bw + 40, 398 + bh + 28), 18, fill=(168, 85, 247, 46))
    draw.text((92, 410), badge, font=badge_font, fill="#d8b4fe")
    draw.text((72, 540), "azgames.poki2.online", font=small_font, fill="#8080a0")

    cell, gap, ox, oy = 230, 22, 690, 82
    for i, name in enumerate(COVERS):
        source = DATA / "img" / name
        if not source.is_file():
            raise SystemExit(f"missing site cover: {source}")
        with Image.open(source) as raw:
            cover = ImageOps.fit(raw.convert("RGB"), (cell, cell), method=Image.Resampling.LANCZOS)
        cover = rounded(cover, 20)
        x = ox + (i % 2) * (cell + gap)
        y = oy + (i // 2) * (cell + gap)
        card.paste(cover, (x, y), cover)
        draw.rounded_rectangle((x, y, x + cell - 1, y + cell - 1), 20, outline=(255, 255, 255, 36), width=2)

    card.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT.relative_to(ROOT)}: {card.width}x{card.height}, {OUT.stat().st_size} bytes, {count} games")


if __name__ == "__main__":
    main()
