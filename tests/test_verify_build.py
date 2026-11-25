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
        equivalent_html_link = (
            "<a class='contact' href=' MAILTO:Vid80gmx@gmail.com '>"
            "<span>Vid80gmx@gmail.com</span></a>"
        )
        equivalent_html = original.replace(canonical_html_link, equivalent_html_link)
        self.assertNotEqual(equivalent_html, original)
        html.write_text(equivalent_html, encoding="utf-8")
        android_html.write_text(equivalent_html, encoding="utf-8")
        self.assertEqual(self.run_check(name), (0, None))

        visible_opacity_html = original.replace(
            canonical_html_link,
            '<a style="opacity:0.01" href="mailto:Vid80gmx@gmail.com">'
            "Vid80gmx@gmail.com</a>",
        )
        self.assertNotEqual(visible_opacity_html, original)
        html.write_text(visible_opacity_html, encoding="utf-8")
        android_html.write_text(visible_opacity_html, encoding="utf-8")
        self.assertEqual(self.run_check(name), (0, None))

        open_details_html = original.replace(
            canonical_html_link,
            '<details open><a href="mailto:Vid80gmx@gmail.com">'
            "Vid80gmx@gmail.com</a></details>",
        )
        self.assertNotEqual(open_details_html, original)
        html.write_text(open_details_html, encoding="utf-8")
        android_html.write_text(open_details_html, encoding="utf-8")
        self.assertEqual(self.run_check(name), (0, None))

        canonical_markdown_link = "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)"
        equivalent_markdown_links = (
            "[Vid80gmx@gmail.com](<MAILTO:Vid80gmx@gmail.com>)",
        )
        for equivalent_markdown_link in equivalent_markdown_links:
            with self.subTest(markdown=equivalent_markdown_link):
                equivalent_markdown = original_markdown.replace(
                    canonical_markdown_link, equivalent_markdown_link
                )
                self.assertNotEqual(equivalent_markdown, original_markdown)
                impressum.write_text(equivalent_markdown, encoding="utf-8")
                self.assertEqual(self.run_check(name), (0, None))

        accepted_markdown_contexts = (
            original_markdown.replace(
                "**Kontakt:** " + canonical_markdown_link,
                "**Kontakt:**\n    " + canonical_markdown_link,
            ),
            original_markdown.replace(
                "**Kontakt:** " + canonical_markdown_link,
                "> **Kontakt:** " + canonical_markdown_link,
            ),
            original_markdown.replace(
                "**Kontakt:** " + canonical_markdown_link,
                "- **Kontakt:** " + canonical_markdown_link,
            ),
        )
        for accepted_markdown in accepted_markdown_contexts:
            with self.subTest(markdown_context=accepted_markdown):
                self.assertNotEqual(accepted_markdown, original_markdown)
                impressum.write_text(accepted_markdown, encoding="utf-8")
                self.assertEqual(self.run_check(name), (0, None))

        # Replace the complete contact line so the quoted fence really starts
        # at the beginning of a line and contains a non-contact link.
        quoted_fence_contact = (
            "> ~~~markdown\n"
            "> [hidden](mailto:hidden@example.invalid)\n\n"
            "**Kontakt:** " + canonical_markdown_link
        )
        equivalent_markdown = original_markdown.replace(
            "**Kontakt:** " + canonical_markdown_link,
            quoted_fence_contact,
        )
        self.assertNotEqual(equivalent_markdown, original_markdown)
        self.assertIn(
            "\n> ~~~markdown\n> [hidden](mailto:hidden@example.invalid)\n\n"
            "**Kontakt:** " + canonical_markdown_link + "\n",
            equivalent_markdown,
        )
        impressum.write_text(equivalent_markdown, encoding="utf-8")
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
            "template-hidden contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com) "
                "<template><a href=\"mailto:Vid80gmx@gmail.com\">"
                "Vid80gmx@gmail.com</a></template>",
            ),
            "hidden contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com) "
                "<a hidden href=\"mailto:Vid80gmx@gmail.com\">"
                "Vid80gmx@gmail.com</a>",
            ),
            "display-none contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com) "
                "<a style=\"display:none\" href=\"mailto:Vid80gmx@gmail.com\">"
                "Vid80gmx@gmail.com</a>",
            ),
            "textarea-hidden contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com) "
                "<textarea><a href=\"mailto:Vid80gmx@gmail.com\">"
                "Vid80gmx@gmail.com</a></textarea>",
            ),
            "script-data contact label": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com">'
                '<script type="text/plain">Vid80gmx@gmail.com</script></a>',
            ),
            "self-closing-script contact label": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com">'
                '<script/>Vid80gmx@gmail.com</script></a>',
            ),
            "aria-hidden contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com) "
                '<a aria-hidden="true" href="mailto:Vid80gmx@gmail.com">'
                "Vid80gmx@gmail.com</a>",
            ),
            "hidden-descendant contact label": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com">'
                '<span hidden>Vid80gmx@gmail.com</span></a>',
            ),
            "inert contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com) "
                '<div inert><a href="mailto:Vid80gmx@gmail.com">'
                "Vid80gmx@gmail.com</a></div>",
            ),
            "visibility-hidden contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com) "
                '<a style="visibility:hidden" href="mailto:Vid80gmx@gmail.com">'
                "Vid80gmx@gmail.com</a>",
            ),
            "opacity-hidden contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com) "
                '<a style="opacity:0" href="mailto:Vid80gmx@gmail.com">'
                "Vid80gmx@gmail.com</a>",
            ),
            "style-element contact label": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com">'
                "<style>Vid80gmx@gmail.com</style></a>",
            ),
            "closed-container contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com) "
                '<details><a href="mailto:Vid80gmx@gmail.com">'
                "Vid80gmx@gmail.com</a></details>",
            ),
            "malformed mailto scheme": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto :Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
            ),
            "duplicate href contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:kontakt@example.invalid" '
                'href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
            ),
            "duplicate matching href contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com" '
                'href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
            ),
            "nested HTML contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com">'
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>'
                '</a>',
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
            "contact link markup": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)",
            ),
            "code-fence-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "```markdown\n[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)\n```",
            ),
            "inline-code-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com) "
                "`[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)`",
            ),
            "indented-code-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "    [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "blockquote-fence-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "> ~~~\n> [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)\n> ~~~",
            ),
            "invalid-fence-closer contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "~~~\n[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)\n~~~ trailing",
            ),
            "nested-image contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "![outer [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com) suffix]"
                "(https://example.invalid)",
            ),
            "unmatched-emphasis contact label": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com) "
                "[Vid80gmx*@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "formatted-label contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com) "
                "[**Vid80gmx@gmail.com**](mailto:Vid80gmx@gmail.com)",
            ),
            "code-span-label contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com) "
                "[`Vid80gmx@gmail.com`](mailto:Vid80gmx@gmail.com)",
            ),
            "autolink contact address": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com) "
                "<Vid80gmx@gmail.com>",
            ),
            "raw-html-attribute contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com) "
                '<span data-link="[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)"></span>',
            ),
            "raw-html-block contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<div>\n[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)\n</div>",
            ),
            "raw-html-wrapper contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<span>[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)</span>",
            ),
            "self-closing-raw-html contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<span/>\n[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "processing-instruction contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<? [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com) ?>",
            ),
            "cdata contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<![CDATA[[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)]]>",
            ),
            "declaration contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<!DOCTYPE [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)>",
            ),
            "link-title contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                '[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com "Contact")',
            ),
            "nested-link-title contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                '[Other](https://example.invalid '
                '"[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)")',
            ),
            "case-folded contact address": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "[Vid80gmx@gmail.com](mailto:VID80GMX@GMAIL.COM)",
            ),
            "reference-style contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "[Vid80gmx@gmail.com][contact]\n\n"
                "[contact]: mailto:Vid80gmx@gmail.com",
            ),
            "unclosed-comment contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<!--\n[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "comment-separated contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "[Vid80gmx@gmail.com]<!-- separator -->"
                "(mailto:Vid80gmx@gmail.com)",
            ),
            "unclosed-pre contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<pre>\n[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "escaped-backtick code-span contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "\\\\`[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)`",
            ),
            "escaped-opener code-span contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "\\` `[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)`",
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
