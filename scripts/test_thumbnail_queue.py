"""Offline regression tests; no GitHub access or third-party dependencies."""

import tempfile
from pathlib import Path
import unittest

import thumbnail_queue as queue


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.games = [
            {"id": "z-game", "category": "games", "path": "./games/z/index.html"},
            {"id": "story", "category": "games", "path": "./games/singlefiles/Story.html"},
            {"id": "covered", "category": "games", "image": "thumbs/covered.jpg"},
            {"id": "tool", "category": "other"},
            {"id": "emulator", "category": "emulators"},
            {"id": "blank", "category": "games", "image": "  "},
        ]

    def test_missing_games_only_in_catalog_order(self):
        self.assertEqual([g["id"] for g in queue.pending_games(self.games, set())],
                         ["z-game", "story", "blank"])

    def test_completed_source_excluded_before_catalog_sync(self):
        self.assertEqual([g["id"] for g in queue.pending_games(self.games, {"story"})],
                         ["z-game", "blank"])

    def test_methods_and_manual_override(self):
        self.assertEqual(queue.initial_method(self.games[0]), "false")
        self.assertEqual(queue.initial_method(self.games[1]), "true")
        self.assertEqual(queue.initial_method({"id": "balatro", "path":
                         "./games/singlefiles/Balatro.html"}), "false")
        text = queue.render_queue(self.games[:2], {"story": "false"}, "abc123")
        self.assertIn("- `story` generate=false", text)
        self.assertIn("2 games** (0 generate=true; 2 generate=false)", text)

    def test_queue_round_trip_and_order(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "queue.md"
            path.write_text(queue.render_queue(self.games[:2], {}, "abc123"))
            self.assertEqual(list(queue.read_queue(path).items()),
                             [("z-game", "false"), ("story", "true")])

    def test_duplicate_and_malformed_queue_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "queue.md"
            for text in ("- `id` generate=true\n- `id` generate=false\n",
                         "- `id` generate=maybe\n"):
                path.write_text(text)
                with self.assertRaises(ValueError):
                    queue.read_queue(path)

    def test_source_scan_is_flat_and_checks_duplicates(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "jpg").mkdir()
            (root / "jpg" / "generated.jpg").write_bytes(b"test")
            (root / "README.md").write_text("ignored")
            (root / "vectoid-td-3d-v1.4.png").write_bytes(b"test")
            self.assertEqual(queue.source_ids(root), {"vectoid-td-3d-v1.4"})
            (root / "vectoid-td-3d-v1.4.svg").write_bytes(b"test")
            with self.assertRaises(ValueError):
                queue.source_ids(root)

    def test_uppercase_empty_and_oversize_sources_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name, size in [("BAD.png", 1), ("empty.png", 0),
                               ("large.png", 5 * 1024 * 1024 + 1)]:
                path = root / name
                with path.open("wb") as stream:
                    stream.truncate(size)
                with self.assertRaises(ValueError):
                    queue.source_ids(root)
                path.unlink()

    def test_catalog_json_extraction(self):
        catalog = queue.load_catalog('const GAMES_DATA = [{"id":"id"}];\nconst other = 1;')
        self.assertEqual(catalog, [{"id": "id"}])

    def test_bad_catalog_fails(self):
        for text in ('let SOMETHING = [];',
                     'const GAMES_DATA = [{"id":"same"},{"id":"same"}];',
                     'const GAMES_DATA = [{"id":"../bad"}];'):
            with self.assertRaises(ValueError):
                queue.load_catalog(text)


if __name__ == "__main__":
    unittest.main()
