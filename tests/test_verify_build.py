"""Regression tests for the static build verification's offline invariants."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ASSET = Path("android/app/src/main/assets")
ENGINE = Path("algorithm/robot-navigation.js")
PWA_NAMES = (
    "manifest.json",
    "sw.js",
    "icon-192.png",
    "icon-512.png",
    "icon-512-maskable.png",
)


class VerifyBuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        relatives = [
            Path("tests/verify-build.py"),
            Path("tests/package.json"),
            Path("index.html"),
            Path("IMPRESSUM.md"),
            ENGINE,
            Path("robot-navigation.js"),
            Path("docs/ARCHITECTURE.md"),
            Path(".nojekyll"),
            Path("scripts/prepare-pages-surface.sh"),
        ]
        relatives.extend(Path(name) for name in PWA_NAMES)
        relatives.extend(ASSET / name for name in ("index.html", "robot-navigation.js", *PWA_NAMES))
        for relative in relatives:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        shutil.copytree(ROOT / "bg", self.root / "bg")
        shutil.copytree(ROOT / ASSET / "bg", self.root / ASSET / "bg")

    def run_check(self, name):
        result = subprocess.run(
            [sys.executable, str(self.root / "tests/verify-build.py")],
            capture_output=True,
            text=True,
            check=False,
        )
        report = json.loads(result.stdout)
        failure = next(
            (item for item in report["failed_checks"] if item["name"] == name), None
        )
        return result.returncode, failure

    def test_android_asset_parity_and_missing_asset(self):
        name = "Android HTML asset matches index.html byte for byte"
        self.assertEqual(self.run_check(name), (0, None))
        android_html = self.root / ASSET / "index.html"
        android_html.write_bytes(android_html.read_bytes() + b"\n")
        status, failure = self.run_check(name)
        self.assertEqual(status, 1)
        self.assertIsNotNone(failure)
        android_html.unlink()
        status, failure = self.run_check(name)
        self.assertEqual(status, 1)
        self.assertIsNotNone(failure)

    def test_network_apis_are_rejected(self):
        name = "Standalone engine has no fetch/XHR/WebSocket"
        engine = self.root / ENGINE
        original = engine.read_text(encoding="utf-8")
        self.assertEqual(self.run_check(name), (0, None))
        for expression in [
            "fetch('/data')",
            "fetch  ('/data')",
            "new XMLHttpRequest()",
            "new WebSocket('/data')",
        ]:
            with self.subTest(expression=expression):
                engine.write_text(original + "\n" + expression + ";\n", encoding="utf-8")
                status, failure = self.run_check(name)
                self.assertEqual(status, 1)
                self.assertIsNotNone(failure)

    def test_service_worker_registration_guard(self):
        name = "Service worker registration is limited to http(s) and skips android_asset"
        html = self.root / "index.html"
        original = html.read_text(encoding="utf-8")
        self.assertEqual(self.run_check(name), (0, None))
        html.write_text(original.replace("android_asset", "skipped_guard"), encoding="utf-8")
        status, failure = self.run_check(name)
        self.assertEqual(status, 1)
        self.assertIsNotNone(failure)
        html.write_text(original.replace("if (proto !== 'http:' && proto !== 'https:') return;\n", ""), encoding="utf-8")
        status, failure = self.run_check(name)
        self.assertEqual(status, 1)
        self.assertIsNotNone(failure)

    def test_impressum_requires_provider_details(self):
        name = "Impressum contains the required DDG provider details"
        html = self.root / "index.html"
        original = html.read_text(encoding="utf-8")
        impressum = self.root / "IMPRESSUM.md"
        original_markdown = impressum.read_text(encoding="utf-8")
        self.assertEqual(self.run_check(name), (0, None))

        html_mutations = {
            "placeholder": (
                "<b>Lowgiga</b>",
                "<i>[vor Veröffentlichung ergänzen: Name, Anschrift, Kontakt]</i>",
            ),
            "provider name": ("<b>Lowgiga</b>", "<b>Example Provider</b>"),
            "provider address": ("New York 11354 USA", "Berlin 10115 Germany"),
            "contact target": (
                'href="mailto:Vid80gmx@gmail.com"',
                'href="mailto:kontakt@example.invalid"',
            ),
            "contact link markup": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                "Vid80gmx@gmail.com",
            ),
        }
        for field, (old, new) in html_mutations.items():
            with self.subTest(document="HTML", field=field):
                html.write_text(original, encoding="utf-8")
                mutated = original.replace(old, new)
                self.assertNotEqual(mutated, original)
                html.write_text(mutated, encoding="utf-8")
                status, failure = self.run_check(name)
                self.assertEqual(status, 1)
                self.assertIsNotNone(failure)

        html.write_text(original, encoding="utf-8")
        markdown_mutations = {
            "placeholder": (
                "**Diensteanbieter:** Lowgiga",
                "**Diensteanbieter:** [vor Veröffentlichung ergänzen: Name, Anschrift, Kontakt]",
            ),
            "provider name": (
                "**Diensteanbieter:** Lowgiga",
                "**Diensteanbieter:** Example Provider",
            ),
            "provider address": (
                "**Anschrift:** New York 11354 USA",
                "**Anschrift:** Berlin 10115 Germany",
            ),
            "contact target": (
                "(mailto:Vid80gmx@gmail.com)",
                "(mailto:kontakt@example.invalid)",
            ),
            "contact link markup": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com",
            ),
        }
        for field, (old, new) in markdown_mutations.items():
            with self.subTest(document="Markdown", field=field):
                impressum.write_text(original_markdown, encoding="utf-8")
                mutated = original_markdown.replace(old, new)
                self.assertNotEqual(mutated, original_markdown)
                impressum.write_text(mutated, encoding="utf-8")
                status, failure = self.run_check(name)
                self.assertEqual(status, 1)
                self.assertIsNotNone(failure)

    def test_relative_manifest_scope_is_required(self):
        name = "PWA manifest uses relative scope and start_url"
        manifest = self.root / "manifest.json"
        android_manifest = self.root / ASSET / "manifest.json"
        original = manifest.read_text(encoding="utf-8")
        self.assertEqual(self.run_check(name), (0, None))
        absolute = original.replace('"./index.html"', '"./index.html"').replace(
            '"start_url": "./"', '"start_url": "/AnFoVO-Lernkompendium/"'
        ).replace('"scope": "./"', '"scope": "/"')
        manifest.write_text(absolute, encoding="utf-8")
        android_manifest.write_text(absolute, encoding="utf-8")
        status, failure = self.run_check(name)
        self.assertEqual(status, 1)
        self.assertIsNotNone(failure)


if __name__ == "__main__":
    unittest.main()
