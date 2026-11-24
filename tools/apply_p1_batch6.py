#!/usr/bin/env python3
"""
apply_p1_batch6.py -- P1 batch 6: Car Games (largest remaining block).

39 rewrites out of 41 remaining verbatim entries in car-games. Two are
DELIBERATELY NOT rewritten because their source description names a different
game — rewriting them would relabel a data defect as fresh copy:

    egg-race    -> source text is "Eggy Car is a game about driving a wobbly car
                   carrying a precious egg", and `eggy-car` is a separate entry
                   in this same catalog. Two pages, one description: either a
                   duplicate game or a mis-extracted slug. Needs a human call.
    overtake-x  -> source text is "Traffic Racer is a high-speed driving game...".
                   No Traffic Racer entry exists here, so the description was
                   lifted from a different title.

Usage:
    python3 tools/apply_p1_batch6.py          # dry run + gate
    python3 tools/apply_p1_batch6.py --apply  # write data/catalog.json
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
BACKUP = ROOT / "data" / ".catalog-pre-p1-batch6.json"

FLAGGED_FOR_MANUAL: dict[str, str] = {
    "egg-race": "source description is Eggy Car's; `eggy-car` is a separate entry with the same game",
    "overtake-x": "source description is Traffic Racer's, a title that does not exist in this catalog",
}

REWRITES: dict[str, str] = {
    "american-truck-driving":
        "American Truck Driving puts you behind the wheel of a rig for a working "
        "day on the road: take the haul, keep it between the lines, and park it "
        "cleanly.",
    "bike-xtreme":
        "Bike Xtreme is a dirt-bike run over rough ground: smooth controls, big "
        "jumps, and a course that keeps testing how well you land.",
    "blocky-overtake-x":
        "Blocky Overtake X is traffic weaving in a voxel world: squeeze past the "
        "block cars, keep the speed up, and finish without a wreck.",
    "blocky-rider":
        "Blocky Rider races voxel motorbikes through city traffic: dodge the "
        "obstacles, stay upright, and try the other modes once the streets clear.",
    "breakout-racing":
        "Breakout Racing is a getaway run with a panda at the wheel: outdrive the "
        "police, scoop up coins, and spend them on the next car.",
    "car-chaos":
        "Car Chaos is a demolition derby in short rounds: take an odd-looking car "
        "into the arena and knock the opposition out of it.",
    "chase-rush":
        "Chase Rush puts you in a getaway car with the police behind it: keep "
        "moving, find the gaps, and last as long as the chase allows.",
    "crafty-car":
        "Crafty Car is workshop work rather than driving: strip a car down, repair "
        "each part, and send it out rebuilt.",
    "crazy-taxi":
        "Crazy Taxi is fare-running: pick up passengers, get them to the marked "
        "stop, and try not to wreck the cab on the way.",
    "deer-adventure":
        "Deer Adventure hands you a deer with an absurdly long neck and a town to "
        "wander — a sandbox with no schedule and nothing you have to do.",
    "doom-rider":
        "Doom Rider mixes driving with combat: drift the tracks, keep the speed, "
        "and deal with the skeletons that want the road to themselves.",
    "drift-boss":
        "Drift Boss is one continuous bend: hold the drift, keep the car on the "
        "road, and do not let it slide off into the void.",
    "drift-hunters":
        "Drift Hunters is a 3D drift sandbox: take a car onto the tracks, hold the "
        "slide through the corners, and tune it between runs.",
    "drift-road":
        "Drift Road runs winding trails that exist to be drifted: link one corner "
        "into the next and keep the car sliding instead of gripping.",
    "eggy-car":
        "Eggy Car is a delivery run with something fragile on the roof: go over "
        "the hills slowly enough that the egg survives the trip.",
    "escape-raid":
        "Escape Raid is a sheriff outrunning a wasteland: drive hard, shake the "
        "pursuers, and keep the vehicle in one piece.",
    "escape-road":
        "Escape Road is one-touch driving: every tap turns the car, and the road "
        "ahead is a chain of traps that has to be threaded.",
    "escape-road-2":
        "Escape Road 2 is the sequel chase — more police behind the car and the "
        "same one-touch steering through city traffic.",
    "escape-road-halloween":
        "Escape Road Halloween keeps the one-touch chase and moves it to a night "
        "city dressed for the season.",
    "escape-road-winter":
        "Escape Road Winter sets the same chase in snow: the city is buried, the "
        "pursuers are still there, and the grip is worse.",
    "escape-vehicles":
        "Escape Vehicles is a police chase with a garage attached: drive to get "
        "away, then put the earnings into a faster car.",
    "fire-flush":
        "Fire Flush casts you as a flying firefighting dog: reach the burning "
        "forest, drop what puts the flames out, and save the trees.",
    "fury-chase-2":
        "Fury Chase 2 is a survival race across a wasteland: speed is the only "
        "defence, and the run ends when the pursuit catches up.",
    "highway-heat":
        "Highway Heat is traffic racing: thread the gaps at speed, bank the "
        "rewards, and put them into the car you actually want.",
    "loop-crash":
        "Loop Crash asks for one thing — keep the car circling and stay clear of "
        "everything else on the loop.",
    "mad-pursuit":
        "Mad Pursuit is a getaway driver under pressure: each level is a police "
        "chase, and surviving it is the whole objective.",
    "mad-trails":
        "Mad Trails is physics-driven off-roading on oversized wheels: climb the "
        "rocks and the hills without tipping over.",
    "mayhem-drive":
        "Mayhem Drive is an open world built for stunts: roam it, pull off what "
        "you can, and spend the coins on a better vehicle.",
    "mountain-road":
        "Mountain Road is a climb: work the car up steep hills and rough ground "
        "toward the highest point on the map.",
    "street-wheelie":
        "Street Wheelie is about holding the front wheel up: ride the maps, chain "
        "the stunts, and spend the points on bike parts.",
    "subway-moto":
        "Subway Moto is first-person motorcycle riding along train tracks: the "
        "corridor is narrow and the obstacles are not forgiving.",
    "tap-drift":
        "Tap Drift is drifting on timing: tap to break the grip, hold the slide "
        "through the corner, and come back faster next time.",
    "traffic-jam-3d":
        "Traffic Jam 3D is dense-traffic racing: find the seam, hold the speed, "
        "and turn the earnings into a better car.",
    "traffic-rally":
        "Traffic Rally sets mission after mission in crowded streets, testing how "
        "precisely you can pass at speed.",
    "traffic-rider":
        "Traffic Rider is first-person bike riding through dense traffic: read the "
        "gaps ahead and keep the rewards coming.",
    "traffic-road":
        "Traffic Road scores you on how cleanly you ride a bike through highway "
        "traffic — no contact, no crash, higher points.",
    "turbo-street":
        "Turbo Street is motorbike racing through crowded streets: pick the fast "
        "line and hold it.",
    "wheelie-master":
        "Wheelie Master is balance and throttle control: hold the wheelie as long "
        "as you can, then unlock a better bike.",
    "wheelie-party":
        "Wheelie Party is a stunt contest on one wheel: get the bike up and keep "
        "it there for as long as the balance holds.",
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
    wrong = [s for s in REWRITES if by_slug[s].get("category") != "car-games"]
    if wrong:
        print(f"ERROR: not car-games: {wrong}")
        return 1
    overlap = set(REWRITES) & set(FLAGGED_FOR_MANUAL)
    if overlap:
        print(f"ERROR: flagged entries must not be rewritten: {sorted(overlap)}")
        return 1

    baseline = (
        load_baseline(BACKUP) if BACKUP.exists()
        else {s: by_slug[s]["short"] for s in REWRITES}
    )

    print(f"{len(REWRITES)} car-games rewrites staged "
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