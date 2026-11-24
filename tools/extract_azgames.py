#!/usr/bin/env python3
"""Crawl azgames.poki2.online and build data/catalog.json.

The live site is plain static HTML (no Cloudflare challenge, no client-side
rendering), so a plain urllib fetch is enough -- unlike the hahagames rebuild
that needed a real Chrome instance to get past a managed challenge.

What we keep per game:
  slug, title, image, embed     -> needed to render the page
  short                         -> the one unique sentence the source has
  category                      -> breadcrumb + listing membership
  faq                           -> only the questions, re-asked in our own copy
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ORIGIN = "https://azgames.poki2.online"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
)
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def fetch(url: str, tries: int = 3) -> str:
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read().decode("utf-8", "ignore")
        except (urllib.error.URLError, TimeoutError, OSError) as exc:  # noqa: PERF203
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"{url}: {last}")


def text(fragment: str) -> str:
    fragment = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", fragment, flags=re.S)
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(fragment)).strip()


def between(hay: str, start: str, end: str) -> str:
    i = hay.find(start)
    if i < 0:
        return ""
    i += len(start)
    j = hay.find(end, i)
    return hay[i:j] if j > 0 else hay[i:]


def parse_game(slug: str, doc: str) -> dict:
    head = between(doc, "<head", "</head>")

    title = text(between(doc, "<h1>", "</h1>")) or slug.replace("-", " ").title()
    meta_desc = ""
    m = re.search(r'<meta name="description" content="([^"]*)"', head)
    if m:
        meta_desc = html.unescape(m.group(1)).strip()

    short = text(between(doc, 'class="game-info-desc">', "</p>"))
    # The `game-info-desc` container was removed from azgames.io, so this lookup
    # now returns "" for every game. Fall back to the meta description rather
    # than emitting an empty/fragmentary string, and record which source was
    # used so a stale field can be spotted later instead of silently shipping.
    short_source = "info-desc" if short else ""
    if not short:
        short, short_source = meta_desc, "meta-desc"
    # A sentence that stops without terminal punctuation is the shape the
    # truncated copies had ("Mama", "Scary Wheels isn"). Flag it for review; it
    # is a hint, not proof, because some source descriptions legitimately omit
    # the final full stop.
    if short and short.rstrip()[-1] not in ".!?":
        short_source += ":unterminated"

    cat_slug = cat_name = ""
    m = re.search(r'class="game-info-tag" href="/category/([^"]+)"[^>]*>([^<]+)<', doc)
    if m:
        cat_slug, cat_name = m.group(1), text(m.group(2))
    if not cat_slug:
        m = re.search(r'<a href="/category/([^"]+)">([^<]+)</a>\s*</p>\s*</div>\s*$', doc)
        if m:
            cat_slug, cat_name = m.group(1), text(m.group(2))

    embed = ""
    m = re.search(r'<iframe[^>]*\sid="gameFrame"[^>]*\ssrc="([^"]+)"', doc) or re.search(
        r'<iframe[^>]*\ssrc="([^"]*\.embed[^"]*)"', doc
    )
    if m:
        embed = html.unescape(m.group(1))

    img = ""
    m = re.search(r'<img[^>]*class="game-play-icon"[^>]*src="([^"]+)"', doc)
    if not m:
        m = re.search(r'"image":\s*"([^"]+)"', doc)
    if m:
        img = html.unescape(m.group(1))
    if not img:
        img = f"/images/games/{slug}.png"

    questions = [text(q) for q in re.findall(r'class="game-faq-q"[^>]*>(.*?)</h3>', doc, re.S)]
    answers = [text(a) for a in re.findall(r'itemprop="text">(.*?)</p>', doc, re.S)]

    # Sections the source already writes for each game, kept for the article body.
    body: list[dict] = []
    for m in re.finditer(r'<h2[^>]*>(.*?)</h2>\s*(<p[^>]*>.*?</p>)', doc, re.S):
        heading, para = text(m.group(1)), text(m.group(2))
        if heading and para and len(para) > 40 and heading.lower() not in {"frequently asked questions"}:
            body.append({"h": heading, "p": para})

    notes = ""
    m = re.search(r'class="game-seo-note"[^>]*>(.*?)</p>', doc, re.S)
    if m:
        notes = text(m.group(1))

    return {
        "slug": slug,
        "title": title,
        "meta": meta_desc,
        "short": short,
        "short_source": short_source,
        "image": img,
        "embed": embed,
        "category": cat_slug,
        "category_name": cat_name,
        "notes": notes,
        "faq": questions,
        "faq_answers": answers,
        "body": body,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", default="catalog.json")
    args = ap.parse_args()

    DATA.mkdir(parents=True, exist_ok=True)
    home = fetch(f"{ORIGIN}/")

    cats = sorted(set(re.findall(r'href="(/category/[^"]+)"', home)))
    plays: set[str] = set(re.findall(r'href="(/play/[^"]+)"', home))
    cat_pages: dict[str, list[str]] = {}

    for path in cats:
        doc = fetch(ORIGIN + path)
        found = sorted(set(re.findall(r'href="(/play/[^"]+)"', doc)))
        cat_pages[path.rsplit("/", 1)[-1]] = [f.rsplit("/", 1)[-1] for f in found]
        plays |= set(found)
        print(f"  {path:38s} {len(found):4d}", flush=True)

    # The source pages contain JS template literals such as
    # href="/play/' + escAttr(g.slug) + '" that look like game links; a real
    # slug is lowercase ascii and hyphenated only.
    slugs = sorted({s.rsplit("/", 1)[-1] for s in plays if re.fullmatch(r"[a-z0-9][a-z0-9-]*", s.rsplit("/", 1)[-1])})
    if args.limit:
        slugs = slugs[: args.limit]
    print(f"games: {len(slugs)} | categories: {len(cats)}", flush=True)

    games: dict[str, dict] = {}
    errors: list[dict] = []

    def work(slug: str) -> None:
        try:
            doc = fetch(f"{ORIGIN}/play/{slug}")
            games[slug] = parse_game(slug, doc)
        except Exception as exc:  # noqa: BLE001
            errors.append({"slug": slug, "error": str(exc)[:200]})

    started = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for i, _ in enumerate(pool.map(work, slugs), 1):
            if i % 40 == 0 or i == len(slugs):
                rate = i / max(time.time() - started, 0.01)
                print(f"  {i}/{len(slugs)}  {rate:.1f} pages/s", flush=True)

    order = {slug: idx for idx, slug in enumerate(slugs)}
    rows = sorted(games.values(), key=lambda g: order.get(g["slug"], 10**6))

    catalogue = {
        "source": ORIGIN,
        "fetched": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "counts": {
            "games": len(rows),
            "categories": len(cat_pages),
            "errors": len(errors),
            "no_embed": sum(1 for g in rows if not g["embed"]),
            "no_short": sum(1 for g in rows if len(g["short"]) < 30),
            "short_unterminated": sum(
                1 for g in rows if g.get("short_source", "").endswith(":unterminated")
            ),
        },
        "categories": [
            {
                "slug": slug,
                "name": rows[0]["category_name"] if rows else slug,
                "games": cat_pages.get(slug, []),
            }
            for slug in cat_pages
        ],
        "games": rows,
        "errors": errors,
    }

    # Human-readable category labels, taken from the category pages themselves.
    for cat in catalogue["categories"]:
        doc = fetch(f"{ORIGIN}/category/{cat['slug']}")
        m = re.search(r"<h1[^>]*>(.*?)</h1>", doc, re.S)
        name = text(m.group(1)).split("—")[0].strip() if m else ""
        cat["name"] = name or cat["slug"].replace("-", " ").title()

    out = DATA / args.out
    out.write_text(json.dumps(catalogue, indent=1))
    print(f"wrote {out} | {catalogue['counts']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
