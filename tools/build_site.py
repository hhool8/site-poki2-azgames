#!/usr/bin/env python3
"""Generate azgames.poki2.online as a static site.

Design is the poki2.online stylesheet, unchanged: same CSS variables, same
nav/footer markup, same .featured-card / .site-card components. Only the
accent usage and the page bodies differ, because this site has no blog and a
much smaller catalogue.

Output (dist/):
  /                               home
  /play/<slug>/                   one page per game
  /category/<slug>/               one page per category (all games, no paging)
  /games/ + /games/page/N/        full catalogue, 48 per page
  /search/ + /search-index.json   client-side search
  /about /contact /privacy /terms /dmca
  /404.html, sitemap.xml, robots.txt, ads.txt, _headers
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
TPL = SRC / "templates"
DATA = ROOT / "data"
DIST = ROOT / "dist"
MAIN_SITE_CSS = Path("/Users/hou/Desktop/SEXTANT/sites/poki2-online/04-source/css/style.css")

NOW = dt.date(2026, 11, 6)

CATEGORY_META = {
    "2-player-games": ("👥", "#a855f7", "One keyboard, two players — the games here expect a second person on the same machine."),
    "adventure-games": ("🗺️", "#22d3ee", "Exploration, quests and slow-burn progression rather than a single run."),
    "car-games": ("🚗", "#f97316", "Driving, drifting and traffic dodging, mostly one-thumb friendly."),
    "casual-games": ("🎮", "#38bdf8", "Short sessions, low pressure, easy to pick up between other things."),
    "clicker-games": ("🖱️", "#facc15", "Incremental games where the loop is the point: click, upgrade, repeat."),
    "io-games": ("🌐", "#34d399", "Arena games with short rounds and other people in them."),
    "kids-games": ("🧒", "#fb7185", "Simpler rules and gentler pacing, chosen with younger players in mind."),
    "puzzle-games": ("🧩", "#c084fc", "Logic, matching and spatial problems that reward thinking before clicking."),
    "shooting-games": ("🎯", "#f43f5e", "Aiming and reflexes — browser shooters rather than anything realistic."),
    "sports-games": ("🏆", "#fbbf24", "Football, basketball, golf and other sports compressed into short arcade rounds."),
}

CATEGORY_BLURB = {
    "2-player-games": "each one is playable on a single keyboard, so a second player only needs to sit down.",
    "adventure-games": "expect exploration and a bit of patience rather than a sixty-second round.",
    "car-games": "the emphasis is on handling and traffic rather than simulation.",
    "casual-games": "sessions are short and the controls are simple by design.",
    "clicker-games": "the loop is deliberately repetitive — that is the appeal, not a flaw.",
    "io-games": "rounds are short and the arena is shared with other players.",
    "kids-games": "rules are simple and the pacing is gentler than the action shelves.",
    "puzzle-games": "most reward thinking a move ahead rather than fast clicking.",
    "shooting-games": "aim and reaction time matter more than realism.",
    "sports-games": "the sport is compressed into short arcade rounds.",
}


def esc(value: str) -> str:
    return html.escape(value or "", quote=True)


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def pick(seq, seed: str, count: int) -> list:
    """Deterministic spread across a list: same seed always yields the same pick."""
    if not seq:
        return []
    if len(seq) <= count:
        return list(seq)
    step = len(seq) / count
    offset = int(hashlib.md5(seed.encode()).hexdigest(), 16) % max(1, int(step))
    return [seq[min(int(i * step) + offset, len(seq) - 1)] for i in range(count)]


class Site:
    def __init__(self) -> None:
        self.cfg = json.loads((SRC / "config.json").read_text())
        self.catalog = json.loads((DATA / "catalog.json").read_text())
        self.site = self.cfg["site"]
        self.ads = self.cfg["ads"]
        self.build = self.cfg["build"]
        self.domain = self.site["domain"].rstrip("/")

        self.games = [g for g in self.catalog["games"] if g["embed"]]
        self.by_slug = {g["slug"]: g for g in self.games}

        # Category membership comes from the live site's own category pages, so
        # it matches what visitors already expect from this domain.
        self.cats: list[dict] = []
        for cat in self.catalog["categories"]:
            members = [self.by_slug[s] for s in cat["games"] if s in self.by_slug]
            if not members:
                continue
            emoji, color, _ = CATEGORY_META.get(cat["slug"], ("🎮", "#22d3ee", ""))
            self.cats.append(
                {
                    "slug": cat["slug"],
                    "name": cat["name"],
                    "emoji": emoji,
                    "color": color,
                    "blurb": CATEGORY_META.get(cat["slug"], ("", "", "Browse the shelf."))[2],
                    "games": members,
                }
            )
        self.cats.sort(key=lambda c: -len(c["games"]))
        self.cat_by_slug = {c["slug"]: c for c in self.cats}

        self.base_tpl = (TPL / "base.html").read_text()
        self.home_tpl = (TPL / "home.html").read_text()
        self.game_tpl = (TPL / "game.html").read_text()
        self.list_tpl = (TPL / "list.html").read_text()
        self.static_tpl = (TPL / "static.html").read_text()
        self.search_tpl = (TPL / "search.html").read_text()

        self.written: list[tuple[str, str]] = []

    # ---------------- shared chrome ----------------

    @property
    def adsense_loader(self) -> str:
        if not self.ads.get("enabled"):
            return ""
        client = self.ads["client"]
        return (
            '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
            f'?client={client}" crossorigin="anonymous"></script>'
        )

    def ad_slot(self, key: str) -> str:
        """Emit an ad unit only when a real slot id is configured.

        An empty <ins> reserves no space and pushes an unfilled request, which
        is worse than shipping no unit at all — so Auto ads carries the site
        until slot ids exist.
        """
        if not self.ads.get("enabled"):
            return ""
        slot = (self.ads.get("slots") or {}).get(key, "")
        if not slot:
            return ""
        return (
            '<div class="ad-slot"><ins class="adsbygoogle" style="display:block" '
            f'data-ad-client="{self.ads["client"]}" data-ad-slot="{slot}" '
            'data-ad-format="auto" data-full-width-responsive="true"></ins>'
            "<script>(adsbygoogle=window.adsbygoogle||[]).push({});</script></div>"
        )

    def nav_categories(self) -> str:
        return "".join(
            f'<li><a href="/category/{c["slug"]}/">{esc(c["name"])}</a></li>' for c in self.cats
        )

    def footer_categories(self) -> str:
        return "".join(
            f'<li><a href="/category/{c["slug"]}/">{esc(c["name"])} ({len(c["games"])})</a></li>'
            for c in self.cats[:8]
        )

    def render(self, body: str, *, title: str, description: str, path: str,
               body_class: str = "", schema: str = "", og_type: str = "website",
               og_image: str = "/favicon.svg", head_extra: str = "") -> str:
        canonical = self.domain + path
        out = self.base_tpl
        replacements = {
            "{{TITLE}}": esc(title),
            "{{DESCRIPTION}}": esc(description),
            "{{CANONICAL}}": esc(canonical),
            "{{OG_TITLE}}": esc(title),
            "{{OG_TYPE}}": og_type,
            "{{OG_IMAGE}}": esc(self.domain + og_image),
            "{{SCHEMA}}": schema,
            "{{ADS_CLIENT}}": self.ads["client"],
            "{{ADSENSE_LOADER}}": self.adsense_loader,
            "{{SITE_NAME}}": esc(self.site["name"]),
            "{{BODY_CLASS}}": body_class,
            "{{NAV_CATEGORIES}}": self.nav_categories(),
            "{{FOOTER_CATEGORIES}}": self.footer_categories(),
            "{{GAME_COUNT}}": f"{len(self.games):,}",
            "{{YEAR}}": str(NOW.year),
            "{{CONTENT}}": body,
        }
        for key, value in replacements.items():
            out = out.replace(key, value)
        if head_extra:
            out = out.replace("</head>", head_extra + "\n</head>")
        return out

    def write(self, path: str, html_text: str, *, priority: str = "0.6",
              changefreq: str = "weekly", sitemap: bool = True,
              file: str | None = None) -> None:
        if file:
            target = DIST / file
        elif path == "/":
            target = DIST / "index.html"
        elif path.endswith("/"):
            target = DIST / path.lstrip("/") / "index.html"
        else:
            # Pages maps /about to /about.html and serves it as text/html.
            # An extensionless file would be served as octet-stream.
            target = DIST / (path.lstrip("/") + ".html")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html_text)
        self.written.append((path, priority))
        if not sitemap:
            self.written.pop()

    # ---------------- components ----------------

    def card(self, game: dict, *, eager: bool = False) -> str:
        cat = self.cat_by_slug.get(game["category"])
        cat_name = cat["name"] if cat else "Games"
        loading = 'loading="eager"' if eager else 'loading="lazy"'
        return (
            f'<a class="featured-card" href="/play/{game["slug"]}/">'
            f'<img src="/img/game/{game["slug"]}.webp" alt="{esc(game["title"])} game cover" '
            f'width="400" height="400" {loading}>'
            f'<span class="featured-card-label">{esc(game["title"])}</span>'
            f'<span class="featured-card-src">{esc(cat_name)}</span></a>'
        )

    def category_card(self, cat: dict) -> str:
        desc = cat["blurb"]
        return (
            f'<a class="site-card" href="/category/{cat["slug"]}/" style="--card-color:{cat["color"]}">'
            '<div class="site-card-header">'
            f'<div class="site-card-icon">{cat["emoji"]}</div>'
            f'<span class="site-card-name">{esc(cat["name"])}</span>'
            f'<span class="site-card-status live">{len(cat["games"])} games</span>'
            "</div>"
            f'<p class="site-card-desc">{esc(desc)}</p>'
            f'<span class="site-card-cta cta-live">Browse {esc(cat["name"])} →</span>'
            "</a>"
        )

    # ---------------- pages ----------------

    def build_home(self) -> None:
        featured = pick(self.games, "home-featured", self.build["heroCount"])
        mid = len(self.games) // 2
        second = pick(self.games[mid:] + self.games[:mid], "home-second", self.build["heroCount"])

        body = self.home_tpl
        body = body.replace("{{FEATURED}}", "".join(self.card(g, eager=i < 6) for i, g in enumerate(featured)))
        body = body.replace("{{NEWEST}}", "".join(self.card(g) for g in second))
        body = body.replace("{{CATEGORY_CARDS}}", "".join(self.category_card(c) for c in self.cats))
        body = body.replace("{{AD_HOME}}", self.ad_slot("homeMid"))
        body = body.replace("{{GAME_COUNT}}", f"{len(self.games):,}")
        body = body.replace("{{CATEGORY_COUNT}}", str(len(self.cats)))

        title = f"AZ Games — {len(self.games)} Free Browser Games, No Download"
        description = (
            f"Play {len(self.games)} free browser games at AZ Games: clicker, .io, puzzle, car, "
            "shooting, sports and 2-player titles. No download, no login, instant play."
        )
        schema = json.dumps(
            {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": "AZ Games",
                "url": self.domain + "/",
                "potentialAction": {
                    "@type": "SearchAction",
                    "target": self.domain + "/search/?q={search_term_string}",
                    "query-input": "required name=search_term_string",
                },
            },
            separators=(",", ":"),
        )
        schema = f'<script type="application/ld+json">{schema}</script>'

        self.write("/", self.render(body, title=title, description=description, path="/",
                                    body_class="home-page", schema=schema), priority="1.0")

    def game_copy(self, game: dict) -> dict:
        title = game["title"]
        cat = self.cat_by_slug.get(game["category"])
        cat_name = cat["name"] if cat else "games"

        intro = (game.get("short") or "").strip()
        if len(intro) < 40:
            intro = (game.get("meta") or "").split("|")[0].strip()
        if len(intro) < 40:
            intro = f"{title} is one of the {cat_name.lower()} on AZ Games, playable in the browser without an install."
        if not intro.endswith((".", "!", "?")):
            intro += "."

        variants = [
            (
                f"<ol><li>Open the page and press play — the game loads inside this page.</li>"
                f"<li>Use the mouse, the keyboard or the touchscreen, depending on what {esc(title)} expects.</li>"
                f"<li>Progress in {esc(title)} is kept by the game itself; closing the tab ends the session.</li></ol>"
            ),
            (
                f"<p>Press play above and {esc(title)} starts in the embedded player — there is no launcher and no "
                f"account step. Controls are the ones the game itself shows on its first screen; if nothing responds, "
                f"click once inside the game area so it receives keyboard focus.</p>"
            ),
            (
                f"<ul><li>Press play to load {esc(title)} in place.</li>"
                f"<li>Click inside the frame if the keyboard does not respond — the game needs focus first.</li>"
                f"<li>Fullscreen is available from the player; on phones, landscape gives the game more room.</li></ul>"
            ),
        ]
        idx = int(hashlib.md5(game["slug"].encode()).hexdigest(), 16) % len(variants)

        free = (
            f"Yes — {esc(title)} is free to play here and needs no account. There is nothing to install: "
            f"the game runs in the browser tab. AZ Games is ad-supported, which is what keeps the catalogue free; "
            f"the ad slots sit around the player, never on top of it."
        )

        return {
            "intro": esc(intro) if "<" not in intro else intro,
            "how_to": variants[idx],
            "free": free,
        }

    def build_game(self, game: dict) -> None:
        cat = self.cat_by_slug.get(game["category"])
        cat_name = cat["name"] if cat else "Games"
        cat_slug = cat["slug"] if cat else "casual-games"
        copy = self.game_copy(game)

        pool = [g for g in (cat["games"] if cat else self.games) if g["slug"] != game["slug"]]
        related = pick(pool, game["slug"], self.build["relatedCount"])

        # The category already appears in the meta bar above; a second chip for
        # the same fact is noise.
        meta_extra = ""

        body = self.game_tpl
        body = body.replace("{{TITLE}}", esc(game["title"]))
        body = body.replace("{{SLUG}}", game["slug"])
        body = body.replace("{{CAT_NAME}}", esc(cat_name))
        body = body.replace("{{CAT_SLUG}}", cat_slug)
        body = body.replace("{{EMBED}}", esc(game["embed"]))
        body = body.replace("{{META_EXTRA}}", meta_extra)
        body = body.replace("{{INTRO}}", copy["intro"])
        body = body.replace("{{HOW_TO}}", copy["how_to"])
        body = body.replace("{{FREE_LINE}}", copy["free"])
        body = body.replace("{{CAT_BLURB}}", esc(CATEGORY_BLURB.get(cat_slug, "the same shelf, different game.")))
        body = body.replace("{{EXTRA_SECTION}}", "")
        body = body.replace("{{RELATED}}", "".join(self.card(g) for g in related))
        body = body.replace("{{AD_UNDER_PLAYER}}", self.ad_slot("gameUnderPlayer"))

        title = f"{game['title']} — Play Free Online | AZ Games"
        description = (game.get("meta") or "").split("|")[0].strip()
        if len(description) < 60:
            description = f"Play {game['title']} free in your browser — no download, no login. {cat_name} on AZ Games."
        description = description[:158]

        schema = json.dumps(
            {
                "@context": "https://schema.org",
                "@type": "VideoGame",
                "name": game["title"],
                "url": f"{self.domain}/play/{game['slug']}/",
                "image": f"{self.domain}/img/game/{game['slug']}.webp",
                "genre": cat_name,
                "gamePlatform": "Browser",
                "applicationCategory": "Game",
                "operatingSystem": "Any",
                "isFamilyFriendly": True,
                "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
            },
            separators=(",", ":"),
        )
        crumbs = json.dumps(
            {
                "@context": "https://schema.org",
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": self.domain + "/"},
                    {"@type": "ListItem", "position": 2, "name": cat_name, "item": f"{self.domain}/category/{cat_slug}/"},
                    {"@type": "ListItem", "position": 3, "name": game["title"],
                     "item": f"{self.domain}/play/{game['slug']}/"},
                ],
            },
            separators=(",", ":"),
        )
        schema = (f'<script type="application/ld+json">{schema}</script>'
                  f'<script type="application/ld+json">{crumbs}</script>')

        self.write(f"/play/{game['slug']}/",
                   self.render(body, title=title, description=description,
                               path=f"/play/{game['slug']}/", body_class="game-play-page",
                               schema=schema, og_type="article",
                               og_image=f"/img/game/{game['slug']}.webp"),
                   priority="0.8")

    def pagination(self, current: int, total: int) -> str:
        if total <= 1:
            return ""
        def href(n: int) -> str:
            return "/games/" if n == 1 else f"/games/page/{n}/"
        parts = []
        if current > 1:
            parts.append(f'<a href="{href(current - 1)}" rel="prev">← Prev</a>')
        shown = [n for n in range(1, total + 1) if n == 1 or n == total or abs(n - current) <= 1]
        last = 0
        for n in shown:
            if last and n - last > 1:
                parts.append('<span class="dots">…</span>')
            if n == current:
                parts.append(f'<span class="current" aria-current="page">{n}</span>')
            else:
                parts.append(f'<a href="{href(n)}">{n}</a>')
            last = n
        if current < total:
            parts.append(f'<a href="{href(current + 1)}" rel="next">Next →</a>')
        return f'<nav class="pagination" aria-label="Pagination">{"".join(parts)}</nav>'

    def build_categories(self) -> None:
        for cat in self.cats:
            body = self.list_tpl
            body = body.replace("{{CRUMB}}", esc(cat["name"]))
            body = body.replace("{{H1}}", f"{esc(cat['name'])} — {len(cat['games'])} Free Games")
            body = body.replace("{{SUB}}", esc(cat["blurb"]))
            body = body.replace("{{GRID}}", "".join(self.card(g) for g in cat["games"]))
            body = body.replace("{{PAGINATION}}", "")
            body = body.replace("{{AD_INLINE}}", self.ad_slot("listInline"))

            title = f"{cat['name']} — {len(cat['games'])} Free Online Games | AZ Games"
            description = f"Play {len(cat['games'])} free {cat['name'].lower()} in your browser on AZ Games. No download, no login, instant play."
            schema = json.dumps(
                {
                    "@context": "https://schema.org",
                    "@type": "CollectionPage",
                    "name": cat["name"],
                    "url": f"{self.domain}/category/{cat['slug']}/",
                    "mainEntity": {
                        "@type": "ItemList",
                        "numberOfItems": len(cat["games"]),
                        "itemListElement": [
                            {"@type": "ListItem", "position": i, "url": f"{self.domain}/play/{g['slug']}/",
                             "name": g["title"]}
                            for i, g in enumerate(cat["games"], 1)
                        ],
                    },
                },
                separators=(",", ":"),
            )
            self.write(f"/category/{cat['slug']}/",
                       self.render(body, title=title, description=description,
                                   path=f"/category/{cat['slug']}/", body_class="category-page",
                                   schema=f'<script type="application/ld+json">{schema}</script>'),
                       priority="0.9")

    def build_all_games(self) -> None:
        size = self.build["pageSize"]
        total = max(1, (len(self.games) + size - 1) // size)
        for page in range(1, total + 1):
            chunk = self.games[(page - 1) * size: page * size]
            body = self.list_tpl
            body = body.replace("{{CRUMB}}", "All Games" if page == 1 else f"All Games · page {page}")
            h1 = f"All {len(self.games)} Games" if page == 1 else f"All Games — Page {page}"
            body = body.replace("{{H1}}", h1)
            sub = ("Every game on AZ Games, alphabetically — the same catalogue the categories are cut from."
                   if page == 1 else f"Page {page} of {total}.")
            body = body.replace("{{SUB}}", sub)
            body = body.replace("{{GRID}}", "".join(self.card(g) for g in chunk))
            body = body.replace("{{PAGINATION}}", self.pagination(page, total))
            body = body.replace("{{AD_INLINE}}", self.ad_slot("listInline"))

            path = "/games/" if page == 1 else f"/games/page/{page}/"
            title = "All Games" if page == 1 else f"All Games — Page {page}"
            title = f"{title} — {len(self.games)} Free Browser Games | AZ Games"
            description = f"Browse all {len(self.games)} free browser games on AZ Games, A to Z. No download, no login."
            self.write(path, self.render(body, title=title, description=description, path=path,
                                         body_class="list-page"),
                       priority="0.9" if page == 1 else "0.5")

    def build_search(self) -> None:
        body = self.search_tpl
        body = body.replace("{{GAME_COUNT}}", f"{len(self.games):,}")
        body = body.replace("{{QUERY}}", "")
        body = body.replace("{{HINT}}", "Loading the catalogue…")
        body = body.replace("{{RESULTS}}", "")
        title = f"Search {len(self.games)} Games | AZ Games"
        description = "Search the AZ Games catalogue by name, category or genre. Results filter as you type."
        self.write("/search/", self.render(body, title=title, description=description, path="/search/",
                                           body_class="search-page"),
                   priority="0.4", sitemap=False)

        index = [
            {
                "s": g["slug"],
                "t": g["title"],
                "c": self.cat_by_slug[g["category"]]["name"] if g["category"] in self.cat_by_slug else "Games",
                "n": (g["title"] + " " + g.get("short", "") + " " +
                      (self.cat_by_slug[g["category"]]["name"] if g["category"] in self.cat_by_slug else "")).lower(),
            }
            for g in self.games
        ]
        (DIST / "search-index.json").write_text(json.dumps(index, separators=(",", ":")))

    def build_static(self) -> None:
        year = NOW.year
        email = self.site["email"]
        pages = {
            "/about": (
                "About AZ Games",
                f"""<p>AZ Games is the A-to-Z shelf of the Poki2 network. It exists for one reason: to make a
                browser game reachable in a single click. No launcher, no sign-up, no "install our app" wall.</p>
                <h2>What is on the site</h2>
                <p>{len(self.games)} games across {len(self.cats)} categories — clicker, .io, puzzle, car, shooting,
                sports, adventure, casual, kids and two-player titles. Every game page shows the game first and the
                information second: which shelf it belongs to, what it plays like, and what else is worth a look.</p>
                <h2>How the games run</h2>
                <p>Games are embedded in the page from the studios and distributors that publish them. Nothing is
                installed on your device. AZ Games does not claim ownership of the games themselves; if you are a
                rights holder and something is listed incorrectly, the <a href="/dmca">DMCA page</a> explains how to
                get it removed.</p>
                <h2>How the site is funded</h2>
                <p>Advertising. Ad slots sit around the player, never on top of it. What is collected, and how to
                opt out, is set out in the <a href="/privacy">privacy policy</a>.</p>
                <h2>Contact</h2>
                <p>Corrections, broken games and partnership questions: <a href="mailto:{email}">{email}</a>.</p>""",
            ),
            "/contact": (
                "Contact AZ Games",
                f"""<p>One address per topic, so messages land in the right place.</p>
                <h2>Broken or missing game</h2>
                <p>Tell us the game name and what happens when you press play:
                <a href="mailto:{email}">{email}</a>. Screenshots help.</p>
                <h2>Copyright</h2>
                <p>Rights holders should use the <a href="/dmca">DMCA page</a>, which lists exactly what a notice
                needs to contain.</p>
                <h2>Advertising and partnerships</h2>
                <p><a href="mailto:ads@poki2.online">ads@poki2.online</a></p>
                <h2>Privacy</h2>
                <p><a href="mailto:privacy@poki2.online">privacy@poki2.online</a></p>
                <p>We read everything, but a reply can take a few days.</p>""",
            ),
            "/privacy": (
                "Privacy Policy",
                f"""<p>Last updated: 6 November {year}.</p>
                <h2>What this policy covers</h2>
                <p>AZ Games (azgames.poki2.online) is a game directory. This page explains what is collected when you
                use it, and what is not.</p>
                <h2>What we collect</h2>
                <ul>
                  <li><strong>Nothing you type.</strong> There are no accounts, no comment forms and no newsletter on
                  this site. The search box filters locally, in your browser; the words you type are not sent to us.</li>
                  <li><strong>Standard server logs.</strong> Our host records IP address, user agent and requested URL
                  for security and abuse prevention.</li>
                  <li><strong>Advertising and measurement cookies</strong>, set by Google, described below.</li>
                </ul>
                <h2>Advertising</h2>
                <p>This site is supported by Google AdSense. Google and its partners may use cookies to serve ads based
                on your prior visits to this and other websites. You can opt out of personalised advertising in
                <a href="https://adssettings.google.com/" rel="noopener nofollow">Google Ads Settings</a>, or opt out of
                third-party vendor cookies at <a href="https://www.aboutads.info/choices/" rel="noopener nofollow">aboutads.info</a>.
                Visitors in the EEA, UK and Switzerland are shown a consent choice before personalised ads are used.</p>
                <h2>Embedded games</h2>
                <p>When you press play, the game loads from the studio or distributor that publishes it. That provider
                may set its own cookies and collect data under its own privacy policy, which we do not control. No
                game is loaded until you press play.</p>
                <h2>Children</h2>
                <p>The catalogue includes games suitable for younger players, but the site is not directed at children
                under 13 and we do not knowingly collect personal data from them.</p>
                <h2>Your rights</h2>
                <p>Requests about access, deletion or correction: <a href="mailto:privacy@poki2.online">privacy@poki2.online</a>.</p>""",
            ),
            "/terms": (
                "Terms of Use",
                f"""<p>Last updated: 6 November {year}. By using AZ Games you agree to these terms.</p>
                <h2>The service</h2>
                <p>AZ Games is a free directory of browser games. It is provided as-is, without warranty of any kind.
                Games may be changed or removed by their publishers at any time, and a listing here is not a promise
                that a game will always work.</p>
                <h2>Acceptable use</h2>
                <ul>
                  <li>Do not attempt to disrupt the site, scrape it at a rate that degrades service for others, or
                  bypass security controls.</li>
                  <li>Do not use the site where doing so would break local law.</li>
                  <li>Game content belongs to its publishers; nothing here grants you a licence to redistribute it.</li>
                </ul>
                <h2>Advertising</h2>
                <p>The site is funded by advertising. Blocking ads is allowed, but it is what pays for the catalogue.</p>
                <h2>Liability</h2>
                <p>To the extent permitted by law, AZ Games is not liable for indirect or consequential loss arising
                from use of the site or of any game linked from it.</p>
                <h2>Changes</h2>
                <p>These terms may be updated; the date above is the version in force.</p>""",
            ),
            "/dmca": (
                "Copyright &amp; DMCA",
                f"""<p>AZ Games links to and embeds games published by third parties. It does not host game files.</p>
                <h2>If you are a rights holder</h2>
                <p>Send a notice to <a href="mailto:dmca@poki2.online">dmca@poki2.online</a> containing:</p>
                <ul>
                  <li>Identification of the copyrighted work you believe is infringed.</li>
                  <li>The exact URL on this site where the material appears.</li>
                  <li>Your name, address, telephone number and email address.</li>
                  <li>A statement that you have a good-faith belief the use is not authorised by the rights holder,
                  its agent or the law.</li>
                  <li>A statement, under penalty of perjury, that the information is accurate and that you are the
                  rights holder or authorised to act for them.</li>
                  <li>Your physical or electronic signature.</li>
                </ul>
                <h2>What happens next</h2>
                <p>Valid notices are actioned promptly: the listing is removed from the catalogue and from the sitemap.
                Because the games are embedded rather than hosted here, we may also need to pass the notice to the
                publisher that serves the file.</p>
                <h2>Counter-notice</h2>
                <p>If your listing was removed in error, the same address accepts counter-notices with the same level
                of detail.</p>""",
            ),
        }

        for path, (title, body_html) in pages.items():
            body = self.static_tpl
            body = body.replace("{{TITLE}}", title)
            body = body.replace("{{BODY}}", body_html)
            plain = re.sub(r"<[^>]+>", " ", body_html)
            description = re.sub(r"\s+", " ", plain).strip()[:155]
            self.write(path, self.render(body, title=f"{title} | AZ Games", description=description,
                                         path=path, body_class="static-page"), priority="0.5",
                       file=path.lstrip("/") + ".html")

    def build_misc(self) -> None:
        # 404
        body = '<div class="page-wrap"><h1>404 — page not found</h1><p>That game may have been renamed or removed. ' \
               'Try the full catalogue:</p><p><a class="btn btn-primary" href="/games/">Browse all games →</a></p></div>'
        (DIST / "404.html").write_text(
            self.render(body, title="Page not found | AZ Games", description="Page not found.",
                        path="/404.html", body_class="error-page")
        )

        # sitemap
        today = NOW.isoformat()
        urls = []
        for path, priority in self.written:
            urls.append(
                f"<url><loc>{self.domain}{path}</loc><lastmod>{today}</lastmod>"
                f"<changefreq>{'daily' if path == '/' else 'weekly'}</changefreq>"
                f"<priority>{priority}</priority></url>"
            )
        (DIST / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(urls) + "\n</urlset>\n"
        )

        (DIST / "robots.txt").write_text(
            "User-agent: *\n"
            "Allow: /\n"
            "Disallow: /search/\n"
            "\n"
            f"Sitemap: {self.domain}/sitemap.xml\n"
        )

        if self.ads.get("enabled"):
            (DIST / "ads.txt").write_text(
                f"google.com, {self.site['adsTxtPub']}, DIRECT, {self.site['adsTxtAuth']}\n"
            )

        (DIST / "_headers").write_text(
            "# AZ Games — Cloudflare Pages headers\n"
            "/*\n"
            "  Strict-Transport-Security: max-age=31536000; includeSubDomains\n"
            "  X-Content-Type-Options: nosniff\n"
            "  Referrer-Policy: strict-origin-when-cross-origin\n"
            "  Permissions-Policy: camera=(), microphone=(), geolocation=()\n"
            "\n"
            "/img/*\n"
            "  Cache-Control: public, max-age=604800, stale-while-revalidate=86400\n"
            "\n"
            "/css/*\n"
            "  Cache-Control: public, max-age=86400\n"
            "\n"
            "/search-index.json\n"
            "  Cache-Control: public, max-age=3600\n"
        )

        # Old paths on this domain: the previous build served .html static pages
        # and /images/games/*.png covers.
        (DIST / "_redirects").write_text(
            "/index.html / 301\n"
            "/blog.html /games/ 301\n"
            "/blog/ /games/ 301\n"
            "/games/page/1/ /games/ 301\n"
        )

        # assets
        (DIST / "css").mkdir(exist_ok=True)
        css = MAIN_SITE_CSS.read_text() + "\n\n" + (SRC / "styles" / "extra.css").read_text()
        (DIST / "css" / "style.css").write_text(css)
        (DIST / "app.js").write_text((SRC / "js" / "app.js").read_text())

        (DIST / "favicon.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="AZ Games">'
            '<rect width="64" height="64" rx="14" fill="#0b0b18"/>'
            '<path d="M13 46 L24 18 h6 l11 28 h-6.2 l-2.4-6.6 H21.6 L19.2 46 z" fill="#22d3ee"/>'
            '<path d="M23.4 34.4 h7.2 L27 24.8 z" fill="#0b0b18"/>'
            '<path d="M40 20 h16 v5.2 L45.8 41.2 H56 V46 H39.4 v-5.2 L50.8 24.8 H40 z" fill="#a855f7"/>'
            "</svg>"
        )

        img_dir = DIST / "img" / "game"
        if img_dir.exists():
            shutil.rmtree(img_dir)
        img_dir.mkdir(parents=True)
        for webp in (DATA / "img").glob("*.webp"):
            shutil.copy2(webp, img_dir / webp.name)

    def run(self, keep: bool = False) -> None:
        if DIST.exists() and not keep:
            shutil.rmtree(DIST)
        DIST.mkdir(parents=True, exist_ok=True)

        self.build_home()
        for game in self.games:
            self.build_game(game)
        self.build_categories()
        self.build_all_games()
        self.build_search()
        self.build_static()
        self.build_misc()

        pages = len(list(DIST.rglob("*.html")))
        size = sum(f.stat().st_size for f in DIST.rglob("*") if f.is_file())
        print(f"built {pages} pages, {len(list((DIST / 'img' / 'game').glob('*.webp')))} images, "
              f"{size / 1e6:.1f} MB")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true", help="do not wipe dist/ first")
    args = ap.parse_args()
    Site().run(keep=args.keep)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
