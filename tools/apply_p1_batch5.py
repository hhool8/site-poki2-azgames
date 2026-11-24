#!/usr/bin/env python3
"""
apply_p1_batch5.py -- P1 batch 5: placeholder `short` replacement.

Second class of data defect found while verifying batch 3. These 6 entries are
not truncated and not copied: the source publishes no description for them at
all (azgames.io returns an empty `og:description`, and `temple-run-2` now 302s to
the homepage while its `.embed` still serves the game). Our copy had degraded to
a bare "Play X free online." placeholder, which is a worse intro than the
fragments in batch 4 and adds nothing to the page.

Confirmed before writing:
  - game bodies are alive: every `<slug>.embed` returns HTTP 200 serving a real
    game page (`<title>Play <name> Game Online!</title>`);
  - no vendor description exists to copy, so there is nothing to lean on.

Therefore the text below is written from what is verifiable: the mechanics of
the series each title belongs to (documented in sibling catalog entries:
slope/slope-2/slope-cyber/slope-emoji for the slope family, subway-surfers for
subway-santa, the Temple Run formula for temple-run-2) plus the theme named in
the title itself. No level counts, characters, or features are invented.

Usage:
    python3 tools/apply_p1_batch5.py          # dry run + gate
    python3 tools/apply_p1_batch5.py --apply  # write data/catalog.json
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
BACKUP = ROOT / "data" / ".catalog-pre-p1-batch5.json"

EVIDENCE: dict[str, str] = {
    "chill-girl-clicker": "no vendor description (empty og:description); embed alive",
    "slope-snowball": "no vendor description; slope-family mechanics from sibling entries",
    "slope-spooky": "no vendor description; slope-family mechanics from sibling entries",
    "subway-santa": "no vendor description; subway-surfers formula + Christmas skin",
    "temple-run-2": "vendor page 302s to homepage; embed alive; Temple Run formula",
    "temple-runner": "no vendor description; temple-runner formula",
}

# Deliberately conservative: series mechanic + title-named theme only.
REWRITES: dict[str, str] = {
    "chill-girl-clicker":
        "Chill Girl Clicker is idle tapping in the calm register: click the "
        "character, collect the points, and let the upgrades do the rest.",
    "slope-snowball":
        "Slope Snowball is the downhill ball run in winter dress — keep the ball "
        "rolling, dodge what the track puts in front of it, and stay on the slope.",
    "slope-spooky":
        "Slope Spooky sends the same fast ball down a track built for the season: "
        "steer around the obstacles and keep the run going.",
    "subway-santa":
        "Subway Santa is an endless runner on railway tracks with a Christmas "
        "skin: keep moving, dodge the trains, and collect what the run throws up.",
    "temple-run-2":
        "Temple Run 2 is the sequel to the original temple escape: run, swipe to "
        "turn, jump and slide past the traps, and see how far the chase goes.",
    "temple-runner":
        "Temple Runner is an endless dash through temple corridors: turn before "
        "the wall, jump the gaps, and keep the runner on his feet.",
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

    baseline = load_baseline(BACKUP) if BACKUP.exists() else {s: by_slug[s]["short"] for s in REWRITES}

    for slug, new in REWRITES.items():
        print(f"--- {slug}  [{EVIDENCE[slug]}]")
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
    print(f"applied: {len(REWRITES)} placeholder shorts replaced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())