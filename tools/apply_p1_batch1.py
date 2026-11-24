#!/usr/bin/env python3
"""
apply_p1_batch1.py -- P1 batch 1: rewrite verbatim-copied intro sentences.

Scope: the 11 games whose `short` field was a verbatim copy of the
azgames.io meta description AND that carry real Bing search impressions
(Bing WMT page stats 2026-11-24, see sidecar report
07-measure/azgames-dedup-selfcheck-2026-11-24.md).

Rules for the new shorts:
- 18-30 words, fact-based on the game itself (facts from the catalog and
  public knowledge of each title), wording fully re-written.
- No two intros share an opening pattern; no template suffixes.
- Since commit f93d2d1 the page intro AND the meta description both derive
  from this field at build time.

Usage:
    python3 tools/apply_p1_batch1.py          # dry run, prints diffs
    python3 tools/apply_p1_batch1.py --apply  # writes data/catalog.json
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "data" / "catalog.json"
BACKUP = ROOT / "data" / ".catalog-pre-p1-batch1.json"

REWRITES: dict[str, str] = {
    "fish-it-online":
        "Fish It Online rewards patient timing: read the water, cast at the "
        "right moment, and hook bigger, rarer fish than a hurried cast would "
        "ever land.",
    "escape-tsunami-brainrots-online":
        "Escape Tsunami Brainrots Online runs two clocks at once — collect "
        "the rarest Brainrots to grow your hoard while the tsunami timer "
        "keeps you moving.",
    "merge-infinity":
        "Merge Infinity stretches the 2048 idea across a grid of lines: "
        "connect matching numbers, chain the merges, and watch the totals "
        "climb past every previous run.",
    "wacky-flip":
        "Wacky Flip turns a run-up into a physics puzzle: time the jump, "
        "hold the flip, and stick the landing — ragdoll physics make every "
        "miss worth watching.",
    "run-3":
        "Run 3 sends a small grey alien along floating space corridors: "
        "jump the gaps, avoid the missing floor, and let the level reroute "
        "beneath your feet.",
    "jetski-race":
        "Jetski Race is arcade water racing: skim across the waves, chain "
        "flips for extra speed, and weave past obstacles on the run to the "
        "finish line.",
    "glide-in":
        "Glide In packs quick aim puzzles into one puck: pull back, read "
        "each hazard, and release so the puck lands in the hole instead of "
        "the trap.",
    "arcade-volley":
        "Arcade Volley keeps volleyball lean: quick matches across "
        "different courts, one well-timed spike at a time, and every rally "
        "ends before the ball drops.",
    "crossy-road":
        "Crossy Road gives its chicken one job — cross again. Cars, rivers "
        "and trees line each hop forward, and every one of them can end "
        "the run.",
    "kitten-defense":
        "Kitten Defense hands the turf to fierce cats: time your attacks, "
        "hold back waves of odd attackers, and keep the cat kingdom "
        "standing.",
    "duck-clicker":
        "Duck Clicker is tapping with a hook: each click earns a reward, "
        "rewards hatch more ducks, and the growing flock keeps the numbers "
        "climbing.",
}


def main() -> int:
    apply = "--apply" in sys.argv
    catalog = json.loads(CATALOG.read_text())
    games = catalog if isinstance(catalog, list) else catalog["games"]

    missing = [s for s in REWRITES if s not in {g["slug"] for g in games}]
    if missing:
        print(f"ERROR: slugs not in catalog: {missing}")
        return 1

    changed = 0
    for g in games:
        slug = g["slug"]
        if slug not in REWRITES:
            continue
        old = g["short"]
        new = REWRITES[slug]
        print(f"--- {slug}")
        print(f"  old ({len(old.split())}w): {old}")
        print(f"  new ({len(new.split())}w): {new}")
        if apply:
            g["short"] = new
            changed += 1

    if not apply:
        print("\nDRY RUN — rerun with --apply to write changes.")
        return 0

    if BACKUP.exists() is False:
        shutil.copy2(CATALOG, BACKUP)
        print(f"backup -> {BACKUP.name}")
    CATALOG.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")
    print(f"applied: {changed}/{len(REWRITES)} shorts rewritten.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
