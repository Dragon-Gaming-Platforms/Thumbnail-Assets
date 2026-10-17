#!/usr/bin/env python3
"""Refresh/check the thumbnail queue using Python's standard library and gh."""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = "Dragon-Gaming-Platforms/Dragon-Gaming-Platforms"
EXTENSIONS = {".svg", ".png", ".webp", ".jpg", ".jpeg", ".gif"}
ROW = re.compile(r"^- `([a-z0-9._-]+)` generate=(true|false)$")
# Prefer screenshots for these recognizable single-file releases, subject to
# asset rights verification. Other single-file games start with original art.
# Games the repository owner has reserved to illustrate personally. Never
# generate or capture artwork for these; they are left out of the queue.
OWNER_RESERVED_IDS = {
    "echoed-path",
}

SCREENSHOT_IDS = {
    "awesometanks2", "balatro", "bloons-td4", "dreadheadparkour",
    "eaglercraft-1-12-2-offline-js", "eaglercraft-1-12-2-offline-wasm",
    "eaglercraft-1-8-8-offline-js", "eaglercraft-1-8-8-offline-wasm",
    "escape-road", "moto-x3m-2", "recoil", "snowrider",
}


def load_catalog(text):
    match = re.search(r"const GAMES_DATA\s*=\s*(\[.*?\]);", text, re.S)
    if not match:
        raise ValueError("Cannot find the JSON GAMES_DATA array")
    games = json.loads(match.group(1))
    ids = [game["id"] for game in games]
    if len(ids) != len(set(ids)):
        raise ValueError("Catalog contains duplicate IDs")
    if any(not re.fullmatch(r"[a-z0-9._-]+", slug) for slug in ids):
        raise ValueError("Catalog contains unsupported IDs")
    return games


def read_queue(path):
    if not path.exists():
        return {}
    flags = {}
    text = path.read_text(encoding="utf-8")
    if "## Queue\n" in text:
        text = text.split("## Queue\n", 1)[1]
    for line in text.splitlines():
        match = ROW.fullmatch(line)
        if match:
            slug, flag = match.groups()
            if slug in flags:
                raise ValueError(f"Duplicate queue ID: {slug}")
            flags[slug] = flag
        elif line.startswith("- `"):
            raise ValueError(f"Malformed queue entry: {line}")
    return flags


def source_ids(directory):
    """Only the flat drop zone counts; CI derivatives are never sources."""
    found = set()
    if not directory.exists():
        return found
    for path in directory.iterdir():
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        if path.name != path.name.lower():
            raise ValueError(f"Source filename must be lowercase: {path.name}")
        if not re.fullmatch(r"[a-z0-9._-]+", path.stem):
            raise ValueError(f"Invalid source ID: {path.name}")
        if path.stem in found:
            raise ValueError(f"Multiple source formats for: {path.stem}")
        if path.stat().st_size == 0:
            raise ValueError(f"Empty source file: {path.name}")
        if path.stat().st_size > 5 * 1024 * 1024:
            raise ValueError(f"Source exceeds 5 MiB: {path.name}")
        found.add(path.stem)
    return found


def pending_games(games, sources):
    return [game for game in games
            if game.get("category") == "games"
            and not str(game.get("image") or "").strip()
            and game["id"] not in sources
            and game["id"] not in OWNER_RESERVED_IDS]


def initial_method(game):
    # Planning recommendation, not proof of permission or a visual review.
    # Inspect the actual game and change this flag before producing artwork
    # when a screenshot or illustration would better represent it.
    if "/singlefiles/" in game.get("path", "") and game["id"] not in SCREENSHOT_IDS:
        return "true"
    return "false"


def render_queue(games, flags, revision):
    true_count = sum(flags.get(g["id"], initial_method(g)) == "true" for g in games)
    header = f"""# Thumbnails to add

Catalog: [{REPO}](https://github.com/{REPO}),
revision `{revision}` (`games.js`).
Remaining: **{len(games)} games** ({true_count} generate=true; {len(games) - true_count} generate=false).

- `generate=true`: create original artwork based on the actual game's gameplay/theme.
- `generate=false`: capture gameplay or reuse existing artwork after verifying display rights.
- Flags describe the **artwork method**, never completion or ownership.
- Initial recommendations: original illustrations for most single-file games;
  gameplay/screenshots for directory-hosted games and recognizable single-file releases.
  Inspect the game first; correct its flag if another method fits better.
  Neither flag is permission to use logos, protected characters, or unlicensed assets.
- Includes only catalog category `games` with no nonempty `image` and no source
  already in this repository's flat `thumbnails/` drop zone. Emulators/tools excluded,
  as are IDs the repository owner reserved for personal artwork (`OWNER_RESERVED_IDS`).
  Existing image URLs have not been audited for HTTP errors.
- Keep **catalog order**, not alphabetical order: one agent works top-down,
  the other bottom-up. Coordinate claimed IDs outside this list before overlapping.
- **Remove the entire entry when its validated source thumbnail is added**;
  commit the source and queue removal together. Do not toggle the flag to mark done.
- Refresh/check with `scripts/thumbnail_queue.py` (see `AGENTS.md`). Refresh
  preserves flags for pending IDs and excludes local sources even before catalog sync.

## Queue

"""
    return header + "".join(
        f"- `{game['id']}` generate={flags.get(game['id'], initial_method(game))}\n"
        for game in games
    )


def gh(*args):
    return subprocess.check_output(["gh", *args], text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, help="Use a local games.js (offline)")
    parser.add_argument("--ref", default="main", help="Platform revision (default: main)")
    parser.add_argument("--queue", type=Path, default=ROOT / "thumbs-to-add.md")
    parser.add_argument("--sources", type=Path, default=ROOT / "thumbnails")
    parser.add_argument("--check", action="store_true", help="Validate without writing")
    args = parser.parse_args()
    try:
        if args.catalog:
            text = args.catalog.read_text(encoding="utf-8")
            revision = args.ref if args.ref != "main" else "local catalog (unversioned)"
        else:
            # Resolve once so catalog content and provenance refer to one snapshot.
            revision = gh("api", f"repos/{REPO}/commits/{args.ref}", "--jq", ".sha")
            text = gh("api", f"repos/{REPO}/contents/games.js?ref={revision}",
                      "-H", "Accept: application/vnd.github.raw+json")
        games = load_catalog(text)
        sources = source_ids(args.sources)
        unknown = sources - {game["id"] for game in games}
        if unknown:
            raise ValueError(f"Sources not in catalog: {', '.join(sorted(unknown))}")
        pending = pending_games(games, sources)
        flags = read_queue(args.queue)
        expected = [game["id"] for game in pending]
        if args.check:
            missing = set(expected) - flags.keys()
            extra = flags.keys() - set(expected)
            if missing or extra:
                raise ValueError(f"Missing queue IDs: {sorted(missing)}; stale IDs: {sorted(extra)}")
            if list(flags) != expected:
                raise ValueError("Queue is not in catalog order")
            print(f"OK: {len(expected)} pending games, {len(sources)} local sources")
        else:
            args.queue.write_text(render_queue(pending, flags, revision), encoding="utf-8")
            print(f"Wrote {args.queue}: {len(expected)} pending games")
        return 0
    except (ValueError, OSError, KeyError, json.JSONDecodeError,
            subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
