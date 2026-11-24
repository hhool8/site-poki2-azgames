#!/usr/bin/env python3
"""
check_gate_single_source.py -- guard against the gate drifting back into copies.

Background: the batch-2 and batch-3 scripts each implemented the shared-word-run
metric by hand, and the two had already diverged within a day (batch 3 accepted
`is a/an`, batch 2 did not). That is a recurring failure mode in this repo, not
an isolated slip, so the rule is now enforced automatically instead of by memory:

  1. only `tools/p1_gate.py` may define `longest_shared_run` / `is_benign_title_phrase`;
  2. any batch script that *uses* the metric must import it from that module —
     batch 1 and 2 predate the metric entirely and are exempt by name, but a
     script that neither imports nor uses it must not silently grow its own copy;
  3. the gate's verdict for a fixed input must match a pinned expectation, so a
     silent semantic change fails the check as well.

Exit 0 = consistent. Exit 1 = violation. Runs in CI.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
GATE = TOOLS / "p1_gate.py"

# Written before the shared-word-run metric existed; verified by hand at the
# time and later re-audited by batch 9. They carry no gate code of their own.
PRE_METRIC_SCRIPTS = {"apply_p1_batch1.py", "apply_p1_batch2.py"}

# Pinned expectations: (old, new, slug, expected_run, expected_benign)
CASES = [
    # identical copy -> run spans the whole sentence
    ("Slope 2 is back with thrilling new obstacles!",
     "Slope 2 is back with thrilling new obstacles!", "slope-2", 8, False),
    # title + "is a" only -> benign, and deliberately below the threshold
    ("Car Chaos is a chaotic racing-battle game where you drive quirky cars.",
     "Car Chaos is a demolition derby in short rounds.", "car-chaos", 4, False),
    # title + "is the" -> benign at exactly 5
    ("Escape Road 2 is the intense sequel in the Escape Road series.",
     "Escape Road 2 is the sequel chase — more police behind the car.", "escape-road-2", 5, True),
    # real phrase past the article -> NOT benign
    ("Brain Lines is a drawing-based puzzle game that challenges your creativity.",
     "Brain Lines is a drawing puzzle: you sketch the answer.", "brain-lines", 5, False),
    # copied phrase that has nothing to do with the title -> NOT benign
    ("Tiny Arena is arcade combat against waves of enemies and bosses.",
     "Tiny Arena is arcade gladiator combat against waves of enemies.", "tiny-arena", 5, False),
]


def fail(msg: str) -> int:
    print(f"FAIL: {msg}")
    return 1


def main() -> int:
    defs = {}
    for f in sorted(TOOLS.glob("*.py")):
        for name in ("longest_shared_run", "is_benign_title_phrase"):
            if re.search(rf"^def {name}\(", f.read_text(), re.M):
                defs.setdefault(name, []).append(f.name)

    problems = []
    for name, files in defs.items():
        if files != [GATE.name]:
            problems.append(f"{name} defined in {files}, expected only {GATE.name}")
    if not defs:
        return fail("the gate functions are not defined anywhere")

    for f in sorted(TOOLS.glob("apply_p1_batch*.py")):
        if f.name in PRE_METRIC_SCRIPTS:
            text = f.read_text()
            if "from p1_gate import" in text or "longest_shared_run" in text:
                problems.append(
                    f"{f.name} is exempt but now references the gate; "
                    "remove the exemption so the check applies to it"
                )
            continue
        if "from p1_gate import" not in f.read_text():
            problems.append(f"{f.name} does not import from p1_gate")

    if problems:
        for p in problems:
            print(f"FAIL: {p}")
        return 1

    sys.path.insert(0, str(TOOLS))
    from p1_gate import is_benign_title_phrase, longest_shared_run  # noqa: E402

    for old, new, slug, exp_run, exp_benign in CASES:
        run, phrase = longest_shared_run(old, new)
        if run != exp_run:
            return fail(f"{slug}: run={run}, pinned {exp_run} (phrase={phrase!r})")
        benign = run >= 5 and is_benign_title_phrase(slug, phrase)
        if benign != exp_benign:
            return fail(f"{slug}: benign={benign}, pinned {exp_benign} (phrase={phrase!r})")

    print(f"OK: gate is single-source in {GATE.name}; "
          f"{len(CASES)} pinned verdicts match; "
          f"{len(list(TOOLS.glob('apply_p1_batch*.py')))} batch scripts import it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())