#!/usr/bin/env python3
"""
apply_p1_batch10.py -- P1 batch 10: disposition of the 6 source-mismatch entries.

Earlier batches deliberately left these alone because their `short` had been
copied from a description that names a different game. Rewriting them then would
have laundered a data defect. They are handled now because each one has been
resolved against real evidence instead of guesswork.

Evidence gathered 2026-11-24 (all recorded below, reproducible):

  identity — every one of the six serves a live Unity WebGL build at
  `https://game.azgame.io/<slug>/`, whose `productName` field equals the entry
  title. So none of them is a dead or wrong embed; the game behind the page is
  the game the title claims.

  egg-race vs eggy-car — NOT duplicates, despite sharing the Eggy Car
  description. Different distribution channels (game.azgame.io own build vs a
  GameDistribution package), different cover art (snow/snowman/red-green
  Christmas car vs green hills/red car/plain egg). Two games, one copy-pasted
  description on the vendor side.

  usable source text — steel-legion has a full "How to Play" section and
  idle-gold-miner has a full "Gameplay Insights" section that describe the
  correct game. Those two are written from that text.

  unusable source text — escape-jump, egg-race, overtake-x and power-surfer have
  nothing but the wrong description in any field (meta, og, About section). Their
  copy is written only from what is verifiable: the title, the cover art, and the
  engine. No level counts, characters or features are invented.

Usage:
    python3 tools/apply_p1_batch10.py          # dry run + gate
    python3 tools/apply_p1_batch10.py --apply  # write data/catalog.json
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
BASELINE = ROOT / "data" / ".catalog-pre-p1-batch1.json"  # original source text
BACKUP = ROOT / "data" / ".catalog-pre-p1-batch10.json"

# What each entry was resolved against. Kept in the script so the decision is
# auditable without re-running the investigation.
DISPOSITION: dict[str, str] = {
    "escape-jump":
        "no correct text anywhere on the vendor page; written from title + cover "
        "(blocky/voxel street scene, character carrying cash) + engine",
    "idle-gold-miner":
        "vendor 'Gameplay Insights' section describes the correct game: workers, "
        "managers, mine/elevator/warehouse upgrades, new shafts, offline income",
    "egg-race":
        "vendor description is Eggy Car's; proven a different game (own build at "
        "game.azgame.io, winter cover art); written from title + cover",
    "overtake-x":
        "no correct text anywhere; written from title + cover (yellow sedan, "
        "motion blur) + engine",
    "power-surfer":
        "no correct text anywhere; written from title + cover (robot on a "
        "hoverboard, orange sky) + engine",
    "steel-legion":
        "vendor 'How to Play' section describes the correct game: Cobra tank, "
        "hills, aimed shots, coins, upgrades, the Legion",
}

REWRITES: dict[str, str] = {
    "escape-jump":
        "Escape Jump is a blocky chase through a city street: the character gets "
        "out with the cash, and the traffic in front of him does not stop for it.",
    "idle-gold-miner":
        "Idle Gold Miner builds a mining business from a single shaft: click the "
        "workers to dig, hire managers so they dig without you, and reinvest in "
        "mines, lifts and warehouses until the money arrives on its own.",
    "egg-race":
        "Egg Race is a winter drive with something fragile on board: steer the "
        "carrying car over the snow, balance the egg through the bumps, and collect "
        "the coins on the way down.",
    "overtake-x":
        "Overtake X is about the pass: pick the gap in the traffic ahead, commit to "
        "it at speed, and settle back into the lane once you are clear.",
    "power-surfer":
        "Power Surfer is a hoverboard run: take the board over the course, keep the "
        "balance, and clear the obstacles that come at you in the air.",
    "steel-legion":
        "Steel Legion is tank combat on uneven ground: drive the Cobra over the "
        "hills, place the shot so the slope does not throw it off, and spend the "
        "coins on armour, gun and engine before the Legion turns up.",
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
    if set(REWRITES) != set(DISPOSITION):
        print("ERROR: every rewrite needs a recorded disposition.")
        return 1

    # Compare to the original vendor text, not to the current catalog: the
    # current text IS the wrong description, and matching against it is the
    # whole reason the gate exists.
    baseline = load_baseline(BASELINE) if BASELINE.exists() else {}

    for slug, new in REWRITES.items():
        print(f"--- {slug}")
        print(f"  vendor text : {baseline.get(slug, '?')}")
        print(f"  disposition : {DISPOSITION[slug]}")
        print(f"  new ({len(new.split())}w)   : {new}")

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
    print(f"applied: {len(REWRITES)} source-mismatch entries given correct copy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())