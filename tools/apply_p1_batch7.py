#!/usr/bin/env python3
"""
apply_p1_batch7.py -- P1 batch 7: Sports Games + Shooting Games (54 slots).

52 rewrites, 2 flagged. The flags follow the same rule as batch 6: if the source
description names a different game, rewriting it would launder a data defect
into plausible-looking fresh copy, so it stays visible instead.

    power-surfer  -> source text is "Play Power Hover to soar through futuristic
                     skies ... hoverboard game". Power Hover is a different title.
    steel-legion  -> source text is "Play Hills of Steel and command powerful
                     tanks ...". Hills of Steel is a different title.

Noted but rewritten (source is merely sloppy, the game is identifiable):
    fury-chase    -> source spells it "Furry Chase"; `fury-chase-2` exists in this
                     catalog and was rewritten in batch 6, so the family is known.

Usage:
    python3 tools/apply_p1_batch7.py          # dry run + gate
    python3 tools/apply_p1_batch7.py --apply  # write data/catalog.json
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
BACKUP = ROOT / "data" / ".catalog-pre-p1-batch7.json"

FLAGGED_FOR_MANUAL: dict[str, str] = {
    "power-surfer": "source description is Power Hover's, a different title",
    "steel-legion": "source description is Hills of Steel's, a different title",
}

REWRITES: dict[str, str] = {
    # --- sports ---
    "arcade-tennis":
        "Arcade Tennis is a cartoony court game: place the serve, time the return, "
        "and out-hit an opponent who never gives the same ball twice.",
    "ball-orbit":
        "Ball Orbit is a distance contest: line up the swing, meet the ball "
        "cleanly, and put the money into a bat that sends it further.",
    "bat-smash":
        "Bat Smash comes down to timing — one swing at the right moment, one "
        "measurement of distance, and coins to spend on the next bat.",
    "dunk-clash":
        "Dunk Clash is one-on-one basketball in short bursts: trade baskets with a "
        "single opponent and be ahead when the clock runs out.",
    "dunk-dash":
        "Dunk Dash is chaotic basketball: take the ball, drive hard, and finish "
        "above the rim while the defence is still turning.",
    "flip-rush":
        "Flip Rush is a ragdoll athlete thrown into the air: the score comes from "
        "how many rotations you can complete before the landing.",
    "hoop-legends":
        "Hoop Legends is 3D basketball with a roster behind it: shoot, play the "
        "modes, and customise the team as you go.",
    "mr-flip":
        "Mr Flip launches a gymnast off the apparatus and lets physics grade the "
        "routine — more rotations, cleaner landing, better score.",
    "orbit-kick":
        "Orbit Kick is a football distance test: strike it right, watch it travel, "
        "and spend the coins on a stronger boot.",
    "perfect-orbit":
        "Perfect Orbit is a one-button hitting game: judge the approach, connect, "
        "and see how far the ball carries across the terrain.",
    "ragdoll-flip":
        "Ragdoll Flip is jump-and-tumble scoring: launch, spin as many times as "
        "you can, and collect enough to open the next location.",
    "ramp-xtreme":
        "Ramp Xtreme is a stunt course on two wheels: hit the ramps, land the "
        "flips, and unlock the faster bikes.",
    "ski-frenzy":
        "Ski Frenzy is a downhill escape: pick Sven or Evana, carve the slope, and "
        "stay ahead of the avalanche behind you.",
    "slap-champions":
        "Slap Champions settles things one slap at a time: read the timing of the "
        "opponent's swing and land yours first.",
    "slope-2":
        "Slope 2 puts the ball back on the downhill run with a harder set of "
        "obstacles: keep the line, absorb the speed, and stay on the track.",
    "slope-rider":
        "Slope Rider trades the ball for a sled: ride the snowy forest, hold the "
        "line through the ice, and dodge what the terrain puts in the way.",
    "slope-rider-3d":
        "Slope Rider 3D turns the sled run into three dimensions: trees, logs and "
        "gaps arrive without warning, and the rewards sit where it is riskiest to "
        "reach for them.",
    "snow-rider-3d":
        "Snow Rider 3D is snowboarding for the sake of the line: ride the mountain "
        "freely and string together the runs you want to make.",
    "snow-road":
        "Snow Road is a sled run down an obstacle course: speed is easy to find, "
        "staying upright is the hard part.",
    "snow-road-3d":
        "Snow Road 3D is racing on ice: hold the throttle, thread the obstacles, "
        "and take the jumps the track offers.",
    "snowtrail-legends":
        "Snowtrail Legends is a snowboarding descent through a trail that keeps "
        "changing — falling trees, swaying bridges, and icy drops in the same run.",
    "speed-legends":
        "Speed Legends is sprint racing: get off the line, hold form down the "
        "track, and finish in front.",
    "stellar-burner":
        "Stellar Burner is ship flying at speed: thread a course that gets harder "
        "each run and keep the hull off the walls.",
    "swipe-ball":
        "Swipe Ball is a physics throwing game: read the arc, put the ball in the "
        "basket, and carry the rhythm into the next level.",
    "wave-rider":
        "Wave Rider is an endless surf run: take the board or the jet ski, ride "
        "the swell, and steer around whatever is in the water.",
    "white-horizon":
        "White Horizon follows a snowboarder down open mountains and alpine "
        "forests, with the scenery doing as much work as the riding.",

    # --- shooting ---
    "blocky-hunter":
        "Blocky Hunter is wave defence against voxel zombies: hold the position, "
        "work the weapons you have, and save the heavy fire for the bosses.",
    "bricky-break":
        "Bricky Break is brick-by-brick clearing with a chain reaction at the end "
        "of it: launch, break, and collect the balls that come back.",
    "chicken-jockey-combat":
        "Chicken Jockey Combat is first-person survival: the base is yours to "
        "hold, the waves keep coming, and the ammo has to last.",
    "dead-strike":
        "Dead Strike is first-person zombie clearing with a story attached: take "
        "the missions, run the quests, and push the outbreak back.",
    "dude-theft-auto":
        "Dude Theft Auto is an open city with several modes and no fixed script: "
        "pick what you want to do and do it.",
    "escape-drive":
        "Escape Drive is monster trucks over bad ground: climb the hills, read the "
        "traps, and keep away from the cars chasing you.",
    "escape-road-city-2":
        "Escape Road City 2 continues the city getaway: work the traffic, dodge "
        "what is parked in the road, and get clear of the pursuit.",
    "fury-chase":
        "Fury Chase is the other side of a heist: collect the crew after the job "
        "and drive them out from under the police response.",
    "golf-hit":
        "Golf Hit is a driving-range game: find the sweet spot on the club face "
        "and send the ball as far down the fairway as it will go.",
    "kickback-dash":
        "Kickback Dash is a launch game with a weapon in it: fly the thing as far "
        "as the physics allow and keep going.",
    "knock-balls":
        "Knock Balls is structural demolition with a ball launcher: pick the weak "
        "point and bring the whole thing down.",
    "mad-racers":
        "Mad Racers mixes racing with combat: hold the lead on the track and clear "
        "the rivals who try to take it off you.",
    "ragdoll-arena":
        "Ragdoll Arena boxes its fighters into small side-view arenas: the physics "
        "does half the work, so no two rounds play out the same way.",
    "ragdoll-playground":
        "Ragdoll Playground is a physics sandbox with no objective: spawn what you "
        "like across the open maps and see how it behaves.",
    "rebound-shooter":
        "Rebound Shooter is zombie clearing built on angles: bank the shot, solve "
        "the layout, and take the undead out with as few rounds as possible.",
    "retro-blaster":
        "Retro Blaster is bullet-hell in the old arcade style: weave the patterns, "
        "collect the power-ups, and chase the high score.",
    "rocket-fortress":
        "Rocket Fortress mixes clicking with army building: fire the missiles, "
        "recruit the units, and keep upgrading as the bosses scale up.",
    "shooter-sky":
        "Shooter Sky is aim-and-destroy with an odd target list — consoles, "
        "phones, and whatever else the game puts in the sky.",
    "spear-warzone":
        "Spear Warzone is a stickman fighter with a spear: out-range the archers, "
        "break the swordsmen, and hold the line.",
    "speed-shooter":
        "Speed Shooter is first-person shooting where the first accurate shot "
        "usually decides the exchange.",
    "spin-blast":
        "Spin Blast gives you a spinning tool and a set of colour-coded targets: "
        "match the colour, clear the zone.",
    "stick-hero-rpg":
        "Stick Hero RPG is a stickman warrior against waves of monsters: survive "
        "the push and take the levels as they come.",
    "undead-corridor":
        "Undead Corridor is close-quarters survival: the space is narrow, the "
        "zombies are not, and there is nowhere to fall back to.",
    "undead-invasion":
        "Undead Invasion scrolls sideways through a pixel apocalypse: the waves do "
        "not stop coming, so the line has to hold.",
    "wing-smash":
        "Wing Smash is a fighter plane run through 3D terrain: fly the route, "
        "avoid the ground, and put bombs on the enemy bases.",
    "zombie-rising":
        "Zombie Rising is third-person shooting through a dark pixel city: clear "
        "the streets, keep moving, and outlast the outbreak.",
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
    wrong = [s for s in REWRITES if by_slug[s].get("category") not in
             ("sports-games", "shooting-games")]
    if wrong:
        print(f"ERROR: outside the two target categories: {wrong}")
        return 1
    bad = set(REWRITES) & set(FLAGGED_FOR_MANUAL)
    if bad:
        print(f"ERROR: flagged entries must not be rewritten: {sorted(bad)}")
        return 1

    baseline = (
        load_baseline(BACKUP) if BACKUP.exists()
        else {s: by_slug[s]["short"] for s in REWRITES}
    )

    print(f"{len(REWRITES)} rewrites staged across sports + shooting "
          f"({len(FLAGGED_FOR_MANUAL)} flagged, not rewritten)")
    rc = run_gate(REWRITES, baseline, verbose=True)
    if rc:
        return rc

    print("\nFlagged for manual verification (not rewritten):")
    for s, why in FLAGGED_FOR_MANUAL.items():
        print(f"  - {s}: {why}")

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