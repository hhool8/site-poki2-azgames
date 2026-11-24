#!/usr/bin/env python3
"""
apply_p1_batch4.py -- P1 batch 4: truncated `short` repair.

Not a dedup batch. Verification of batch 3 surfaced 11 entries whose `short`
stops mid-word, so the page opens with a fragment:

    Mama | Papa | Scary Wheels isn | ...thrilling space journe

Cause: the extractor reads `class="game-info-desc"`; that container no longer
exists on the current azgames.io pages, so these 11 came from an older crawl and
were cut at the apostrophe. The cut strings are shorter than the real sentence,
so they also made every meta description worthless.

Fix: the replacement text is written from the CURRENT source description of each
game (re-fetched 2026-11-24, quoted in SOURCE below), not invented. That is the
difference between this batch and batch 2's deliberate non-rewrites: there the
source was wrong, here the source is fine and only our copy was truncated.

Usage:
    python3 tools/apply_p1_batch4.py          # dry run + gate
    python3 tools/apply_p1_batch4.py --apply  # write data/catalog.json
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p1_gate import load_baseline, run_gate  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "data" / "catalog.json"
BACKUP = ROOT / "data" / ".catalog-pre-p1-batch4.json"

# Source description as published by azgames.io on 2026-11-24, for audit.
SOURCE: dict[str, str] = {
    "astro-robot-clicker": "Astro Robot Clicker is the best clicker game, transporting you to a thrilling space journey! Get ready to discover the universe's mysteries and establish a timeless empire of technology.",
    "battle-karts": "Battle Karts Join the ultimate free multiplayer kart battle arena. Drive fast Unleash rockets Create epic explosions. Play now for endless thrills",
    "escape-road-city": "Escape Road City is a thrilling car chase game on the streets! Control your car, overcome all obstacles and escape from the police",
    "mamas-cookeria": "Mama's Cookeria is a cooking simulation game where you step into the kitchen as a budding chef and prepare delicious meals step by step through various mini games.",
    "mars-jump": "Mars Jump is a casual yet challenging arcade-style platformer where players use a jetpack to leap from platform to platform, aiming to travel as far as possible",
    "moto-x3m": "Moto X3M is a fast motorcycle racing game where you tackle difficult obstacles. Madpuffers' game has colorful graphics, realistic vehicle mechanics, and novel gameplay.",
    "papas-freezeria": "Papa's Freezeria is just what you need! This is a fun and realistic business game about running an ice cream shop.",
    "police-drive": "Gear up for action! Jump into the driver's seat of the police car or hop on the motorbike to chase down criminals and stop their crimes. Try Police Drive today!",
    "scary-wheels": "Scary Wheels isn't your average race! Drive strange vehicles, encounter unexpected traps, and overcome obstacles to reach the finish line as fast as you can.",
    "slope-3": "Slope 3 is a new version of the popular Slope game series. Let's see how far you can run on a high-speed slope while managing your ball.",
    "slope-emoji": "Slope Emoji is an addictive game with simple gameplay and funny graphics. The player's task is to control an emoji ball rolling quickly on a slope full of obstacles.",
}

REWRITES: dict[str, str] = {
    "astro-robot-clicker":
        "Astro Robot Clicker builds a technology empire one tap at a time: send "
        "robots out into space, find what is out there, and keep the upgrades coming.",
    "battle-karts":
        "Battle Karts is a multiplayer kart arena: drive fast, fire rockets at the "
        "other karts, and stay in one piece long enough to enjoy the explosions.",
    "escape-road-city":
        "Escape Road City is a police chase through traffic: steer around the "
        "obstacles, keep the car whole, and stay ahead of the pursuit.",
    "mamas-cookeria":
        "Mama's Cookeria puts you in the kitchen as a trainee chef: work each recipe "
        "step by step through a run of mini games.",
    "mars-jump":
        "Mars Jump runs on a jetpack: hop platform to platform across the Martian "
        "surface and see how far the fuel takes you.",
    "moto-x3m":
        "Moto X3M is time-trial motocross: pick a bike, clear the obstacle course, "
        "and reach the finish before the clock does.",
    "papas-freezeria":
        "Papa's Freezeria is an ice cream shop to run: take the orders, build each "
        "sundae in the right order, and keep the queue moving.",
    "police-drive":
        "Police Drive is a pursuit game: take the patrol car or the motorbike, chase "
        "the criminals down, and close the case.",
    "scary-wheels":
        "Scary Wheels races mismatched vehicles over trap-filled tracks — the finish "
        "line is all that matters, and the traps do not play fair.",
    "slope-3":
        "Slope 3 continues the downhill ball series: hold the line on a fast slope, "
        "keep the ball under control, and see how far it gets.",
    "slope-emoji":
        "Slope Emoji rolls a smiley ball down an obstacle-strewn slope: light "
        "inputs, high speed, and a long fall waiting at the first mistake.",
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
    if set(REWRITES) != set(SOURCE):
        print("ERROR: REWRITES and SOURCE must cover the same slugs.")
        return 1

    # The gate needs the pre-batch text to be meaningful. On the first run the
    # catalog still holds the fragments, which is exactly what we want.
    baseline = load_baseline(BACKUP) if BACKUP.exists() else {s: by_slug[s]["short"] for s in REWRITES}

    for slug, new in REWRITES.items():
        print(f"--- {slug}")
        print(f"  old: {by_slug[slug]['short']!r}")
        print(f"  new ({len(new.split())}w): {new}")

    rc = run_gate(REWRITES, baseline, verbose=False)
    if rc:
        return rc

    if not apply:
        print("\nDRY RUN — use --apply to write.")
        return 0

    if not BACKUP.exists():
        shutil.copy2(CATALOG, BACKUP)
        print(f"backup -> {BACKUP.name}")
    for slug, new in REWRITES.items():
        by_slug[slug]["short"] = new
    CATALOG.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")
    print(f"applied: {len(REWRITES)} fragmented shorts repaired.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())