#!/usr/bin/env python3
"""check_lastmod_truthful.py — guard the sitemap's freshness claims.

WHY THIS EXISTS
`sitemap.xml` used to stamp ONE date on all 314 URLs, taken from a hardcoded
constant (`NOW = dt.date(2026, 11, 6)`). That constant then outlived its purpose:
the 2026-11-24 content batches rewrote 280 intros while every URL still advertised
2026-11-06. A <lastmod> that describes the build instead of the page is a false
signal to Google in whichever direction it is wrong.

The fix (per-URL content fingerprints in data/sitemap-lastmod.json) can regress in
three quiet ways, so this script pins all three:

  1. A single date on every URL again — the original bug, easiest to reintroduce
     by "simplifying" the sitemap loop.
  2. A date LATER than the newest evidence we have. Nothing can have changed after
     today, so a future date means the clock, not the content, decided.
  3. A URL in the sitemap with no history entry, or a history entry whose hash no
     longer matches the file on disk — the fingerprint stopped covering the page.
  4. A date decided by "we do not know" rather than by evidence. A build with no
     prior history and no migration seed marks every page `unknown` and dates it
     TODAY, which is the original bug wearing a fingerprint. Checks 1-3 all pass
     in that state (the dates are consistent, not future, and hashed), so this
     has to be asserted separately — otherwise the guard merely certifies that the
     sitemap is well-formed, not that it is true.

Exit 0 = the dates are defensible. Exit 1 = a claim needs fixing before deploy.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
SITEMAP = DIST / "sitemap.xml"
STORE = ROOT / "data" / "sitemap-lastmod.json"

sys.path.insert(0, str(ROOT / "tools"))
from build_site import TODAY, canonicalize_html  # noqa: E402  (single source of truth)

failures: list[str] = []
notes: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)
    print(f"   FAIL {msg}")


def ok(msg: str) -> None:
    print(f"   ok   {msg}")


if not SITEMAP.exists():
    print("dist/sitemap.xml not found — run `python3 tools/build_site.py` first")
    raise SystemExit(1)
if not STORE.exists():
    print("data/sitemap-lastmod.json not found — the sitemap has no change history")
    raise SystemExit(1)

xml = SITEMAP.read_text()
pairs = re.findall(r"<loc>([^<]+)</loc><lastmod>([^<]+)</lastmod>", xml)
if not pairs:
    print("no <loc>/<lastmod> pairs parsed from sitemap.xml")
    raise SystemExit(1)

today = TODAY  # same UTC clock as the builder; never a host-local date
dates = {loc: lm for loc, lm in pairs}
distinct = sorted(set(dates.values()))

# 1. more than one date ---------------------------------------------------------
# A brand-new site legitimately has one date on day one. Once history exists,
# collapsing back to a single date is the regression, so require real spread
# whenever the site has had more than one change period.
if len(distinct) == 1:
    only = distinct[0]
    # Tolerate it only if today IS that date (first build of a brand-new site).
    if only != today.isoformat():
        fail(f"all {len(dates)} URLs claim the same lastmod {only} — "
             "that is a build date, not per-page history")
    else:
        notes.append("single date equals today (acceptable only on a first build)")
else:
    ok(f"lastmod spread across {len(distinct)} dates: {', '.join(distinct)}")

# 2. no date in the future -----------------------------------------------------
future = {loc: lm for loc, lm in dates.items() if lm > today.isoformat()}
if future:
    sample = ", ".join(f"{k} -> {v}" for k, v in list(future.items())[:3])
    fail(f"{len(future)} URL(s) claim a lastmod after today ({today}): {sample}")
else:
    ok(f"no lastmod is later than today ({today})")

# 3. every URL has history, and the history still matches the file -------------
try:
    store = json.loads(STORE.read_text())
except ValueError as exc:
    print(f"data/sitemap-lastmod.json is not valid JSON: {exc}")
    raise SystemExit(1)

missing_history = [loc for loc in dates if loc.replace("https://azgames.poki2.online", "") not in store]
if missing_history:
    fail(f"{len(missing_history)} sitemap URL(s) have no history entry: "
         f"{', '.join(missing_history[:3])}")
else:
    ok("every sitemap URL has a history entry")

# Recompute the fingerprint from the file actually written to dist/. A mismatch
# means the stored hash describes something other than the deployed page.
def path_to_file(url_path: str) -> Path | None:
    if url_path == "/":
        return DIST / "index.html"
    if url_path.endswith("/"):
        return DIST / url_path.strip("/") / "index.html"
    return DIST / (url_path.strip("/") + ".html")

stale = []
for loc in dates:
    rel = loc.replace("https://azgames.poki2.online", "")
    entry = store.get(rel)
    if not entry:
        continue
    target = path_to_file(rel)
    if not target or not target.exists():
        stale.append((rel, "missing file"))
        continue
    digest = hashlib.sha256(canonicalize_html(target.read_text()).encode()).hexdigest()[:32]
    if digest != entry.get("hash"):
        stale.append((rel, "hash mismatch"))
if stale:
    fail(f"{len(stale)} URL(s) whose stored fingerprint no longer matches dist/: "
         f"{', '.join(f'{p} ({why})' for p, why in stale[:3])}")
else:
    ok("stored fingerprints match the built files")

# 4. the dates were decided by evidence, not by "we do not know" ----------------
REPORT = ROOT / "data" / "sitemap-lastmod-report.json"
if not REPORT.exists():
    fail("data/sitemap-lastmod-report.json is missing — cannot tell how many "
         "dates were guessed (rebuild with the current build_site.py)")
else:
    report = json.loads(REPORT.read_text())
    unknown = report.get("unknown") or []
    stats = report.get("stats") or {}
    if unknown:
        # This is the state a CI checkout lands in when the migration seed files
        # are absent: every page is "never seen", so TODAY gets stamped on all of
        # them. Checks 1-3 pass because the output is self-consistent.
        fail(f"{len(unknown)} URL(s) were dated today because no provenance "
             f"existed: {', '.join(unknown[:3])}"
             + (f" (+{len(unknown) - 3} more)" if len(unknown) > 3 else ""))
    else:
        ok(f"no date was guessed: {stats.get('kept', 0)} kept, "
           f"{stats.get('bumped', 0)} changed, {stats.get('seeded', 0)} seeded")

print()
if failures:
    print(f"lastmod claims are NOT defensible ({len(failures)} problem(s)). "
          "Rebuild before deploying.")
    raise SystemExit(1)

print(f"lastmod claims are defensible: {len(dates)} URLs, "
      f"{len(distinct)} distinct dates, none in the future, all fingerprinted.")
for n in notes:
    print(f"   note: {n}")