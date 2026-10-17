# Agent guide — Thumbnail Assets

## Scope and source of truth
- Read `README.md` and `thumbnails/README.md` first.
- This repo holds artwork, not game code or platform catalogs.
- Platform: `Dragon-Gaming-Platforms/Dragon-Gaming-Platforms`; `games.js`
  supplies exact IDs. Consult its `THIRD_PARTY.md` and upstream asset licenses.
- Focus only on `thumbs-to-add.md`: games lacking catalog images and local
  source artwork. Existing image URLs are not a broken-link audit.
- Planning flags are recommendations, not completed visual/license reviews.

## Shared work queue
- `generate=true`: create original game-specific artwork.
- `generate=false`: use gameplay screenshots or existing licensed artwork.
- Inspect the real game before making art; generic catalog descriptions may
  be inaccurate. Change the method if inspection supports a better approach.
- One agent works from the top; the other from the bottom. Preserve catalog
  order and coordinate claimed IDs before the agents' work ranges meet.
- Remove the entire game entry only after adding and validating its source.
  Never use `generate=false` to mark completion.
- Commit the source, provenance/attribution where required, and queue removal
  together. Refresh the queue to update its summary counts.
- Owner-reserved games (`OWNER_RESERVED_IDS` in `scripts/thumbnail_queue.py`,
  currently `echoed-path`) are excluded from the queue: the owner adds their
  thumbnails personally. Never create artwork for them.
- Pull/reconcile teammates' changes before refreshing; never overwrite another
  agent's artwork, flags, or queue edits. If a removed ID reappears, check that
  its source was committed and synced before doing duplicate work.

## Artwork rules
- Save ONE lowercase `thumbnails/<exact-catalog-id>.<ext>`; never derive IDs
  from display names. Dots/underscores in IDs are significant.
- Allowed formats: svg, png, webp, jpg, jpeg, gif. Avoid duplicate formats;
  CI precedence is `svg > png > webp > jpg > jpeg > gif`.
- Aim for 800×260 (~3:1) landscape framing; keep the subject safe for a center
  cover crop, avoid tiny text, and keep sources below about 5 MiB.
- Prefer real gameplay over title/loading screens for screenshot jobs.
- Generated art must reflect gameplay, not invent a misleading game scene.
- Use only artwork with verified display rights. A code license does not
  automatically license bundled artwork or commercial characters/logos.
- Record provenance in root `ARTWORK.md` (published with the artwork).
- Record source URLs, license/permission, author, and required attribution
  when reusing art; record original/generated provenance for new artwork.
  Include license notices/share-alike obligations where applicable. If rights
  are unclear, leave the entry pending and ask; don't bypass this with AI art.
- Do not add copyrighted ROMs, proprietary rips, Git LFS, or large datasets.
- No subdirectories in the drop zone; never hand-edit `thumbnails/jpg/`.

## Helpers and checks
`python3 scripts/thumbnail_queue.py` fetches the platform's current `main`
via authenticated `gh`, pins a commit, and refreshes `thumbs-to-add.md`.
It preserves existing method flags, removes catalog-covered/local-source IDs,
and adds new missing games in catalog order. Initial methods favor original
art for most single-file games and screenshots for directory-hosted games
and recognizable single-file releases; inspect and revise as needed.

```sh
# Validate queue membership/order and source names, duplicates, size, emptiness:
python3 scripts/thumbnail_queue.py --check
# Reproduce/check a pinned snapshot:
python3 scripts/thumbnail_queue.py --ref <platform-commit-sha> --check
# Offline refresh/check with a downloaded catalog (add --check to avoid writes):
python3 scripts/thumbnail_queue.py --catalog /path/to/games.js --ref <commit-sha>
# Dependency-free helper tests:
python3 -m unittest discover -s scripts -p 'test_*.py'
# Before committing:
git diff --check
```
- The queue helper does NOT decode images, audit remote URLs, or verify rights.
  Open every new image, check it decodes/rasterizes, review its 800×260 crop,
  and check the format/size before removing its queue entry.
- Keep downloaded catalogs, upstream clones, renders, caches, and temporary
  previews out of Git; use an external scratch directory.

`scripts/prepare_thumbnail.py` requires Pillow (`python3 -m pip install pillow`
in a virtual environment). It creates a decoded, cover-cropped 800×260 JPEG
source <=40 KiB, refuses overwrites and CI output paths, and supports explicit
`--crop LEFT TOP RIGHT BOTTOM` and optional `--brightness` for dark captures.
Review the finished image; compression alone is not visual validation. Example:

```sh
python3 scripts/prepare_thumbnail.py /scratch/capture.png thumbnails/<id>.jpg
```

## Delivery and Git safety
- Work only on the branch assigned by the current session instructions.
  Verify it with `git branch --show-current`; never switch branches or push
  to `main`. Do not reuse branch names from previous sessions.
- Commit small batches and push frequently: sandboxes can reset.
  Push explicitly to the assigned branch, not an old branch from chat history.
- Use local `git` for changes and `gh` for GitHub operations; never request
  credentials. Reconcile remote changes without force-pushing.
- Setup/queue instructions must be committed and pushed before adding art.
- CI builds/publishes on `main` or manual dispatch, not ordinary Arena branch
  pushes. It flattens transparency onto `#09090f`, cover-crops and compresses
  raster art toward 800×260 and <=40 KiB (640/480-wide fallback sizes exist).
  GIF sources pass through unchanged; keep animated files lightweight.
- The asset README describes a platform thumbnail-sync workflow, but the
  inspected platform revision did not contain `sync-thumbnails.yml`. Don't
  claim thumbnails are catalog-linked/live until actual sync/deploy is verified.
