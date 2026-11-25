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
        android_html = self.root / ASSET / "index.html"
        original = html.read_text(encoding="utf-8")
        android_original = android_html.read_text(encoding="utf-8")
        self.assertEqual(original, android_original)
        impressum = self.root / "IMPRESSUM.md"
        original_markdown = impressum.read_text(encoding="utf-8")
        self.assertEqual(self.run_check(name), (0, None))

        canonical_html_link = '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>'
        accepted_html_links = (
            "<a class='contact' href='mailto:Vid80gmx@gmail.com'>"
            "<span>Vid80gmx@gmail.com</span></a>",
            '<a href="mailto:Vid80gmx@gmail.com" '
            'href="mailto:kontakt@example.invalid">Vid80gmx@gmail.com</a>',
        )
        for accepted_html_link in accepted_html_links:
            with self.subTest(html=accepted_html_link):
                equivalent_html = original.replace(
                    canonical_html_link, accepted_html_link
                )
                self.assertNotEqual(equivalent_html, original)
                html.write_text(equivalent_html, encoding="utf-8")
                android_html.write_text(equivalent_html, encoding="utf-8")
                self.assertEqual(self.run_check(name), (0, None))

        canonical_markdown_link = "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)"
        accepted_markdown_links = (
            "[Vid80gmx@gmail.com](<mailto:Vid80gmx@gmail.com>)",
            "[`Vid80gmx@gmail.com`](mailto:Vid80gmx@gmail.com)",
            "[**Vid80gmx@gmail.com**](mailto:Vid80gmx@gmail.com)",
            "[~Vid80gmx@gmail.com~](mailto:Vid80gmx@gmail.com)",
            "[*Vid80gmx@gmail.com*](mailto:Vid80gmx@gmail.com)",
            r"[Vid80gmx@gmail\.com](mailto:Vid80gmx@gmail.com)",
            (
                f"```markdown\n{canonical_markdown_link}\n``` \n\n"
                f"{canonical_markdown_link}"
            ),
            (
                f"```markdown\n{canonical_markdown_link}\n```\t\n\n"
                f"{canonical_markdown_link}"
            ),
            "> [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            (
                "> ~~~\n> example\n\n"
                f"{canonical_markdown_link}"
            ),
            (
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<!-- hidden -->\n\n"
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)"
            ),
            (
                "<span>[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)"
                "</span>"
            ),
        )
        for accepted_markdown_link in accepted_markdown_links:
            with self.subTest(markdown=accepted_markdown_link):
                equivalent_markdown = original_markdown.replace(
                    canonical_markdown_link, accepted_markdown_link
                )
                self.assertNotEqual(equivalent_markdown, original_markdown)
                impressum.write_text(equivalent_markdown, encoding="utf-8")
                self.assertEqual(self.run_check(name), (0, None))

        paragraph_continuation = original_markdown.replace(
            "**Kontakt:** " + canonical_markdown_link,
            "**Kontakt:**\n    " + canonical_markdown_link,
        )
        self.assertNotEqual(paragraph_continuation, original_markdown)
        impressum.write_text(paragraph_continuation, encoding="utf-8")
        self.assertEqual(self.run_check(name), (0, None))

        html_mutations = {
            "placeholder": (
                "<b>Lowgiga</b>",
                "<b>Lowgiga</b> <i>[vor Veröffentlichung ergänzen: Name, Anschrift, Kontakt]</i>",
            ),
            "provider name": ("<b>Lowgiga</b>", "<b>Example Provider</b>"),
            "provider address": ("New York 11354 USA", "Berlin 10115 Germany"),
            "contact target": (
                'href="mailto:Vid80gmx@gmail.com"',
                'href="mailto:kontakt@example.invalid"',
            ),
            "contact link markup": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)",
            ),
            "comment-hidden contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com) "
                "<!-- <a href=\"mailto:Vid80gmx@gmail.com\">"
                "Vid80gmx@gmail.com</a> -->",
            ),
            "script-hidden contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com">'
                '<script type="text/plain">Vid80gmx@gmail.com</script></a>',
            ),
            "self-closing-script-hidden contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com">'
                '<script/>Vid80gmx@gmail.com</script></a>',
            ),
            "textarea-hidden contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<textarea><a href="mailto:Vid80gmx@gmail.com">'
                'Vid80gmx@gmail.com</a></textarea>',
            ),
            "hidden-anchor contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a hidden href="mailto:Vid80gmx@gmail.com">'
                'Vid80gmx@gmail.com</a>',
            ),
            "hidden-descendant contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com">'
                '<span hidden>Vid80gmx@gmail.com</span></a>',
            ),
            "template-hidden contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<template><a href="mailto:Vid80gmx@gmail.com">'
                'Vid80gmx@gmail.com</a></template>',
            ),
            "duplicate href with wrong first target": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:kontakt@example.invalid" '
                'href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
            ),
            "nested anchor contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com">'
                '<a href="mailto:kontakt@example.invalid">'
                'Vid80gmx@gmail.com</a></a>',
            ),
        }
        for field, (old, new) in html_mutations.items():
            with self.subTest(document="HTML", field=field):
                html.write_text(original, encoding="utf-8")
                android_html.write_text(android_original, encoding="utf-8")
                mutated = original.replace(old, new)
                self.assertNotEqual(mutated, original)
                html.write_text(mutated, encoding="utf-8")
                android_html.write_text(mutated, encoding="utf-8")
                status, failure = self.run_check(name)
                self.assertEqual(status, 1)
                self.assertIsNotNone(failure)

        html.write_text(original, encoding="utf-8")
        android_html.write_text(android_original, encoding="utf-8")
        markdown_mutations = {
            "placeholder": (
                "**Diensteanbieter:** Lowgiga",
                "**Diensteanbieter:** Lowgiga [vor Veröffentlichung ergänzen: Name, Anschrift, Kontakt]",
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
            "case-folded contact target": (
                "(mailto:Vid80gmx@gmail.com)",
                "(mailto:VID80GMX@GMAIL.COM)",
            ),
            "contact link markup": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)",
            ),
            "autolink outside supported scope": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "<Vid80gmx@gmail.com>",
            ),
            "reference link outside supported scope": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "[Vid80gmx@gmail.com][contact]\n\n"
                "[contact]: mailto:Vid80gmx@gmail.com",
            ),
            "code-fence-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "```markdown\n[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)\n```",
            ),
            "invalid-fence-close-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "~~~markdown\n~~~not-a-close\n"
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)\n~~~",
            ),
            "indented-code-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "    [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "unclosed-pre-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n<pre>\n"
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "inline-code-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "`[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)`",
            ),
            "code-span-label-with-extra-text": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "[`Vid80gmx@gmail.com`extra](mailto:Vid80gmx@gmail.com)",
            ),
            "unmatched-emphasis-label": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "[*Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "triple-tilde-label": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "[~~~Vid80gmx@gmail.com~~~](mailto:Vid80gmx@gmail.com)",
            ),
            "escaped-extra-label": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                r"[Vid80gmx@gmail.com\*](mailto:Vid80gmx@gmail.com)",
            ),
            "escaped-backtick-code-span-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                r"\` `[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)`",
            ),
            "unclosed-comment-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n<!--\n"
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "comment-separated contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "[Vid80gmx@gmail.com]<!-- separator -->"
                "(mailto:Vid80gmx@gmail.com)",
            ),
            "blockquote-fence-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "> ~~~markdown\n"
                "> [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)\n"
                "> ~~~",
            ),
            "image-description-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "![Contact [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)]"
                "(contact.png)",
            ),
            "raw-html-attribute-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                '<span title="[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)">'
                "No contact link</span>",
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
