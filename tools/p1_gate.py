#!/usr/bin/env python3
"""
p1_gate.py -- the single implementation of the P1 acceptance gate.

Every batch script imports this instead of carrying its own copy. The gate was
written twice by hand (batch 2, batch 3) and the two copies had already started
to diverge (batch 3 added the `is a/an` exception, batch 2 did not). One
implementation, one behaviour.

Metric: the longest run of CONSECUTIVE shared words between the old and the new
copy of a field. SequenceMatcher's ratio is useless for game titles because
proper nouns ("Cuby Road", "Ice Baby Quest") dominate it and produce 0.6-0.74
false positives on text that shares nothing else.

Threshold: a run of 5+ words is a real copied phrase, except for the single
structural case `<title> is a/an/the`, where the title cannot change and the
connector is the only grammatical way to introduce a game in English.
"""
from __future__ import annotations

import re
import sys

TOKEN = re.compile(r"[a-z0-9']+")
ARTICLES = {"a", "an", "the"}


def longest_shared_run(a: str, b: str) -> tuple[int, str]:
    ta, tb = TOKEN.findall(a.lower()), TOKEN.findall(b.lower())
    best, best_phrase = 0, ""
    prev = [0] * (len(tb) + 1)
    for i in range(1, len(ta) + 1):
        cur = [0] * (len(tb) + 1)
        for j in range(1, len(tb) + 1):
            if ta[i - 1] == tb[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best = cur[j]
                    best_phrase = " ".join(ta[i - cur[j]:i])
        prev = cur
    return best, best_phrase


def is_benign_title_phrase(slug: str, phrase: str) -> bool:
    """`<title> is a/an/the` cannot be avoided: the title is fixed, the connector
    is grammar. Anything past the article is a real phrase and still counts."""
    title_tokens = TOKEN.findall(slug.replace("-", " ").lower())
    p = TOKEN.findall(phrase.lower())
    if len(p) < 2 or p[-2] != "is" or p[-1] not in ARTICLES:
        return False
    core = p[:-2]
    return bool(core) and core == title_tokens[-len(core):]


def run_gate(rewrites: dict[str, str], baseline: dict[str, str], verbose: bool = True) -> int:
    """Print the overlap report and return 0 on pass, 2 on rejection."""
    worst, benign = 0, []
    for slug, new in rewrites.items():
        old = baseline.get(slug, "")
        run, phrase = longest_shared_run(old, new)
        if run >= 5 and is_benign_title_phrase(slug, phrase):
            benign.append(f"{slug} (\"{phrase}\")")
            continue
        worst = max(worst, run)
        if not verbose:
            continue
        print(f"{slug:<26} run={run}{'  <-- OVERLAP' if run >= 5 else ''}")
        if run >= 4:
            print(f"    shared: \"{phrase}\"")
            print(f"    old: {old}")
            print(f"    new: {new}")

    print(f"\n{len(rewrites)} rewrites staged, longest non-benign shared run = {worst}")
    if benign:
        print("Benign title phrases (allowed):")
        for b in benign:
            print(f"  - {b}")
    if worst >= 5:
        print("REJECT: shared run >= 5 words. Fix the flagged entries first.")
        return 2
    return 0


def load_baseline(path):
    """Pre-batch text. Required when re-running a batch after --apply, otherwise
    the catalog already holds the new copy and the gate compares it to itself."""
    import json
    d = json.loads(path.read_text())
    games = d if isinstance(d, list) else d["games"]
    return {g["slug"]: g.get("short", "") for g in games}


if __name__ == "__main__":
    sys.exit("import me; do not run me")