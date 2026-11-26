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
    IMPRESSUM_CHECK = "Impressum contains the required DDG provider details"
    CANONICAL_HTML_LINK = (
        '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>'
    )
    CANONICAL_MARKDOWN_LINK = (
        "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)"
    )

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

    def assert_impressum_check(self, should_pass):
        status, failure = self.run_check(self.IMPRESSUM_CHECK)
        if should_pass:
            self.assertEqual(status, 0)
            self.assertIsNone(failure)
        else:
            self.assertEqual(status, 1)
            self.assertIsNotNone(failure)

    def write_html_pair(self, html):
        (self.root / "index.html").write_text(html, encoding="utf-8")
        (self.root / ASSET / "index.html").write_text(html, encoding="utf-8")

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
            '<a href="mailto:Vid80gmx@gmail.com" '
            'href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
            '<a style="opacity:0.01" href="mailto:Vid80gmx@gmail.com">'
            "Vid80gmx@gmail.com</a>",
            '<details open><a href="mailto:Vid80gmx@gmail.com">'
            "Vid80gmx@gmail.com</a></details>",
            '<a style="opacity:0;opacity:1" href="mailto:Vid80gmx@gmail.com">'
            "Vid80gmx@gmail.com</a>",
            '<a style="opacity:0;opacity:1!important" '
            'href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
            '<a style="filter:opacity(0);filter:opacity(1)" '
            'href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
            '<a style="clip-path:inset(50%);clip-path:none" '
            'href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
            '<a style="color:rgba(1,2,3,1)" '
            'href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
            '<a style="color:#1234" '
            'href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
            "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com) <svg/>"
            + canonical_html_link,
            "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com) <math/>"
            + canonical_html_link,
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
            "[__Vid80gmx@gmail.com__](mailto:Vid80gmx@gmail.com)",
            "[~~Vid80gmx@gmail.com~~](mailto:Vid80gmx@gmail.com)",
            "[~Vid80gmx@gmail.com~](mailto:Vid80gmx@gmail.com)",
            "[*Vid80gmx@gmail.com*](mailto:Vid80gmx@gmail.com)",
            "[Vid80gmx&commat;gmail.com](mailto:Vid80gmx@gmail.com)",
            "[Vid80gmx&#64;gmail.com](mailto:Vid80gmx@gmail.com)",
            "[Vid80gmx&#0000064;gmail.com](mailto:Vid80gmx@gmail.com)",
            "[Vid80gmx&#x000040;gmail.com](mailto:Vid80gmx@gmail.com)",
            "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)<!-- trailing -->",
            "[Vid80gmx@gmail.com<!-- comment -->](mailto:Vid80gmx@gmail.com)",
            r"[Vid80gmx@gmail\.com](mailto:Vid80gmx@gmail.com)",
            "Example `\n\n" + canonical_markdown_link + "\n\n`",
            "Example [unfinished\n\n" + canonical_markdown_link,
            "\n~~~html\n<!--\n~~~\n\n" + canonical_markdown_link,
            "\n\n[guide]: /guide\n" + canonical_markdown_link,
            "Example ![unfinished\n\n" + canonical_markdown_link,
            "\n\n- ~~~\n  code\n\n" + canonical_markdown_link,
            "\n\n- item\n\n    " + canonical_markdown_link,
            "<span hidden>note</span> " + canonical_markdown_link,
            "<span>" + canonical_markdown_link + "</span>",
        )
        for accepted_markdown_link in accepted_markdown_links:
            with self.subTest(markdown=accepted_markdown_link):
                equivalent_markdown = original_markdown.replace(
                    canonical_markdown_link, accepted_markdown_link
                )
                self.assertNotEqual(equivalent_markdown, original_markdown)
                impressum.write_text(equivalent_markdown, encoding="utf-8")
                self.assertEqual(self.run_check(name), (0, None))

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

        paragraph_continuation = original_markdown.replace(
            "**Kontakt:** " + canonical_markdown_link,
            "**Kontakt:**\n    " + canonical_markdown_link,
        )
        self.assertNotEqual(paragraph_continuation, original_markdown)
        impressum.write_text(paragraph_continuation, encoding="utf-8")
        self.assertEqual(self.run_check(name), (0, None))

        accepted_markdown_contexts = (
            (
                f"```markdown\n{canonical_markdown_link}\n``` \n\n"
                "**Kontakt:** " + canonical_markdown_link
            ),
            (
                f"```markdown\n{canonical_markdown_link}\n```\t\n\n"
                "**Kontakt:** " + canonical_markdown_link
            ),
            (
                "`<div>`\n\n"
                "**Kontakt:** " + canonical_markdown_link
            ),
            (
                "`<script>`\n\n"
                "**Kontakt:** " + canonical_markdown_link
            ),
            (
                "\\<!-- escaped comment opener\n\n"
                "**Kontakt:** " + canonical_markdown_link
            ),
            (
                "\n\n<div>\n[hidden](mailto:hidden@example.invalid)\n\n"
                "**Kontakt:** " + canonical_markdown_link
            ),
            (
                "\n\n<div>\n[wrong](mailto:wrong@example.invalid)\n\n"
                "**Kontakt:** " + canonical_markdown_link
            ),
            (
                "`unclosed\n<span hidden>\n`**Kontakt:** "
                + canonical_markdown_link
            ),
        )
        for accepted_markdown_context in accepted_markdown_contexts:
            with self.subTest(markdown_context=accepted_markdown_context):
                equivalent_markdown = original_markdown.replace(
                    "**Kontakt:** " + canonical_markdown_link,
                    accepted_markdown_context,
                )
                self.assertNotEqual(equivalent_markdown, original_markdown)
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
            "case-folded contact target": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="MAILTO:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
            ),
            "case-folded contact label": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com">VID80GMX@GMAIL.COM</a>',
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
            "hidden contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com" hidden>'
                'Vid80gmx@gmail.com</a>',
            ),
            "display-none contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com" style="display:none">'
                'Vid80gmx@gmail.com</a>',
            ),
            "template-hidden contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com"><template>'
                'Vid80gmx@gmail.com</template></a>',
            ),
            "style-hidden contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com"><style>'
                'Vid80gmx@gmail.com</style></a>',
            ),
            "noscript-hidden contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com"><noscript>'
                'Vid80gmx@gmail.com</noscript></a>',
            ),
            "hidden-ancestor contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<div hidden><a href="mailto:Vid80gmx@gmail.com">'
                'Vid80gmx@gmail.com</a></div>',
            ),
            "template-ancestor contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<template><a href="mailto:Vid80gmx@gmail.com">'
                'Vid80gmx@gmail.com</a></template>',
            ),
            "textarea-ancestor contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<textarea><a href="mailto:Vid80gmx@gmail.com">'
                'Vid80gmx@gmail.com</a></textarea>',
            ),
            "noscript-ancestor contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<noscript><a href="mailto:Vid80gmx@gmail.com">'
                'Vid80gmx@gmail.com</a></noscript>',
            ),
            "visibility-hidden contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com" style="visibility:hidden">'
                'Vid80gmx@gmail.com</a>',
            ),
            "opacity-zero contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com" style="opacity:0">'
                'Vid80gmx@gmail.com</a>',
            ),
            "opacity-dot-zero contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com" style="opacity:.0">'
                'Vid80gmx@gmail.com</a>',
            ),
            "opacity-positive-zero contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com" style="opacity:+0">'
                'Vid80gmx@gmail.com</a>',
            ),
            "opacity-negative-zero contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com" style="opacity:-0">'
                'Vid80gmx@gmail.com</a>',
            ),
            "opacity-exponent-zero contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com" style="opacity:0e0">'
                'Vid80gmx@gmail.com</a>',
            ),
            "canvas-fallback contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com) "
                '<canvas><a href="mailto:Vid80gmx@gmail.com">'
                "Vid80gmx@gmail.com</a></canvas>",
            ),
            "svg-self-closing contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com) "
                '<svg><a href="mailto:Vid80gmx@gmail.com"/>'
                "Vid80gmx@gmail.com</svg>",
            ),
            "malformed-marked-section contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n<![x]>",
            ),
            "closed-details contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<details><a href="mailto:Vid80gmx@gmail.com">'
                'Vid80gmx@gmail.com</a></details>',
            ),
            "closed-dialog contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<dialog><a href="mailto:Vid80gmx@gmail.com">'
                'Vid80gmx@gmail.com</a></dialog>',
            ),
            "closed-popover contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<div popover><a href="mailto:Vid80gmx@gmail.com">'
                'Vid80gmx@gmail.com</a></div>',
            ),
            "self-closing-hidden-ancestor contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<div hidden/><a href="mailto:Vid80gmx@gmail.com">'
                'Vid80gmx@gmail.com</a>',
            ),
            "nested-anchor contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com">'
                '<a href="mailto:kontakt@example.invalid">Vid80gmx@gmail.com</a>',
            ),
            "hidden-label contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com">'
                '<span hidden>Vid80gmx@gmail.com</span></a>',
            ),
            "select-ancestor contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<select><a href="mailto:Vid80gmx@gmail.com">'
                'Vid80gmx@gmail.com</a></select>',
            ),
            "opacity cascade hidden contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com" style="opacity:1;opacity:0">'
                "Vid80gmx@gmail.com</a>",
            ),
            "opacity important hidden contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com" '
                'style="opacity:0!important;opacity:1">'
                "Vid80gmx@gmail.com</a>",
            ),
            "display cascade hidden contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com" '
                'style="display:inline;display:none">Vid80gmx@gmail.com</a>',
            ),
            "visibility cascade hidden contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com" '
                'style="visibility:visible;visibility:hidden">'
                "Vid80gmx@gmail.com</a>",
            ),
            "content-visibility cascade hidden contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com" '
                'style="content-visibility:visible;content-visibility:hidden">'
                "Vid80gmx@gmail.com</a>",
            ),
            "entity-decoded decimal href contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx&#64;gmail.com">Vid80gmx@gmail.com</a>',
            ),
            "entity-decoded hexadecimal href contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx&#x40;gmail.com">'
                "Vid80gmx@gmail.com</a>",
            ),
            "entity-decoded named href contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx&commat;gmail.com">'
                "Vid80gmx@gmail.com</a>",
            ),
            "entity-decoded overlong href contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx&#000000000064;gmail.com">'
                "Vid80gmx@gmail.com</a>",
            ),
            "entity-decoded first duplicate href contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx&#64;gmail.com" '
                'href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
            ),
            "visible-br contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@<br>'
                "gmail.com</a>",
            ),
            "non-breaking-space contact label": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com&nbsp;'
                "</a>",
            ),
            "nested same-name hidden ancestor contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com"><span hidden><span></span>'
                "Vid80gmx@gmail.com</span></a>",
            ),
            "calc-zero opacity contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com" style="opacity:calc(0)">'
                "Vid80gmx@gmail.com</a>",
            ),
            "transparent-text contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com" style="color:transparent">'
                "Vid80gmx@gmail.com</a>",
            ),
            "transparent-rgba-text contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com" '
                'style="color:rgba(1, 2, 3, 0)">Vid80gmx@gmail.com</a>',
            ),
            "transparent-hex-text contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com" style="color:#1230">'
                "Vid80gmx@gmail.com</a>",
            ),
            "transparent-text-fill contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com" '
                'style="-webkit-text-fill-color:rgba(1,2,3,0)">'
                "Vid80gmx@gmail.com</a>",
            ),
            "filter-opacity-zero contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com" style="filter:opacity(0)">'
                "Vid80gmx@gmail.com</a>",
            ),
            "filter-calc-opacity-zero contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:Vid80gmx@gmail.com" '
                'style="filter:opacity(calc(0))">Vid80gmx@gmail.com</a>',
            ),
            "math-fallback contact link": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com) "
                '<math><a href="mailto:Vid80gmx@gmail.com">'
                "Vid80gmx@gmail.com</a></math>",
            ),
            "hidden impressum section contact link": (
                '<section class="fsec" aria-labelledby="imp-h">',
                '<section class="fsec" aria-labelledby="imp-h" hidden>',
            ),
            "hidden footer contact link": (
                '<footer id="foot">',
                '<footer id="foot" hidden>',
            ),
            "duplicate href with wrong first target": (
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
                '<a href="mailto:kontakt@example.invalid" '
                'href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
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
            "case-folded contact label": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "[VID80GMX@GMAIL.COM](mailto:Vid80gmx@gmail.com)",
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
            "code-fence-without-outside-contact": (
                "**Kontakt:** [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
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
            "blockquote-indented-code-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                ">     [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "list-fence-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "- ```markdown\n"
                "  [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)\n  ```",
            ),
            "blockquote-list-fence-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "> - ```markdown\n"
                ">   [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)\n"
                ">   ```",
            ),
            "new-list-item-fence-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "- ```markdown\n"
                "  code\n"
                "- ```\n"
                "  [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "blockquote-fence-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "> ```markdown\n"
                "> [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)\n> ```",
            ),
            "blockquote-tilde-fence-hidden contact link": (
                "**Kontakt:** [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "> ~~~markdown\n"
                "> [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)\n> ~~~",
            ),
            "top-level-fence-container-mismatch contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "```markdown\n> ```\n"
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)\n```",
            ),
            "blockquote-fence-container-mismatch contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "> ```markdown\n```\n"
                "> [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)\n> ```",
            ),
            "list-fence-container-mismatch contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "- ```markdown\n```\n"
                "  [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)\n  ```",
            ),
            "list-indented-code-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "-     [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "nested-list-indented-code-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "- -     [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "raw-script-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<script>\n[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)\n"
                "</script>",
            ),
            "raw-style-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<style>\n[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)\n"
                "</style>",
            ),
            "raw-pre-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<pre>\n[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)\n"
                "</pre>",
            ),
            "raw-code-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<code>\n[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)\n"
                "</code>",
            ),
            "raw-html-attribute-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                '<span title="[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)">'
                "</span>",
            ),
            "link-title-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                '[label](https://example.com '
                '"[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)")',
            ),
            "link-destination-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "[label](https://example.com/"
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com))",
            ),
            "raw-html-block-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<div>[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)</div>",
            ),
            "self-closing-raw-html-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<span/>\n[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "dedented-list-html-block-hidden contact link": (
                "**Kontakt:** [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "\n- text\n<span>\n"
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "table-html-block-hidden contact link": (
                "**Kontakt:** [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "\n| a | b |\n| - | - |\n<span>\n"
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "raw-html-base-block-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<base>[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)</base>",
            ),
            "raw-script-unclosed-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<script>\n[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "raw-pre-unclosed-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<pre>\n[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "raw-div-unclosed-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<div>\n[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "raw-div-blank-boundary-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "\n<div>\n[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)\n\n"
                "[visible](mailto:visible@example.invalid)",
            ),
            "raw-code-unclosed-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<code>\n[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "unclosed-comment-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<!--\n[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "comment-block-same-line contact link": (
                "**Kontakt:** [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "<!-- leading -->[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "comment-separated contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "[Vid80gmx@gmail.com]<!-- separator -->"
                "(mailto:Vid80gmx@gmail.com)",
            ),
            "comment-in-code-label contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "[`Vid80gmx@gmail.com<!-- comment -->`]"
                "(mailto:Vid80gmx@gmail.com)",
            ),
            "image-description-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "![description [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)]"
                "(image.png)",
            ),
            "image-title-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                '![description](image.png '
                '"[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)")',
            ),
            "direct-image-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "![Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "even-backslash-code-span-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "\\\\`[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)`",
            ),
            "escaped-backtick-code-span-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                r"\` `[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)`",
            ),
            "cross-paragraph-code-span-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "`unclosed\n\n"
                '<span hidden title="`">[Vid80gmx@gmail.com]'
                "(mailto:Vid80gmx@gmail.com)</span>",
            ),
            "cross-container-code-span-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "- `unclosed\n"
                '> <span hidden title="`">[Vid80gmx@gmail.com]'
                "(mailto:Vid80gmx@gmail.com)</span>",
            ),
            "code-span-entity-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "[`Vid80gmx&#64;gmail.com`](mailto:Vid80gmx@gmail.com)",
            ),
            "numeric-entity-without-semicolon-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "[Vid80gmx&#64gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "eight-digit-decimal-entity-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "[Vid80gmx&#00000064;gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "seven-digit-hex-entity-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "[Vid80gmx&#x0000040;gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "overlong-decimal-entity-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "[Vid80gmx&#000000064;gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "overlong-hex-entity-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "[Vid80gmx&#x000000064;gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "footnote-definition-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "[^note]: [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "footnote-continuation-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "[^note]: footnote\n"
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "reference-definition-title-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                '[unused]: mailto:Vid80gmx@gmail.com '
                '"[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)"',
            ),
            "reference-definition-next-title-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "[unused]: mailto:Vid80gmx@gmail.com\n"
                '"[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)"',
            ),
            "indented-reference-definition-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "  [unused]: mailto:x\n"
                '  "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)"',
            ),
            "next-line-reference-destination-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "[unused]:\nmailto:x\n"
                '"[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)"',
            ),
            "multiline-reference-title-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                '[unused]: mailto:x\n  "first\n'
                "  [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)\n"
                '  more"',
            ),
            "inline-html-label-out-of-scope contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "[<span>Vid80gmx@gmail.com</span>](mailto:Vid80gmx@gmail.com)",
            ),
            "hidden-inline-html-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                '<span hidden>[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)</span>',
            ),
            "autolink-out-of-scope contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<Vid80gmx@gmail.com>",
            ),
            "reference-link-out-of-scope contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "[Vid80gmx@gmail.com][contact]\n\n"
                "[contact]: mailto:Vid80gmx@gmail.com",
            ),
            "raw-html-anchor-out-of-scope contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
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
            "intraword-underscore-label": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "[Vid80gmx_@gmail.com_](mailto:Vid80gmx@gmail.com)",
            ),
            "triple-tilde-label": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "[~~~Vid80gmx@gmail.com~~~](mailto:Vid80gmx@gmail.com)",
            ),
            "nested-outer-link contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "[outer [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)]"
                "(https://example.com)",
            ),
            "cross-paragraph-link-destination contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "[Vid80gmx@gmail.com](\n\nmailto:Vid80gmx@gmail.com)",
            ),
            "code-suffixed-bare-destination contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com`suffix`)",
            ),
            "list-paragraph-indented-code contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "- item\n\n        [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "fence-without-outside-link contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "```markdown\n[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)\n```",
            ),
            "shorter-fence-closer contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "````markdown\n[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)\n```\n"
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "different-fence-family-closer contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "```markdown\n[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)\n~~~\n"
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
            ),
            "processing-instruction-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<?php echo '[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)'; ?>",
            ),
            "cdata-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<![CDATA[[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)]]>",
            ),
            "declaration-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "Vid80gmx@gmail.com (mailto:Vid80gmx@gmail.com)\n\n"
                "<!DOCTYPE [Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)>",
            ),
            "mathml-hidden contact link": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                "<math>[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)</math>",
            ),
            "escaped-extra-label": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                r"[Vid80gmx@gmail.com\*](mailto:Vid80gmx@gmail.com)",
            ),
            "escaped-backtick-label": (
                "[Vid80gmx@gmail.com](mailto:Vid80gmx@gmail.com)",
                r"[Vid80gmx@gmail.com\`](mailto:Vid80gmx@gmail.com)",
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

    def test_regression_css_alpha_and_inline_declaration_precedence(self):
        html = self.root / "index.html"
        original = html.read_text(encoding="utf-8")

        accepted_links = (
            '<a style="color:#112233f0" href="mailto:Vid80gmx@gmail.com">'
            "Vid80gmx@gmail.com</a>",
            '<a style="color:#123f" href="mailto:Vid80gmx@gmail.com">'
            "Vid80gmx@gmail.com</a>",
            '<a style="opacity:0;opacity:1" href="mailto:Vid80gmx@gmail.com">'
            "Vid80gmx@gmail.com</a>",
            '<a style="opacity:0.01" href="mailto:Vid80gmx@gmail.com">'
            "Vid80gmx@gmail.com</a>",
        )
        for replacement in accepted_links:
            with self.subTest(replacement=replacement, expected="visible"):
                mutated = original.replace(self.CANONICAL_HTML_LINK, replacement)
                self.assertNotEqual(mutated, original)
                self.write_html_pair(mutated)
                self.assert_impressum_check(True)

        rejected_links = (
            '<a style="color:#11223300" href="mailto:Vid80gmx@gmail.com">'
            "Vid80gmx@gmail.com</a>",
            '<a style="color:#1230" href="mailto:Vid80gmx@gmail.com">'
            "Vid80gmx@gmail.com</a>",
            '<a style="opacity:0;opacity:bogus" '
            'href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>',
            '<a style="opacity:-0.1" href="mailto:Vid80gmx@gmail.com">'
            "Vid80gmx@gmail.com</a>",
        )
        for replacement in rejected_links:
            with self.subTest(replacement=replacement, expected="hidden"):
                mutated = original.replace(self.CANONICAL_HTML_LINK, replacement)
                self.assertNotEqual(mutated, original)
                self.write_html_pair(mutated)
                self.assert_impressum_check(False)

    def test_regression_html_visible_label_block_boundaries(self):
        html = self.root / "index.html"
        original = html.read_text(encoding="utf-8")

        accepted_links = (
            '<a href="mailto:Vid80gmx@gmail.com"><span>Vid80gmx@</span>'
            "<span>gmail.com</span></a>",
        )
        for replacement in accepted_links:
            with self.subTest(replacement=replacement, expected="visible"):
                mutated = original.replace(self.CANONICAL_HTML_LINK, replacement)
                self.assertNotEqual(mutated, original)
                self.write_html_pair(mutated)
                self.assert_impressum_check(True)

        rejected_links = (
            '<a href="mailto:Vid80gmx@gmail.com">'
            '<span style="display:block">Vid80gmx@</span>gmail.com</a>',
            '<a href="mailto:Vid80gmx@gmail.com"><div>Vid80gmx@</div>'
            "<div>gmail.com</div></a>",
        )
        for replacement in rejected_links:
            with self.subTest(replacement=replacement, expected="hidden"):
                mutated = original.replace(self.CANONICAL_HTML_LINK, replacement)
                self.assertNotEqual(mutated, original)
                self.write_html_pair(mutated)
                self.assert_impressum_check(False)

    def test_regression_markdown_hidden_html_and_list_fences(self):
        impressum = self.root / "IMPRESSUM.md"
        original = impressum.read_text(encoding="utf-8")
        original_contact = "**Kontakt:** " + self.CANONICAL_MARKDOWN_LINK

        accepted_contexts = (
            "\\<span hidden>\n" + self.CANONICAL_MARKDOWN_LINK,
            "- ~~~\n  - sample\n- sibling\n"
            + self.CANONICAL_MARKDOWN_LINK,
            "- ~~~\n  sample\n\noutside\n"
            + self.CANONICAL_MARKDOWN_LINK,
            " - ~~~\n\n  " + self.CANONICAL_MARKDOWN_LINK,
        )
        for context in accepted_contexts:
            with self.subTest(context=context, expected="visible"):
                mutated = original.replace(original_contact, context)
                self.assertNotEqual(mutated, original)
                impressum.write_text(mutated, encoding="utf-8")
                self.assert_impressum_check(True)

        rejected_contexts = (
            "<span hidden>\n" + self.CANONICAL_MARKDOWN_LINK,
            "- ~~~\n  - sample\n  " + self.CANONICAL_MARKDOWN_LINK,
            "- ~~~\n  sample\n\n  " + self.CANONICAL_MARKDOWN_LINK,
            "- ~~~\n\n  " + self.CANONICAL_MARKDOWN_LINK,
        )
        for context in rejected_contexts:
            with self.subTest(context=context, expected="hidden"):
                mutated = original.replace(original_contact, context)
                self.assertNotEqual(mutated, original)
                impressum.write_text(mutated, encoding="utf-8")
                self.assert_impressum_check(False)

    def test_regression_markdown_comments_and_processing_instructions(self):
        impressum = self.root / "IMPRESSUM.md"
        original = impressum.read_text(encoding="utf-8")
        original_contact = "**Kontakt:** " + self.CANONICAL_MARKDOWN_LINK

        accepted_contexts = (
            "<!-- ` -->` `\n\n" + self.CANONICAL_MARKDOWN_LINK,
            "`<!--`\n\n" + self.CANONICAL_MARKDOWN_LINK,
            "<?probe?>\n" + self.CANONICAL_MARKDOWN_LINK,
            "> <?probe\n\n" + self.CANONICAL_MARKDOWN_LINK,
            "prefix <!-- note --> " + self.CANONICAL_MARKDOWN_LINK,
        )
        for context in accepted_contexts:
            with self.subTest(context=context, expected="visible"):
                mutated = original.replace(original_contact, context)
                self.assertNotEqual(mutated, original)
                impressum.write_text(mutated, encoding="utf-8")
                self.assert_impressum_check(True)

        rejected_contexts = (
            "<?probe\n\n" + self.CANONICAL_MARKDOWN_LINK,
            "<?probe?>" + self.CANONICAL_MARKDOWN_LINK,
            "<?probe\n?>" + self.CANONICAL_MARKDOWN_LINK,
            "  <!-- note -->" + self.CANONICAL_MARKDOWN_LINK,
            "<div>\n" + self.CANONICAL_MARKDOWN_LINK,
        )
        for context in rejected_contexts:
            with self.subTest(context=context, expected="hidden"):
                mutated = original.replace(original_contact, context)
                self.assertNotEqual(mutated, original)
                impressum.write_text(mutated, encoding="utf-8")
                self.assert_impressum_check(False)

    def test_regression_impressum_scope_visibility(self):
        html = self.root / "index.html"
        original = html.read_text(encoding="utf-8")

        moved_anchor = original.replace(
            self.CANONICAL_HTML_LINK,
            "Vid80gmx@gmail.com",
        )
        footer_paragraph = (
            '<p class="savehint"><span id="savestate">'
            "💾 Gespeichert auf diesem Gerät</span></p>"
        )
        self.assertIn(footer_paragraph, moved_anchor)
        moved_anchor = moved_anchor.replace(
            footer_paragraph,
            footer_paragraph.replace(
                "</p>",
                " " + self.CANONICAL_HTML_LINK + "</p>",
            ),
        )
        self.assertIn(self.CANONICAL_HTML_LINK, moved_anchor)
        self.write_html_pair(moved_anchor)
        self.assert_impressum_check(False)

        section_start = original.index(
            '<section class="fsec" aria-labelledby="imp-h">'
        )
        section_end = original.index("</section>", section_start) + len(
            "</section>"
        )
        impressum_section = original[section_start:section_end]
        commented_section = (
            original[:section_start]
            + "<!--\n"
            + impressum_section
            + "\n-->"
            + original[section_end:]
        )
        for detail in ("Lowgiga", "New York 11354 USA", "Vid80gmx@gmail.com"):
            self.assertIn(detail, commented_section)
        self.write_html_pair(commented_section)
        self.assert_impressum_check(False)

        hidden_ancestor = original.replace(
            '<footer id="foot">',
            '<div hidden><footer id="foot">',
            1,
        ).replace("</footer>", "</footer></div>", 1)
        self.assertNotEqual(hidden_ancestor, original)
        self.write_html_pair(hidden_ancestor)
        self.assert_impressum_check(False)

    def test_regression_markdown_comment_block_line_semantics(self):
        impressum = self.root / "IMPRESSUM.md"
        original = impressum.read_text(encoding="utf-8")
        original_contact = "**Kontakt:** " + self.CANONICAL_MARKDOWN_LINK

        same_line = "<!-- leading -->" + self.CANONICAL_MARKDOWN_LINK
        mutated = original.replace(original_contact, same_line)
        self.assertNotEqual(mutated, original)
        impressum.write_text(mutated, encoding="utf-8")
        self.assert_impressum_check(False)

        next_line = "<!-- leading -->\n" + self.CANONICAL_MARKDOWN_LINK
        mutated = original.replace(original_contact, next_line)
        self.assertNotEqual(mutated, original)
        impressum.write_text(mutated, encoding="utf-8")
        self.assert_impressum_check(True)

    def test_regression_markdown_heading_indented_code(self):
        impressum = self.root / "IMPRESSUM.md"
        original = impressum.read_text(encoding="utf-8")
        original_contact = "**Kontakt:** " + self.CANONICAL_MARKDOWN_LINK

        immediate_code = "# Kontakt\n    " + self.CANONICAL_MARKDOWN_LINK
        mutated = original.replace(original_contact, immediate_code)
        self.assertNotEqual(mutated, original)
        impressum.write_text(mutated, encoding="utf-8")
        self.assert_impressum_check(False)

        after_blank = "# Kontakt\n\n" + self.CANONICAL_MARKDOWN_LINK
        mutated = original.replace(original_contact, after_blank)
        self.assertNotEqual(mutated, original)
        impressum.write_text(mutated, encoding="utf-8")
        self.assert_impressum_check(True)

        for underline in ("=", "-"):
            with self.subTest(setext_underline=underline, expected="hidden"):
                setext_code = (
                    f"Kontakt\n{underline}\n    " + self.CANONICAL_MARKDOWN_LINK
                )
                mutated = original.replace(original_contact, setext_code)
                self.assertNotEqual(mutated, original)
                impressum.write_text(mutated, encoding="utf-8")
                self.assert_impressum_check(False)

            with self.subTest(setext_underline=underline, expected="visible"):
                setext_link = (
                    f"Kontakt\n{underline}\n" + self.CANONICAL_MARKDOWN_LINK
                )
                mutated = original.replace(original_contact, setext_link)
                self.assertNotEqual(mutated, original)
                impressum.write_text(mutated, encoding="utf-8")
                self.assert_impressum_check(True)

    def test_regression_markdown_fence_info_comment_literal(self):
        impressum = self.root / "IMPRESSUM.md"
        original = impressum.read_text(encoding="utf-8")
        original_contact = "**Kontakt:** " + self.CANONICAL_MARKDOWN_LINK

        after_fence = (
            "```markdown <!--\ncode\n```\n" + self.CANONICAL_MARKDOWN_LINK
        )
        mutated = original.replace(original_contact, after_fence)
        self.assertNotEqual(mutated, original)
        impressum.write_text(mutated, encoding="utf-8")
        self.assert_impressum_check(True)

        after_list_fence = (
            "- ```markdown <!--\n  code\n  ```\n"
            + self.CANONICAL_MARKDOWN_LINK
        )
        mutated = original.replace(original_contact, after_list_fence)
        self.assertNotEqual(mutated, original)
        impressum.write_text(mutated, encoding="utf-8")
        self.assert_impressum_check(True)

        inside_fence = (
            "```markdown <!--\n" + self.CANONICAL_MARKDOWN_LINK + "\n```"
        )
        mutated = original.replace(original_contact, inside_fence)
        self.assertNotEqual(mutated, original)
        impressum.write_text(mutated, encoding="utf-8")
        self.assert_impressum_check(False)

    def test_regression_html_details_and_visibility_overrides(self):
        html = self.root / "index.html"
        original = html.read_text(encoding="utf-8")

        accepted_links = (
            "<details><summary>" + self.CANONICAL_HTML_LINK
            + "</summary></details>",
            "<details open>" + self.CANONICAL_HTML_LINK + "</details>",
            '<div style="visibility:hidden">'
            '<a style="visibility:visible" '
            'href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a></div>',
            '<div style="visibility:hidden"><span style="visibility:visible">'
            '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a>'
            "</span></div>",
            '<a style="visibility:hidden" '
            'href="mailto:Vid80gmx@gmail.com"><span style="visibility:visible">'
            "Vid80gmx@gmail.com</span></a>",
        )
        for replacement in accepted_links:
            with self.subTest(replacement=replacement, expected="visible"):
                mutated = original.replace(self.CANONICAL_HTML_LINK, replacement)
                self.assertNotEqual(mutated, original)
                self.write_html_pair(mutated)
                self.assert_impressum_check(True)

        rejected_links = (
            "<details>" + self.CANONICAL_HTML_LINK + "</details>",
            "<details><summary>More</summary><summary>"
            + self.CANONICAL_HTML_LINK
            + "</summary></details>",
            '<div style="visibility:hidden">'
            '<a href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a></div>',
            '<div style="opacity:0">'
            '<a style="visibility:visible" '
            'href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a></div>',
            '<div style="display:none">'
            '<a style="visibility:visible" '
            'href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a></div>',
            '<div style="clip-path:inset(50%)">'
            '<a style="visibility:visible" '
            'href="mailto:Vid80gmx@gmail.com">Vid80gmx@gmail.com</a></div>',
        )
        for replacement in rejected_links:
            with self.subTest(replacement=replacement, expected="hidden"):
                mutated = original.replace(self.CANONICAL_HTML_LINK, replacement)
                self.assertNotEqual(mutated, original)
                self.write_html_pair(mutated)
                self.assert_impressum_check(False)

        self.write_html_pair(original)
        impressum = self.root / "IMPRESSUM.md"
        original_markdown = impressum.read_text(encoding="utf-8")
        original_contact = "**Kontakt:** " + self.CANONICAL_MARKDOWN_LINK
        visible_markdown = (
            '<span style="visibility:hidden">'
            '<span style="visibility:visible">'
            + self.CANONICAL_MARKDOWN_LINK
            + "</span></span>"
        )
        mutated = original_markdown.replace(original_contact, visible_markdown)
        self.assertNotEqual(mutated, original_markdown)
        impressum.write_text(mutated, encoding="utf-8")
        self.assert_impressum_check(True)

        hidden_markdown = (
            '<span style="visibility:hidden">'
            + self.CANONICAL_MARKDOWN_LINK
            + "</span>"
        )
        mutated = original_markdown.replace(original_contact, hidden_markdown)
        self.assertNotEqual(mutated, original_markdown)
        impressum.write_text(mutated, encoding="utf-8")
        self.assert_impressum_check(False)

        first_summary_markdown = (
            "prefix <details><summary>"
            + self.CANONICAL_MARKDOWN_LINK
            + "</summary></details>"
        )
        mutated = original_markdown.replace(
            original_contact, first_summary_markdown
        )
        self.assertNotEqual(mutated, original_markdown)
        impressum.write_text(mutated, encoding="utf-8")
        self.assert_impressum_check(True)

        second_summary_markdown = (
            "prefix <details><summary>More</summary><summary>"
            + self.CANONICAL_MARKDOWN_LINK
            + "</summary></details>"
        )
        mutated = original_markdown.replace(
            original_contact, second_summary_markdown
        )
        self.assertNotEqual(mutated, original_markdown)
        impressum.write_text(mutated, encoding="utf-8")
        self.assert_impressum_check(False)

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
