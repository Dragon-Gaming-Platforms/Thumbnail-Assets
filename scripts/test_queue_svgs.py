"""Dependency-free checks for the original SVG collection and safe generator."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from create_queue_svgs import ART, make_svg

SVG = '{http://www.w3.org/2000/svg}'
SCRIPT = Path(__file__).with_name('create_queue_svgs.py')


class OriginalQueueSVGTests(unittest.TestCase):
    def test_unique_exact_ids_and_reserved_work_excluded(self):
        ids = [s[0] for s in ART]
        self.assertEqual(len(ids), 35)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertNotIn('echoed-path', ids)
        self.assertNotIn('glade-game', ids)
        for id in ids:
            self.assertRegex(id, r'^[a-z0-9._-]+$')

    def test_all_are_small_accessible_standalone_svg(self):
        allowed = {'svg', 'title', 'desc', 'g', 'rect', 'circle', 'ellipse',
                   'path', 'line', 'polyline', 'polygon', 'text'}
        for spec in ART:
            with self.subTest(id=spec[0]):
                source = make_svg(spec)
                root = ET.fromstring(source)
                self.assertEqual(root.tag, SVG + 'svg')
                self.assertEqual(root.attrib['viewBox'], '0 0 800 260')
                self.assertEqual((root.attrib['width'], root.attrib['height']), ('800', '260'))
                self.assertEqual(root.attrib['aria-labelledby'], 'title desc')
                self.assertTrue(root.find(SVG + 'title').text)
                self.assertIn('Not a gameplay screenshot', root.find(SVG + 'desc').text)
                self.assertLessEqual(len(source.encode('utf-8')), 40960)
                for node in root.iter():
                    self.assertIn(node.tag.removeprefix(SVG), allowed)
                    for key, value in node.attrib.items():
                        self.assertFalse(key.lower().startswith('on'))
                        self.assertNotIn('href', key.lower())
                        self.assertNotIn('url(', value.lower())
                        self.assertNotIn('data:', value.lower())

    def test_deterministic_and_every_asset_is_distinct(self):
        bodies = [make_svg(s) for s in ART]
        self.assertEqual(len(bodies), len(set(bodies)))
        self.assertEqual(bodies, [make_svg(s) for s in ART])

    def test_source_files_match_hand_authored_recipes(self):
        root = SCRIPT.parent.parent / 'thumbnails'
        for spec in ART:
            with self.subTest(id=spec[0]):
                self.assertEqual((root / (spec[0] + '.svg')).read_text(), make_svg(spec))

    def test_generator_requires_explicit_destination(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True)
        self.assertNotEqual(r.returncode, 0)

    def test_generator_never_overwrites_and_checks_before_writing(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / 'wordle.svg'
            target.write_text('existing artwork')
            r = subprocess.run([sys.executable, str(SCRIPT), '--output', d,
                                '--ids', 'pong', 'wordle'], capture_output=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertEqual(target.read_text(), 'existing artwork')
            self.assertFalse((Path(d) / 'pong.svg').exists())

    def test_generator_rejects_unknown_ids(self):
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run([sys.executable, str(SCRIPT), '--output', d,
                                '--ids', 'not-a-game'], capture_output=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertEqual(list(Path(d).iterdir()), [])

    def test_generator_can_reproduce_one_asset(self):
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run([sys.executable, str(SCRIPT), '--output', d,
                                '--ids', 'wordle'], capture_output=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            wordle = next(s for s in ART if s[0] == 'wordle')
            self.assertEqual((Path(d) / 'wordle.svg').read_text(), make_svg(wordle))


if __name__ == '__main__':
    unittest.main()
