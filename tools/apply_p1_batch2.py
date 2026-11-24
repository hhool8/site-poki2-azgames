#!/usr/bin/env python3
"""
apply_p1_batch2.py -- P1 batch 2.

Scope:
  a) 2 quality fixes: `wacky-steps` and `geometry-dash` shipped a truncated
     half-sentence as their intro (visible mid-clause cut at "Wacky" /
     "surviving and"). Both have Bing impressions.
  b) 19 Clicker Games entries whose `short` was a verbatim copy of azgames.io.

Deliberately NOT rewritten: `escape-jump` and `idle-gold-miner`. Their source
descriptions are themselves wrong (they describe Escape Road and Idle Miner
Tycoon respectively). Rewriting them would only relabel a data defect, so they
stay flagged for manual verification instead.

Usage:
    python3 tools/apply_p1_batch2.py          # dry run
    python3 tools/apply_p1_batch2.py --apply  # write data/catalog.json
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "data" / "catalog.json"
BACKUP = ROOT / "data" / ".catalog-pre-p1-batch2.json"

REWRITES: dict[str, str] = {
    # --- truncated-intro fixes ---
    "wacky-steps":
        "Wacky Steps is a ragdoll walking challenge: every step down the street "
        "is a timing test, and one mistimed move sends the character tumbling.",
    "geometry-dash":
        "Geometry Dash is a rhythm platformer on rails: one square, one jump "
        "button, and a level that punishes every mistimed tap.",

    # --- Clicker Games (verbatim copies) ---
    "bombardino-crocodilo-clicker":
        "Bombardino Crocodilo Clicker is an Italian-brainrot meme clicker: tap "
        "the crocodile, bank the coins, and push the numbers up.",
    "chicken-jockey-clicker":
        "Chicken Jockey Clicker is idle clicking with upgrades: earn points per "
        "tap, then spend them on boosts that make every later tap worth more.",
    "chill-clicker":
        "Chill Clicker is the quiet end of the genre: a capybara, slow progress, "
        "and small tasks that advance while you click at your own pace.",
    "chill-guy-clicker":
        "Chill Guy Clicker turns the deadpan dog meme into an idle loop: tap for "
        "points, unlock upgrades, and let the counter climb.",
    "chill-guy-clicker-3d":
        "Chill Guy Clicker 3D puts the same relaxed tapping into a 3D scene — "
        "click the chill guy, collect points, and unwind.",
    "cookie-clicker":
        "Cookie Clicker is the reference point for the genre: click the cookie, "
        "buy buildings that click for you, and watch production compound.",
    "god-simulator":
        "God Simulator treats religion as a strategy loop: found a faith, spread "
        "it across the map, and grow it until the world follows.",
    "goo-goo-gaga-clicker":
        "Goo Goo Gaga Clicker is meme idle clicking: tap fast, buy upgrades, and "
        "unlock the strange Goo Goo Gaga skins as the total rises.",
    "italian-brainrot-clicker-2":
        "Italian Brainrot Clicker 2 gathers Tralalero Tralala, Tung Tung Tung "
        "Sahur and more: click the cast, bank points, spend them on upgrades.",
    "labubu-clicker":
        "Labubu Clicker is idle tapping built around the Labubu character: click "
        "to earn, unlock upgrades, and let the points accumulate.",
    "lizard-lizard-clicker":
        "Lizard Lizard Clicker asks for two things — clicks and upgrades: earn "
        "points per tap, then reinvest to meet the stranger lizards.",
    "planet-buster":
        "Planet Buster goes idle in space: launch missiles at planets across the "
        "galaxy, upgrade the arsenal, and clear one world after another.",
    "sprunki-clicker":
        "Sprunki Clicker is an endless idle loop around one character: tap for "
        "points and unlock upgrade paths that keep the numbers moving.",
    "supermarket-master":
        "Supermarket Master is retail management rather than pure clicking: open "
        "stores, expand departments, and draw in customers until the chain grows.",
    "tap-rich-idle":
        "Tap Rich Idle starts from nothing: each tap adds wealth, upgrades turn "
        "taps into income, and the business compounds while you watch.",
    "titans-clicker":
        "Titans Clicker casts you as the hero against giants: fight the Titans "
        "head-on and turn each victory into the next upgrade.",
    "tralalero-tralala-clicker":
        "Tralalero Tralala Clicker follows the shark in blue sneakers: click for "
        "points, unlock upgrades, and collect the alternate skins.",
    "tung-sahur-clicker":
        "Tung Sahur Clicker is a Ramadan-themed tapper: wake the village before "
        "dawn, tap fast, and climb toward the Galactic Sahur rank.",
    "unchill-guy-clicker":
        "Unchill Guy Clicker flips the meme: the grumpy version of Chill Guy "
        "wants none of the fun, and every click drags him further in.",
}

FLAGGED_FOR_MANUAL = {
    "escape-jump": "source description describes Escape Road, not Escape Jump",
    "idle-gold-miner": "source description describes Idle Miner Tycoon, not Idle Gold Miner",
}


def main() -> int:
    apply = "--apply" in sys.argv
    catalog = json.loads(CATALOG.read_text())
    games = catalog if isinstance(catalog, list) else catalog["games"]
    by_slug = {g["slug"]: g for g in games}

    missing = [s for s in REWRITES if s not in by_slug]
    if missing:
        print(f"ERROR: slugs not in catalog: {missing}")
        return 1

    for slug, new in REWRITES.items():
        old = by_slug[slug]["short"]
        print(f"--- {slug}")
        print(f"  old ({len(old.split())}w): {old[:160]}")
        print(f"  new ({len(new.split())}w): {new}")

    if not apply:
        print(f"\nDRY RUN — {len(REWRITES)} rewrites staged. Use --apply to write.")
        print("Flagged for manual verification (not rewritten):")
        for s, why in FLAGGED_FOR_MANUAL.items():
            print(f"  - {s}: {why}")
        return 0

    if not BACKUP.exists():
        shutil.copy2(CATALOG, BACKUP)
        print(f"backup -> {BACKUP.name}")
    for slug, new in REWRITES.items():
        by_slug[slug]["short"] = new
    CATALOG.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")
    print(f"applied: {len(REWRITES)} shorts rewritten.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())