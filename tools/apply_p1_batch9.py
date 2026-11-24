#!/usr/bin/env python3
"""
apply_p1_batch9.py -- P1 batch 9: batch-2 leftovers caught by a retro audit.

Batch 2 was written before the shared-word-run gate existed, and three of its
rewrites still carried a 5+ word run against the original source text. They were
not wrong enough to hurt, but they are the same defect the gate now rejects, so
the full catalog is being brought to one standard.

Retro-audit basis: every rewritten `short` was re-compared to its pre-batch1 text
(`data/.catalog-pre-p1-batch1.json`). Only these three failed:
    bombardino-crocodilo-clicker  run=8  "bombardino crocodilo clicker is an italian brainrot meme"
    italian-brainrot-clicker-2    run=7  "tralalero tralala tung tung tung sahur and"
    tung-sahur-clicker            run=6  "the village before dawn tap fast"

Usage:
    python3 tools/apply_p1_batch9.py          # dry run + gate
    python3 tools/apply_p1_batch9.py --apply  # write data/catalog.json
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
BACKUP = ROOT / "data" / ".catalog-pre-p1-batch9.json"

REWRITES: dict[str, str] = {
    "bombardino-crocodilo-clicker":
        "Bombardino Crocodilo Clicker is built on the Italian brainrot meme: tap "
        "the crocodile, watch the counter climb, and spend the earnings on upgrades.",
    "italian-brainrot-clicker-2":
        "Italian Brainrot Clicker 2 rounds up the whole meme cast — the shark in "
        "sneakers, the woodpecker, and the rest — and turns them into a tapping game.",
    "tung-sahur-clicker":
        "Tung Sahur Clicker is a themed tapper: rouse the village ahead of dawn, "
        "keep the clicks coming, and work up through the ranks.",
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

    # Compare against the ORIGINAL source text, which is the standard the audit
    # applies; the pre-batch9 backup would only show batch2's version.
    baseline = load_baseline(BASELINE) if BASELINE.exists() else {}

    for slug, new in REWRITES.items():
        print(f"--- {slug}")
        print(f"  original: {baseline.get(slug, '?')}")
        print(f"  batch2  : {by_slug[slug]['short']}")
        print(f"  new     : {new}")

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
    print(f"applied: {len(REWRITES)} batch-2 leftovers tightened.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())