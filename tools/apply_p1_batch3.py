#!/usr/bin/env python3
"""
apply_p1_batch3.py -- P1 batch 3: Kids Games.

Scope: all 56 Kids Games entries whose `short` was still a verbatim copy of the
azgames.io source description. Kids Games is the largest remaining block
(56 of 234 leftovers) and it is where most of the "crawled - not indexed"
weight sits, so it goes next after Clicker.

Acceptance gate (same as batch 2): no shared *consecutive* word run of 5+ with
the original `short`. SequenceMatcher is useless here because proper nouns
("Cuby Road", "Ice Baby Quest", "Fireboy and Watergirl") dominate the ratio.

Single documented exception: `<title> is a/an` — the title cannot be renamed and
"is a" is the only English way to introduce a game, so this run is structurally
unavoidable. It is reported as BENIGN, not as an overlap.

Usage:
    python3 tools/apply_p1_batch3.py          # dry run + overlap report
    python3 tools/apply_p1_batch3.py --apply  # write data/catalog.json
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "data" / "catalog.json"
BACKUP = ROOT / "data" / ".catalog-pre-p1-batch3.json"

REWRITES: dict[str, str] = {
    "animal-craft":
        "Animal Craft mixes creature-breeding with survival: splice two animals "
        "into a hybrid, then take the result out to fight and see how long it lasts.",
    "astro-tycoon":
        "Astro Tycoon is idle mining in space: work the nearest rock for minerals, "
        "bank what comes back, and push the operation toward the farthest planet.",
    "bottle-hop":
        "Bottle Hop flips a plastic bottle across rooms full of furniture — one tap "
        "per hop, and it has to come down flat on the next ledge.",
    "bottle-jump":
        "Bottle Jump chains upward hops — every jump has to finish with the bottle "
        "standing upright, or the run is over.",
    "bounce-path":
        "Bounce Path sets a small dark blob moving to the beat: tap in time and the "
        "platforms appear where the music says they should.",
    "bounce-up":
        "Bounce Up keeps a ball climbing between ledges: bounce, land, repeat, and "
        "never miss the next edge.",
    "bucket-smash":
        "Bucket Smash hands you an oversized saw blade: cut walls down brick by brick "
        "and sell the debris to pay for upgrades.",
    "chicken-flip":
        "Chicken Flip sends a small chicken down a hill, tumbling over whatever is "
        "in the way and trying not to stop.",
    "city-brawl":
        "City Brawl is street fighting in short bursts: punch, kick, chain combos, "
        "and clear the gang holding the block.",
    "color-jump":
        "Color Jump asks you to read the shape and match its colour before it "
        "arrives — wrong shade, run over.",
    "color-rhythm":
        "Color Rhythm pairs reflex with timing: switch shade on the beat and stay "
        "alive through the pattern.",
    "color-rush":
        "Color Rush is colour-switching at speed — change to the matching shade "
        "before the wall reaches you.",
    "cowboy-safari":
        "Cowboy Safari has you lassoing wildlife at a gallop and driving the catch "
        "back to a zoo you build yourself.",
    "crazy-bull-city":
        "Crazy Bull City puts you inside a bull in a destructible city: charge, "
        "smash, and count what is still standing afterwards.",
    "crazy-shark":
        "Crazy Shark starts you small and hungry: eat, grow, and climb the ocean "
        "food chain until nothing else is a threat.",
    "cuby-road":
        "Cuby Road walks a cube across broken ground and scores it by distance — the "
        "strip never ends, it just gets harder to survive.",
    "cuby-road-halloween":
        "Cuby Road Halloween keeps the cube-and-obstacles run intact but dresses the "
        "track for the season.",
    "dancing-beat":
        "Dancing Beat routes a ball through mazes that shift on the beat — click on "
        "the downbeat to open the way forward.",
    "dino-age":
        "Dino Age is a defence line with dinosaurs: hold the egg against waves of "
        "humans using ranged shots and units you spawn.",
    "dino-dash-3d":
        "Dino Dash 3D rebuilds the browser's offline T-Rex runner in three "
        "dimensions: jump, duck, and last one more stretch.",
    "duck-life":
        "Duck Life turns a farm duck into a racer: train it between races, then "
        "put it on the track against the field.",
    "escape-bear":
        "Escape Bear has a bear breaking its friends out of a hive: sneak past the "
        "guards, fight the bees, and get everyone out.",
    "fireboy-and-watergirl":
        "Two elements, two players: Fireboy can cross lava but not water, Watergirl "
        "the reverse, so each of you opens the way for the other through the temple.",
    "flamy-dash":
        "Flamy Dash is a one-button swing through a dark cave — hook the fireball, "
        "release at the right moment, keep the chain alive.",
    "flipping-master":
        "Flipping Master moves heroes tile by tile: flip the board, line up the "
        "strike, and use abilities to break the enemy formation.",
    "flying-ball":
        "Flying Ball is a downhill ball run on aerial tracks: steer, avoid the "
        "traps, and hold the line as long as possible.",
    "flying-kong":
        "Flying Kong puts a gorilla in the air above the jungle canopy: dodge "
        "obstacles, gather bananas, stay airborne.",
    "forest-mouse":
        "Forest Mouse drops the camera to rodent height: explore a forest that is far "
        "bigger than you are, gather what you find, and stay clear of the dangers.",
    "hyper-tunnel":
        "Hyper Tunnel threads a ship through corridors that keep narrowing: small "
        "steering inputs, no wall contact.",
    "ice-baby-quest":
        "Ice Baby Quest is a deliberately odd 3D scavenger hunt — wander a strange "
        "world, talk to its NPCs, and track the Ice Baby down.",
    "ice-baby-quest-2":
        "Ice Baby Quest 2 turns the hunt into a confrontation: find Ice Age Baby and "
        "finish the fight.",
    "lift-off":
        "Lift Off is rocket staging by the second: release each stage at the right "
        "height and trade fuel for altitude.",
    "loot-and-scoot":
        "Loot and Scoot follows a bank clerk who walks out with the cash: grab "
        "coins, dodge whatever is chasing you, and keep moving.",
    "madness-lab":
        "Madness Lab runs minions through randomised test rooms, testing one "
        "ability at a time to see which one survives.",
    "neon-leap":
        "Neon Leap swings a stickman across glowing geometry — time each jump to the "
        "shape ahead of you.",
    "omnom-jump":
        "Om Nom Jump stacks blocks under a falling candy-eater: keep building "
        "upward, climb higher, and stay ahead of the starving sharks.",
    "orbit-dash":
        "Orbit Dash flies a single coloured line up a vertical course: small "
        "corrections, long runs.",
    "ragdoll-launcher":
        "Ragdoll Launcher fires a limp body out of a cannon: set the angle, upgrade "
        "the launch, and measure the distance.",
    "red-rush":
        "Red Rush is reflex testing at speed — pilot a fast craft through whatever "
        "the track throws next.",
    "rooftop-rush":
        "Rooftop Rush skates a line of roofs with helicopters overhead: hop the "
        "gaps, scoop coins, and put the money into speed.",
    "santa-run":
        "Santa Run is a seasonal runner: keep Santa moving through snow and "
        "Christmas scenery without hitting anything.",
    "shooter-hero":
        "Shooter Hero is target practice with progression: aim, fire, score, then "
        "unlock the next character.",
    "slope-xtreme":
        "Slope Xtreme takes the downhill ball formula and raises the speed: stay on "
        "the track while the track keeps tilting away.",
    "space-road":
        "Space Road runs a glowing route through open space and asks you to follow "
        "it cleanly — a short bright arcade run rather than a long campaign.",
    "sprunki":
        "Sprunki is a fan-made Incredibox variant: drag the characters onto the "
        "stage, stack their loops, and build a mix you can share.",
    "sprunki-jump":
        "Sprunki Jump takes the character sideways through coloured worlds: leap the "
        "gaps, grab the rewards on the way.",
    "stickman-slash":
        "Stickman Slash is a side-scrolling ninja brawler: cut through enemies, "
        "learn the boss patterns, and fight with no connection at all.",
    "tap-road":
        "Tap Road rolls a neon ball down a track that turns without warning — tap to "
        "switch lanes and keep the ball intact.",
    "tap-road-beat":
        "Tap Road Beat adds a soundtrack to the same lane-switching run: turns "
        "arrive on the beat, gems sit between them.",
    "tap-rush":
        "Tap Rush rolls a small ball over an obstacle course where clean lines score "
        "better than risky ones.",
    "tiny-fishing":
        "Tiny Fishing is a cast-and-upgrade loop: drop the hook deeper, sell the "
        "catch, and buy gear that reaches further.",
    "town-run":
        "Town Run follows Tom the cat chasing a raccoon through a town that never "
        "stops scrolling.",
    "tube-fall":
        "Tube Fall drops a fluffy creature down a tube: level after level of "
        "falling, steering, and not clipping the sides.",
    "vex-3":
        "Vex 3 is a precision platformer: run, wall-jump, and clear trap rooms built "
        "to kill on the first attempt.",
    "wyrmdash":
        "Wyrmdash puts the princess on a dragon and sends her after revenge: fly "
        "fast and burn whatever is in front of you.",
    "ziggy-road":
        "Ziggy Road rolls a ball along a platform that zig-zags and narrows — the "
        "edges are the entire challenge.",
}

TOKEN = re.compile(r"[a-z0-9']+")


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
    """`<title> is a/an` cannot be avoided: the title is fixed, "is a" is grammar."""
    title_tokens = TOKEN.findall(slug.replace("-", " ").lower())
    p = TOKEN.findall(phrase.lower())
    core = p[:-2] if p[-2:] in (["is", "a"], ["is", "an"]) else None
    return core is not None and core == title_tokens[-len(core):]


def main() -> int:
    apply = "--apply" in sys.argv
    catalog = json.loads(CATALOG.read_text())
    games = catalog if isinstance(catalog, list) else catalog["games"]
    by_slug = {g["slug"]: g for g in games}

    missing = [s for s in REWRITES if s not in by_slug]
    if missing:
        print(f"ERROR: slugs not in catalog: {missing}")
        return 1
    wrong_cat = [s for s in REWRITES if by_slug[s].get("category") != "kids-games"]
    if wrong_cat:
        print(f"ERROR: not kids-games: {wrong_cat}")
        return 1

    worst = 0
    benign: list[str] = []
    # The gate must always compare against the PRE-batch baseline. After --apply
    # the catalog already holds the new text, so comparing to its own `short`
    # would report the rewrite as a 100% overlap with itself.
    baseline: dict[str, str] = {}
    if BACKUP.exists():
        bcat = json.loads(BACKUP.read_text())
        bgames = bcat if isinstance(bcat, list) else bcat["games"]
        baseline = {g["slug"]: g["short"] for g in bgames}

    for slug, new in REWRITES.items():
        old = baseline.get(slug, by_slug[slug]["short"])
        run, phrase = longest_shared_run(old, new)
        if run >= 5 and is_benign_title_phrase(slug, phrase):
            benign.append(f"{slug} (\"{phrase}\")")
            continue
        worst = max(worst, run)
        flag = "  <-- OVERLAP" if run >= 5 else ""
        print(f"{slug:<26} run={run}{flag}")
        if run >= 4:
            print(f"    shared: \"{phrase}\"")
            print(f"    old: {old}")
            print(f"    new: {new}")

    print(f"\n{len(REWRITES)} rewrites staged, longest non-benign shared run = {worst}")
    if benign:
        print("Benign title phrases (allowed):")
        for b in benign:
            print(f"  - {b}")

    if not apply:
        print("\nDRY RUN — use --apply to write.")
        return 0

    if not BACKUP.exists():
        shutil.copy2(CATALOG, BACKUP)
        print(f"backup -> {BACKUP.name}")
    for slug, new in REWRITES.items():
        by_slug[slug]["short"] = new
    CATALOG.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")
    print(f"applied: {len(REWRITES)} shorts rewritten.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())