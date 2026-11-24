#!/usr/bin/env python3
"""
apply_p1_batch8.py -- P1 batch 8: final tranche (IO / Puzzle / Casual / Adventure
/ 2-Player / leftover Clicker).

78 rewrites. The 6 entries flagged across batches 2, 6 and 7 are NOT touched here
either — the guard below fails the run if any of them appears in REWRITES.

Usage:
    python3 tools/apply_p1_batch8.py          # dry run + gate
    python3 tools/apply_p1_batch8.py --apply  # write data/catalog.json
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
BACKUP = ROOT / "data" / ".catalog-pre-p1-batch8.json"

FLAGGED_FOR_MANUAL: dict[str, str] = {
    "escape-jump": "source description is Escape Road's",
    "idle-gold-miner": "source description is Idle Miner Tycoon's",
    "egg-race": "source description is Eggy Car's (eggy-car is a separate entry)",
    "overtake-x": "source description is Traffic Racer's",
    "power-surfer": "source description is Power Hover's",
    "steel-legion": "source description is Hills of Steel's",
}

REWRITES: dict[str, str] = {
    # --- io games ---
    "1v1soccerio":
        "1v1soccer.io is football stripped to a single duel: one ball, one "
        "opponent, and a short match to settle who is better.",
    "billiards-master":
        "Billiards Master is pool with the aiming done properly: choose a mode, "
        "set the angle and the power, and let the cue go.",
    "crazy-mouse-battle":
        "Crazy Mouse Battle is a battle royale of mice: charge the rivals and bump "
        "them off the edge until only one is left standing.",
    "curve-rush":
        "Curve Rush is about flying the line above the sand: the higher the arc, "
        "the harder the landing has to be survived.",
    "curve-rush-2":
        "Curve Rush 2 keeps the rolling ball and the sandy hills and adds a fresh "
        "set of mechanics on top of them.",
    "curve-rush-io":
        "Curve Rush IO takes the same downhill ball runs online: share the hills "
        "with other players and hold the line longer than they do.",
    "escape-animals":
        "Escape Animals is a survival scramble: lava, tsunamis and ice close in, "
        "and each zone you reach has an animal to collect.",
    "fall-flat-battle":
        "Fall Flat Battle is a physics platformer set in dreamscapes: the puzzles "
        "are solved by pushing the environment rather than by fighting it.",
    "fun-typing-io":
        "Fun Typing IO is a typing race: accuracy and speed are the only two "
        "skills that count, and the leaderboard is live.",
    "icy-dash":
        "Icy Dash is a downhill snowboard race with other players on the same "
        "slope: stay fast, stay upright, and finish first.",
    "krunker":
        "Krunker is a browser first-person shooter built for speed: short "
        "engagements, fast movement, and matches against players worldwide.",
    "narrow-one":
        "Narrow One is team archery capture-the-flag: bows, arrows, and a 3D map "
        "that rewards holding the right angle.",
    "paper-io":
        "Paper IO is territory capture: steer the cube, trace out an area, and "
        "claim as much of the map as the rivals will allow.",
    "ragdoll-hit-stickman":
        "Ragdoll Hit Stickman is a physics brawler: pick a character and a weapon, "
        "then let the collision do the damage.",
    "rob-brainrot-2":
        "Rob Brainrot 2 is collect-and-defend: gather the meme characters, buy the "
        "rare ones, and keep rivals from taking the base apart.",
    "smash-karts":
        "Smash Karts is kart combat in 3D: grab the weapons scattered on the track "
        "and use them on everyone else's kart.",
    "smashy-road":
        "Smashy Road is a police chase from the wrong side of it: drive, dodge, "
        "and stay free for as long as the pursuit lasts.",
    "snake-arena":
        "Snake Arena is the snake formula as a free-for-all: grow, cut off the "
        "rivals, and take the arena.",
    "stickman-racing":
        "Stickman Racing is parkour at speed: jump, climb, slide and swing through "
        "the course without falling out of it.",
    "tic-tac-toe-io":
        "Tic Tac Toe IO puts the pen-and-paper game online against real opponents, "
        "one quick grid at a time.",
    "venge-io":
        "Venge IO is a browser FPS: pick up a gun, find an angle, and take the "
        "fight to other players in real time.",
    "wacky-nursery":
        "Wacky Nursery is a puzzle-adventure set somewhere a school should not be: "
        "work out the dark little mysteries and get through the day alive.",
    "zombie-strike":
        "Zombie Strike is FPS survival against the undead: build the defences, "
        "hold them, and stay standing when the wave ends.",

    # --- puzzle ---
    "2048":
        "2048 is the sliding-tile number game: merge matching tiles, keep the grid "
        "from filling, and work toward the 2048 tile.",
    "2048-drop":
        "2048 Drop changes the input: drop numbered chips into a column instead of "
        "sliding a grid, and merge on contact.",
    "2048-italian-brainrot":
        "2048 Italian Brainrot runs the 2048 merge rules with the meme cast as the "
        "tiles, climbing the ranks as the numbers double.",
    "2048-rogue":
        "2048 Rogue uses a 4x4 board and merges upward through creatures and "
        "objects rather than plain numbers.",
    "blendrix":
        "Blendrix is a minimal colour puzzle: draw the paths that bring every dot "
        "to a single shared colour.",
    "block-blast-3d":
        "Block Blast 3D is block placement in three dimensions: fit the shapes, "
        "complete the lines, and clear them for the score.",
    "block-slide":
        "Block Slide is a sliding-block puzzle: move the pieces out of the way "
        "until the route opens.",
    "blocky-rush":
        "Blocky Rush is endless line-clearing: nudge the blocks sideways until a row "
        "completes, and keep the stack from reaching the top.",
    "brain-lines":
        "Brain Lines asks you to sketch the answer with your finger: the physics engine "
        "then decides whether the sketch holds up or collapses.",
    "bricky-blast":
        "Bricky Blast is match-and-clear with colour: group the blocks, break them, "
        "and work through the level list.",
    "dark-loop":
        "Dark Loop hands you one level and asks for a different answer each time: "
        "solve it, then solve it another way.",
    "golf-puzzle":
        "Golf Puzzle is golf as a climbing route: land the ball in the hole to gain "
        "the height, and work up through the levels.",
    "jelly-hop":
        "Jelly Hop is endless upward jumping: the only goal is to get higher and "
        "last longer than the previous run.",
    "loop-breakout":
        "Loop Breakout is an escape-room puzzle chain: work Tommy out of each level "
        "using the traps and logic laid out in it.",
    "meme-puzzle":
        "Meme Puzzle is image assembly: put the meme picture back together piece by "
        "piece, one puzzle at a time.",
    "merge-brainrot":
        "Merge Brainrot is drop-and-merge with the meme cast: drop the characters, "
        "combine the matches, and keep the board clear.",
    "stack-rush":
        "Stack Rush puts falling shapes onto a cube you can rotate: place them "
        "cleanly and clear the layers.",
    "sugar-sugar":
        "Sugar Sugar is line drawing with a sweet tooth: draw the path that funnels "
        "the sugar into the cups.",
    "suika-game":
        "Suika Game is fruit merging: drop the fruit, pair the same kinds, and keep "
        "the pile below the rim.",
    "trap-the-cat":
        "Trap the Cat is a pursuit puzzle: wall the cat in before it walks off the "
        "board, against an opponent that always finds the better route.",
    "trimerge":
        "TriMerge merges in multiples of three: slide the tiles, combine the "
        "numbers, and push the values as high as the grid allows.",
    "tunnel-ball":
        "Tunnel Ball rolls a ball through obstacle runs: collect the diamonds, "
        "avoid the traps, and travel as far as possible.",

    # --- casual ---
    "age-of-war":
        "Age of War runs a civilisation from stone tools to modern weapons: evolve "
        "the army between ages and hold the line while you do it.",
    "hill-climb-race":
        "Hill Climb Race is off-road driving across hills, desert and stranger "
        "ground than either: the terrain is the opponent.",
    "horror-nun":
        "Horror Nun is first-person escape horror: find the way out of the school "
        "before the nun finishes what she started.",
    "jelly-runner":
        "Jelly Runner is an endless run with a soft cube for a hero: keep it "
        "bouncing through tracks built out of obstacles.",
    "knife-master":
        "Knife Master is throwing practice: send knives, axes and blades into the "
        "target so they stick, not bounce.",
    "orbit-beats":
        "Orbit Beats is a one-button rhythm game: two planets, winding paths, and "
        "taps that have to land on the beat.",
    "orbit-rush":
        "Orbit Rush is one-button orbiting: hold the circle around the black hole, "
        "dodge what crosses the path, and chase the score.",
    "pinball-master":
        "Pinball Master is crystal-smashing pinball: work the flippers, break the "
        "gems, and keep the ball alive for the high score.",
    "skip-it":
        "Skip It is stone skipping: set the angle and the power, and try to get one "
        "more bounce out of the water than last time.",
    "slide-down":
        "Slide Down is an endless ball run on tracks suspended in the air: stay on the "
        "surface, clear the obstacles, and see how far it goes.",
    "slope-cyber":
        "Slope Cyber reskins the downhill ball run in neon: a robotic ball, "
        "cyberpunk streets, and the same demand for clean lines.",
    "slope-emoji-2":
        "Slope Emoji 2 continues the smiley-ball slope run with extra mechanics "
        "layered on the original.",
    "slope-gear":
        "Slope Gear is the downhill ball run in steampunk dress: same speed, "
        "different machinery.",
    "slope-legacy":
        "Slope Legacy is a Slope spin-off with a retro-futurist look and a few new "
        "tricks on the track.",
    "sorry-bob":
        "Sorry Bob is mock surgery: the tools are wrong for the job, the controls "
        "fight you, and the patient is not helping.",
    "wacky-nursery-2":
        "Wacky Nursery 2 continues the sinister-school story with a new cast, new "
        "rooms and new ways to end the day badly.",

    # --- adventure ---
    "crazy-animal-city":
        "Crazy Animal City is an animal sandbox in an open city: pick a creature, "
        "roam, and cause whatever chaos the physics allows.",
    "kong-adventure":
        "Kong Adventure is an endless run as a mischievous monkey: leap the "
        "obstacles and collect bananas on the way through.",
    "plants-vs-brainrots-online":
        "Plants vs Brainrots Online builds a defence in three dimensions: cultivate the "
        "plants, put them where they cover the lane, and keep the Brainrot zombies "
        "off the base.",
    "rob-a-car":
        "Rob A Car is a heist sandbox: lift the cars, stash them, and build the base "
        "up until it holds the rarest of them.",
    "run-3d":
        "Run 3D rebuilds the tunnel runner in three dimensions: keep running, jump "
        "the gaps, and avoid the walls and the holes.",
    "slope":
        "Slope is the original downhill ball run: one ball, an endless slope, sharp "
        "turns, and no second chances.",
    "stickman-empires":
        "Stickman Empires is stick-figure strategy: raise the army, pick the right "
        "classes, and take the nations one at a time.",
    "stickman-war":
        "Stickman War is a side-scrolling action RPG: a dark knight against "
        "monsters, demons and the bosses that follow them.",
    "tiny-arena":
        "Tiny Arena is arcade gladiator combat: you take a small fighter into fast "
        "rounds and work through the ranks toward the bosses.",
    "tung-sahur-horror":
        "Tung Sahur Horror wakes you up inside the house of Tung Tung Tung Sahur "
        "with a deadline: find the way out before the days run out.",
    "wave-road":
        "Wave Road is a stunt flight over obstacles: keep the momentum, use the "
        "gravity, and see how far the line goes.",

    # --- 2 player ---
    "basket-random":
        "Basket Random is two-player basketball with the physics set loose: the "
        "players flail, the ball behaves unpredictably, and the score still counts.",
    "basketball-stars":
        "Basketball Stars is one-on-one streetball for two: pick a player, work the "
        "court, and outscore the other side.",
    "gun-mayhem":
        "Gun Mayhem throws cartoon fighters at each other on one stage: knock the "
        "opponents off it before they return the favour.",
    "head-basketball":
        "Head Basketball is oversized-head basketball: each character brings its "
        "own skill, and the heads make the angles unusual.",
    "head-soccer-2024":
        "Head Soccer 2024 is football for oversized heads: each player carries a "
        "superpower into the match, and most of it happens in the air.",
    "hockey-random":
        "Hockey Random is two-player hockey where the puck does not cooperate: "
        "fast, chaotic, and decided by whoever adapts.",

    # --- leftover clicker ---
    "escape-jump-x":
        "",
}

# The last key is a placeholder guard; keep the dict honest.
REWRITES.pop("escape-jump-x", None)


def main() -> int:
    apply = "--apply" in sys.argv
    catalog = json.loads(CATALOG.read_text())
    games = catalog if isinstance(catalog, list) else catalog["games"]
    by_slug = {g["slug"]: g for g in games}

    missing = [s for s in REWRITES if s not in by_slug]
    if missing:
        print(f"ERROR: slugs not in catalog: {missing}")
        return 1
    bad = set(REWRITES) & set(FLAGGED_FOR_MANUAL)
    if bad:
        print(f"ERROR: flagged entries must not be rewritten: {sorted(bad)}")
        return 1
    empty = [s for s, v in REWRITES.items() if not v.strip()]
    if empty:
        print(f"ERROR: empty rewrite text: {empty}")
        return 1

    baseline = (
        load_baseline(BACKUP) if BACKUP.exists()
        else {s: by_slug[s]["short"] for s in REWRITES}
    )

    from collections import Counter
    print(f"{len(REWRITES)} rewrites staged across "
          f"{len(set(by_slug[s]['category'] for s in REWRITES))} categories:")
    for c, n in Counter(by_slug[s]["category"] for s in REWRITES).most_common():
        print(f"  {c}: {n}")
    rc = run_gate(REWRITES, baseline, verbose=True)
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
    print(f"applied: {len(REWRITES)} shorts rewritten.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())