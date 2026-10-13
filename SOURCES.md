# Thumbnail provenance

One entry per file in `thumbnails/`. Screenshots were captured by running the
game copy vendored in the platform repository
([Dragon-Gaming-Platforms](https://github.com/Dragon-Gaming-Platforms/Dragon-Gaming-Platforms),
revision `db88cc18c657878aacf5c896bdc69f35342b415d`) in headless Chromium,
then center-cropping to 800×260. No third-party logos or trademarked
characters are included beyond what the game itself draws during play.

| File | Game / upstream | Author | License | Method / notes |
| :--- | :--- | :--- | :--- | :--- |
| `0hh1.png` | [Q42/0hh1](https://github.com/Q42/0hh1) | Q42 / Martin Kool | MIT (`games/0hh1/LICENSE`) | Gameplay screenshot, 8×8 puzzle mid-solve. |
| `0hn0.png` | [Q42/0hn0](https://github.com/Q42/0hn0) | Q42 / Martin Kool | MIT (`games/0hn0/LICENSE`) | Gameplay screenshot, 8×8 puzzle mid-solve. |
| `2048.png` | [gabrielecirulli/2048](https://github.com/gabrielecirulli/2048) | Gabriele Cirulli | MIT (`games/2048/LICENSE.txt`) | Gameplay screenshot of the 4×4 board (mid-game state loaded through the game's own save format). |
| `3d-chess.png` | [juliangarnier/3D-Hartwig-chess-set](https://github.com/juliangarnier/3D-Hartwig-chess-set) | Julian Garnier | MIT (`games/3d-chess/LICENSE.txt`) | Gameplay screenshot after an Italian-game opening, board rotated to the 3D view. Textures are part of the MIT repo. |
| `3d-city.jpg` | [lo-th/3d.city](https://github.com/lo-th/3d.city) | lo-th (Three.js city builder on micropolisJS) | MIT (`games/3d.city/LICENSE`); simulation engine GPL-3.0 (`COPYING`) | Author's own in-repo gameplay screenshot `assets/img/preview02.jpg` (800×280), trimmed to 800×260. No pixels altered otherwise. |
| `adarkroom.png` | [doublespeakgames/adarkroom](https://github.com/doublespeakgames/adarkroom) | Michael Townsend (Doublespeak Games) | MPL-2.0 (`games/adarkroom/LICENSE.md`) | Gameplay screenshot of the Firelit Room / Tiny Village view (mid-game state set through the game's state manager). Text-only UI, no artwork reproduced. |
| `abyss-sonar.png` | `games/singlefiles/Abyss-Sonar.html` (platform single-file game) | — | Original artwork for this repo | AI-generated original illustration after inspecting the game: top-down sonar scope, submarine, echo contacts, mines and a wreck (the game's radial sonar canvas gameplay). No text. |
| `air-hockey.png` | `games/singlefiles/Air-Hockey.html` (platform single-file game) | — | Original artwork for this repo | AI-generated original illustration after inspecting the game: top-down air hockey table, two strikers, puck with pulse trail, bumpers and rebound lines (the game's 12-match cup with table gadgets). No text. |
| `air-traffic-control.png` | `games/singlefiles/Air-Traffic-Control.html` (platform single-file game) | — | Original artwork for this repo | AI-generated original illustration after inspecting the game: radar scope with aircraft markers and heading lines, two runways, restricted-area polygon and weather cell (the game's radar-vectoring canvas). No text. |
| `alchemy-workshop.png` | `games/singlefiles/Alchemy-Workshop.html` (platform single-file game) | — | Original artwork for this repo | AI-generated original illustration after inspecting the game: cauldron, distillation tower, flask and ingredient shelves with three property-coloured vapours (the game's apparatus / heat / duration brewing). No text. |

## Pending / blocked (not added)

- `1255-burgomaster`: source code is GPL-3.0 but the game README states
  "ALL GRAPHIC AND SOUND ASSETS UNDER PROPRIETARY LICENSE ... YOU MAY NOT
  REDISTRIBUTE THE GAME WITH THE ASSETS". A screenshot would reproduce those
  assets, so no thumbnail was created; needs explicit permission.
- `3d-graphing-calculator`: not vendored; the page is an iframe embed of a
  turbowarp.org Scratch project by 52525rr (CC-BY-NC-SA 2.0). Could not be
  loaded from the sandbox and the licence needs a project-level decision.
