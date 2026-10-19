#!/usr/bin/env python3
"""Open every catalog game in headless Chromium and save one raw screenshot each.

Intended for the `Screenshot Games` GitHub Actions workflow, but runs locally too:

    python -m pip install playwright && python -m playwright install chromium
    python scripts/screenshot_games.py --platform ../Dragon-Gaming-Platforms \
        --assets ../Dragon-Gaming-Assets --out screenshots

The platform checkout is served over a local static HTTP server (games rely on
fetch/XHR and module scripts, which `file://` breaks). Each game is loaded,
given a generic nudge (click, Enter/Space, a short burst of arrow/WASD input so
title screens advance and something moves), then the viewport is captured to
`<out>/<id>.png`. A `<out>/manifest.json` records the outcome per game so
failures are visible without digging through logs.

These are unreviewed raw captures for human inspection — NOT thumbnails and NOT
proof of display rights. See AGENTS.md before promoting any of them.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, urlparse

ASSETS_HOST = "dragon-gaming-platforms.github.io"
ASSETS_PREFIX = "/Dragon-Gaming-Assets/"
CHROMIUM_ARGS = [
    "--no-sandbox",
    "--disable-gpu",
    "--use-gl=angle",
    "--use-angle=swiftshader",
    "--enable-unsafe-swiftshader",
    "--ignore-gpu-blocklist",
    "--autoplay-policy=no-user-gesture-required",
    "--mute-audio",
]


def load_catalog(path: Path) -> list[dict]:
    """games.js is a JS file whose first array literal is valid JSON."""
    text = path.read_text(encoding="utf-8")
    start = text.index("[")
    games, _ = json.JSONDecoder().raw_decode(text[start:])
    return games


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):  # keep CI logs readable
        pass


@contextlib.contextmanager
def static_server(root: Path):
    port = free_port()
    handler = partial(QuietHandler, directory=str(root))
    httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        httpd.shutdown()


def resolve_url(game: dict, base: str, has_assets: bool) -> str | None:
    """Map a catalog path onto the local server, or None if it is remote-only."""
    path = str(game.get("path") or "").strip()
    if not path:
        return None
    if path.startswith("./") or path.startswith("/"):
        return base + "/platform/" + quote(path.lstrip("./"))
    parsed = urlparse(path)
    if parsed.scheme in ("http", "https"):
        if has_assets and parsed.netloc == ASSETS_HOST and parsed.path.startswith(ASSETS_PREFIX):
            rel = parsed.path[len(ASSETS_PREFIX):]
            if rel.endswith("/") or not rel:
                rel += "index.html"
            return base + "/assets/" + quote(rel)
        return None  # third-party host; the runner has no business hitting it
    return base + "/platform/" + quote(path)


def nudge(page, settle_ms: int) -> None:
    """Generic interaction that gets most games past title screens."""
    page.wait_for_timeout(settle_ms)
    vw = page.viewport_size or {"width": 1280, "height": 800}
    cx, cy = vw["width"] // 2, vw["height"] // 2
    with contextlib.suppress(Exception):
        page.mouse.click(cx, cy)
    for key in ("Enter", "Space"):
        with contextlib.suppress(Exception):
            page.keyboard.down(key)
            page.wait_for_timeout(120)
            page.keyboard.up(key)
    page.wait_for_timeout(1500)
    # A short burst of movement so action games show something besides a
    # frozen first frame. Keys are held (not tapped) because many games poll.
    for key in ("ArrowRight", "d", "ArrowUp", "w"):
        with contextlib.suppress(Exception):
            page.keyboard.down(key)
            page.wait_for_timeout(400)
            page.keyboard.up(key)
    page.wait_for_timeout(settle_ms // 2)
    # Arrow keys scroll ordinary pages; capture from the top like a visitor sees it.
    with contextlib.suppress(Exception):
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(200)


def capture(playwright, game: dict, url: str, dest: Path, args) -> dict:
    """Open one game in a fresh browser and screenshot it. Never raises."""
    result = {"id": game["id"], "url": url, "status": "ok", "file": dest.name}
    errors: list[str] = []
    browser = None
    try:
        launch = {"args": CHROMIUM_ARGS}
        if os.environ.get("CHROMIUM_PATH"):  # local runs without `playwright install`
            launch["executable_path"] = os.environ["CHROMIUM_PATH"]
        browser = playwright.chromium.launch(**launch)
        context = browser.new_context(
            viewport={"width": args.width, "height": args.height},
            device_scale_factor=1,
        )
        page = context.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)[:200]))
        page.set_default_timeout(args.timeout * 1000)
        page.goto(url, wait_until="load", timeout=args.timeout * 1000)
        nudge(page, args.settle * 1000)
        page.screenshot(path=str(dest), full_page=False)
        if errors:
            result["page_errors"] = errors[:5]
    except Exception as exc:  # timeouts, crashes, navigation failures
        result["status"] = "error"
        result["error"] = f"{type(exc).__name__}: {str(exc)[:300]}"
        if errors:
            result["page_errors"] = errors[:5]
    finally:
        with contextlib.suppress(Exception):
            if browser:
                browser.close()
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--platform", required=True, type=Path,
                    help="checkout of Dragon-Gaming-Platforms (contains games.js and games/)")
    ap.add_argument("--assets", type=Path, default=None,
                    help="optional checkout of Dragon-Gaming-Assets for github.io-hosted entries")
    ap.add_argument("--out", type=Path, default=Path("screenshots"))
    ap.add_argument("--categories", default="games",
                    help="comma-separated catalog categories to include (default: games)")
    ap.add_argument("--only", default="",
                    help="comma-separated IDs or regex (prefix with re:) to restrict the run")
    ap.add_argument("--limit", type=int, default=0, help="stop after N games (0 = all)")
    ap.add_argument("--force", action="store_true", help="recapture games that already have a PNG")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=800)
    ap.add_argument("--timeout", type=int, default=45, help="per-page navigation timeout, seconds")
    ap.add_argument("--settle", type=int, default=6, help="seconds to wait after load before interacting")
    args = ap.parse_args()

    catalog = args.platform / "games.js"
    if not catalog.is_file():
        print(f"error: {catalog} not found", file=sys.stderr)
        return 2
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("error: pip install playwright && python -m playwright install chromium", file=sys.stderr)
        return 2

    games = load_catalog(catalog)
    categories = {c.strip() for c in args.categories.split(",") if c.strip()}
    games = [g for g in games if g.get("category") in categories]
    if args.only:
        if args.only.startswith("re:"):
            rx = re.compile(args.only[3:])
            games = [g for g in games if rx.search(g["id"])]
        else:
            wanted = {s.strip() for s in args.only.split(",")}
            games = [g for g in games if g["id"] in wanted]
    if args.limit:
        games = games[: args.limit]

    args.out.mkdir(parents=True, exist_ok=True)
    manifest_path = args.out / "manifest.json"
    manifest: dict[str, dict] = {}
    if manifest_path.is_file():
        with contextlib.suppress(Exception):
            manifest = {m["id"]: m for m in json.loads(manifest_path.read_text()).get("games", [])}

    # Serve both checkouts under one origin via symlinks in a scratch root.
    root = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "screenshot-games-root"
    root.mkdir(parents=True, exist_ok=True)
    for name, target in (("platform", args.platform), ("assets", args.assets)):
        link = root / name
        if link.is_symlink() or link.exists():
            link.unlink()
        if target:
            link.symlink_to(target.resolve(), target_is_directory=True)

    counts = {"ok": 0, "error": 0, "skipped": 0, "remote": 0}
    with static_server(root) as base, sync_playwright() as pw:
        for i, game in enumerate(games, 1):
            gid = game["id"]
            if not re.fullmatch(r"[a-z0-9._-]+", gid):
                print(f"[{i}/{len(games)}] {gid}: skipped (unsafe id)")
                counts["skipped"] += 1
                continue
            dest = args.out / f"{gid}.png"
            if dest.exists() and not args.force:
                counts["skipped"] += 1
                continue
            url = resolve_url(game, base, args.assets is not None)
            if url is None:
                manifest[gid] = {"id": gid, "status": "remote", "path": game.get("path")}
                counts["remote"] += 1
                print(f"[{i}/{len(games)}] {gid}: remote-only path, not captured")
                continue
            t0 = time.time()
            res = capture(pw, game, url, dest, args)
            res["seconds"] = round(time.time() - t0, 1)
            manifest[gid] = res
            counts[res["status"]] += 1
            note = res.get("error", "")
            print(f"[{i}/{len(games)}] {gid}: {res['status']} ({res['seconds']}s) {note}".rstrip())
            manifest_path.write_text(json.dumps(
                {"generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                 "games": [manifest[k] for k in sorted(manifest)]},
                indent=2) + "\n")
    print("done:", json.dumps(counts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
