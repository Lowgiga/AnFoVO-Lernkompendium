from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import re
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
HTML_BYTES = (ROOT / "index.html").read_bytes()
ANDROID_ASSETS = ROOT / "android" / "app" / "src" / "main" / "assets"
HTML_TITLE = re.search(r"<title>(.*?)</title>", HTML, re.S).group(1).strip()
DATA_VERSION = re.search(r'var DATA = \{"version":\s*"([^"]+)"', HTML).group(1)
MANIFEST = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
MANIFEST_VERSION = MANIFEST.get("version", "")
SW = (ROOT / "sw.js").read_text(encoding="utf-8")
SW_VERSION = re.search(r"var VERSION = '([^']+)'", SW).group(1)
PKG_VERSION = json.loads(
    (ROOT / "tests" / "package.json").read_text(encoding="utf-8")
).get("version", "")
ANDROID_HTML = ANDROID_ASSETS / "index.html"
PWA_FILES = (
    "manifest.json",
    "sw.js",
    "icon-192.png",
    "icon-512.png",
    "icon-512-maskable.png",
)
IMPRESSUM_FILE = ROOT / "IMPRESSUM.md"
IMPRESSUM_MD = (
    IMPRESSUM_FILE.read_text(encoding="utf-8") if IMPRESSUM_FILE.is_file() else ""
)
PROVIDER_NAME = "Lowgiga"
PROVIDER_ADDRESS = "New York 11354 USA"
CONTACT_EMAIL = "Vid80gmx@gmail.com"
SERVICE_WORKER_BUILD = "web-pwa-2.9.5-legal.1"
PLACEHOLDER = "[vor Veröffentlichung ergänzen: Name, Anschrift, Kontakt]"
JS = (ROOT / "algorithm" / "robot-navigation.js").read_text(encoding="utf-8").strip()
ARCHITECTURE = (ROOT / "docs" / "ARCHITECTURE.md").read_text(encoding="utf-8")


def _trim_url_whitespace(value):
    return value.strip(" \t\n\r\f\v")


def _is_mailto_destination(destination, email):
    scheme, separator, address = destination.partition(":")
    return (
        bool(separator)
        and scheme.casefold() == "mailto"
        and address == email
    )


class _ContactAnchorParser(HTMLParser):
    """Collect only native, non-nested anchors from explicitly rendered HTML."""

    VOID_ELEMENTS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
    IGNORED_CONTAINERS = {
        "datalist",
        "details",
        "dialog",
        "head",
        "iframe",
        "math",
        "noembed",
        "noframes",
        "noscript",
        "object",
        "optgroup",
        "option",
        "plaintext",
        "script",
        "select",
        "style",
        "svg",
        "template",
        "textarea",
        "title",
        "xmp",
    }
    HIDDEN_STYLE = re.compile(
        r"(?:^|;)\s*(?:"
        r"display\s*:\s*none(?![-\w])|"
        r"visibility\s*:\s*hidden(?![-\w])|"
        r"opacity\s*:\s*(?:0+(?:\.0+)?|\.0+)(?![0-9.])"
        r")",
        re.IGNORECASE,
    )

    def __init__(self, email):
        super().__init__(convert_charrefs=True)
        self.email = email
        self.found = False
        self._anchors = []
        self._hidden_tags = []
        self._ignored_tag = None
        self._ignored_depth = 0

    @staticmethod
    def _first_attr(attrs, name):
        return next((value for key, value in attrs if key.lower() == name), None)

    @staticmethod
    def _has_attr(attrs, name):
        return any(key.lower() == name for key, _ in attrs)

    @classmethod
    def _is_hidden(cls, attrs):
        style = cls._first_attr(attrs, "style") or ""
        aria_hidden = cls._first_attr(attrs, "aria-hidden") or ""
        return (
            cls._has_attr(attrs, "hidden")
            or cls._has_attr(attrs, "inert")
            or aria_hidden.strip().casefold() == "true"
            or bool(cls.HIDDEN_STYLE.search(style))
        )

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs = list(attrs)
        if self._ignored_tag:
            if tag == self._ignored_tag:
                self._ignored_depth += 1
            return
        if tag in self.IGNORED_CONTAINERS:
            renders_when_open = tag in {"details", "dialog"} and self._has_attr(
                attrs, "open"
            )
            if not renders_when_open:
                self._ignored_tag = tag
                self._ignored_depth = 1
                return

        parent_hidden = bool(self._hidden_tags)
        element_hidden = self._is_hidden(attrs)
        if element_hidden and tag not in self.VOID_ELEMENTS:
            self._hidden_tags.append(tag)
        if tag == "a":
            href_values = [value for key, value in attrs if key.lower() == "href"]
            nested_anchor = bool(self._anchors)
            if nested_anchor:
                self._anchors[-1]["nested_anchor"] = True
            self._anchors.append(
                {
                    "href": href_values[0] if href_values else None,
                    "duplicate_href": len(href_values) > 1,
                    "nested_anchor": nested_anchor,
                    "text": [],
                    "hidden": parent_hidden or element_hidden,
                }
            )

    def handle_startendtag(self, tag, attrs):
        tag = tag.lower()
        if tag in self.VOID_ELEMENTS:
            super().handle_startendtag(tag, attrs)
            return
        # HTML ignores the self-closing slash on non-void elements.
        self.handle_starttag(tag, attrs)

    def handle_data(self, data):
        if self._ignored_tag:
            return
        if self._anchors and not self._hidden_tags:
            self._anchors[-1]["text"].append(data)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if self._ignored_tag:
            if tag == self._ignored_tag:
                self._ignored_depth -= 1
                if self._ignored_depth == 0:
                    self._ignored_tag = None
            return

        for index in range(len(self._hidden_tags) - 1, -1, -1):
            if self._hidden_tags[index] == tag:
                del self._hidden_tags[index]
                break

        if tag == "a" and self._anchors:
            anchor = self._anchors.pop()
            visible_text = " ".join("".join(anchor["text"]).split())
            href = _trim_url_whitespace(anchor["href"] or "")
            if (
                not anchor["hidden"]
                and not anchor["duplicate_href"]
                and not anchor["nested_anchor"]
                and not self._hidden_tags
                and _is_mailto_destination(href, self.email)
                and visible_text == self.email
            ):
                self.found = True


def has_html_contact_link(fragment, email):
    parser = _ContactAnchorParser(email)
    parser.feed(fragment)
    parser.close()
    return parser.found


def _mask_source_range(masked, start, end):
    for index in range(start, end):
        if masked[index] not in "\r\n":
            masked[index] = " "


def _mask_markdown_comments(source):
    masked = list(source)
    for comment in re.finditer(r"<!--[\s\S]*?(?:-->|$)", source):
        _mask_source_range(masked, comment.start(), comment.end())
    return "".join(masked)


def _markdown_blockquote_content(line):
    candidate = line
    quote_depth = 0
    while True:
        blockquote = re.match(r"^[ \t]{0,3}>[ \t]?", candidate)
        if not blockquote:
            break
        candidate = candidate[blockquote.end() :]
        quote_depth += 1
    return candidate, quote_depth


def _markdown_container_content(line):
    candidate, quote_depth = _markdown_blockquote_content(line)
    list_item = re.match(
        r"^[ \t]{0,3}(?:[*+-]|\d{1,9}[.)])([ \t]+)(.*)$",
        candidate,
    )
    if list_item:
        indentation = list_item.group(1)
        if not indentation.startswith("\t") and len(indentation.expandtabs(4)) < 4:
            candidate = list_item.group(2)
    return candidate, quote_depth


def _markdown_indent(line):
    expanded = line.expandtabs(4)
    return len(expanded) - len(expanded.lstrip(" "))


def _mask_markdown_code_blocks(source):
    masked = list(source)
    offset = 0
    fence = None
    previous_blank = True
    indented_code = False

    for raw_line in source.splitlines(keepends=True):
        line = raw_line.rstrip("\r\n")
        content, quote_depth = _markdown_container_content(line)
        marker = re.match(r"^[ \t]{0,3}(`{3,}|~{3,})(.*)$", content)

        if fence and quote_depth < fence[2]:
            fence = None

        if fence:
            closes_fence = (
                marker
                and quote_depth == fence[2]
                and marker.group(1)[0] == fence[0]
                and len(marker.group(1)) >= fence[1]
                and not marker.group(2).strip(" \t")
            )
            _mask_source_range(masked, offset, offset + len(raw_line))
            if closes_fence:
                fence = None
            offset += len(raw_line)
            continue

        if marker:
            fence = (marker.group(1)[0], len(marker.group(1)), quote_depth)
            _mask_source_range(masked, offset, offset + len(raw_line))
            offset += len(raw_line)
            continue

        code_content, _ = _markdown_blockquote_content(line)
        list_item = re.match(
            r"^[ \t]{0,3}(?:[*+-]|\d{1,9}[.)])([ \t]+)(.*)$",
            code_content,
        )
        blank = not code_content.strip()
        is_code = False

        if list_item:
            indentation = list_item.group(1)
            is_code = indentation.startswith("\t") or len(indentation.expandtabs(4)) >= 4
        else:
            indent = _markdown_indent(code_content)
            if indented_code:
                is_code = blank or indent >= 4
                if not is_code:
                    indented_code = False
            elif indent >= 4 and previous_blank:
                indented_code = True
                is_code = True

        if is_code:
            _mask_source_range(masked, offset, offset + len(raw_line))
        else:
            previous_blank = blank
        offset += len(raw_line)

    return "".join(masked)


def _mask_markdown_reference_definitions(source):
    masked = list(source)
    definition = re.compile(
        r"^[ \t]{0,3}(?:>[ \t]?)*\[[^\]\n]+\]:[^\n]*(?:\n|$)",
        flags=re.MULTILINE,
    )
    for match in definition.finditer(source):
        _mask_source_range(masked, match.start(), match.end())
    return "".join(masked)


def _markdown_html_tag_events(source):
    events = []
    index = 0
    while index < len(source):
        start = source.find("<", index)
        if start == -1:
            break
        if source.startswith("<!--", start):
            comment_end = source.find("-->", start + 4)
            index = len(source) if comment_end == -1 else comment_end + 3
            continue
        if source.startswith("<![CDATA[", start):
            cdata_end = source.find("]]>", start + 9)
            end = len(source) if cdata_end == -1 else cdata_end + 3
            events.append((start, end, "", False, True))
            index = end
            continue
        if source.startswith("<?", start):
            instruction_end = source.find("?>", start + 2)
            end = len(source) if instruction_end == -1 else instruction_end + 2
            events.append((start, end, "", False, True))
            index = end
            continue
        if source.startswith("<!", start):
            declaration_end = source.find(">", start + 2)
            end = len(source) if declaration_end == -1 else declaration_end + 1
            events.append((start, end, "", False, True))
            index = end
            continue

        cursor = start + 1
        closing = cursor < len(source) and source[cursor] == "/"
        if closing:
            cursor += 1
        name_start = cursor
        while cursor < len(source) and (
            source[cursor].isalnum() or source[cursor] in "-_"
        ):
            cursor += 1
        if cursor == name_start or (
            cursor < len(source)
            and source[cursor] not in " \t\r\n\f/>"
        ):
            index = start + 1
            continue

        name = source[name_start:cursor].lower()
        quote = ""
        while cursor < len(source):
            character = source[cursor]
            if quote:
                if character == quote:
                    quote = ""
            elif character in "\"'":
                quote = character
            elif character == ">":
                break
            cursor += 1

        if cursor >= len(source):
            events.append((start, len(source), name, False, False))
            break

        end = cursor + 1
        self_closing = source[end - 2 : end] == "/>"
        events.append((start, end, name, closing, self_closing))
        index = end
    return events


def _mask_markdown_html(source):
    masked = list(source)
    events = _markdown_html_tag_events(source)
    void_elements = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
    stack = []

    for start, end, name, closing, self_closing in events:
        _mask_source_range(masked, start, end)
        if closing:
            for stack_index in range(len(stack) - 1, -1, -1):
                if stack[stack_index][0] == name:
                    open_start = stack[stack_index][1]
                    _mask_source_range(masked, open_start, end)
                    del stack[stack_index:]
                    break
        elif name and name not in void_elements:
            stack.append((name, start))

    for _, start in stack:
        _mask_source_range(masked, start, len(source))

    return "".join(masked)


def _is_escaped(text, index):
    backslashes = 0
    index -= 1
    while index >= 0 and text[index] == "\\":
        backslashes += 1
        index -= 1
    return backslashes % 2 == 1


def _mask_markdown_code_spans(source):
    masked = list(source)
    index = 0
    while index < len(source):
        if source[index] != "`" or _is_escaped(source, index):
            index += 1
            continue

        opener_start = index
        while index < len(source) and source[index] == "`":
            index += 1
        opener_length = index - opener_start
        cursor = index
        while cursor < len(source):
            if source[cursor] != "`":
                cursor += 1
                continue
            closer_start = cursor
            while cursor < len(source) and source[cursor] == "`":
                cursor += 1
            if cursor - closer_start == opener_length:
                _mask_source_range(masked, opener_start, cursor)
                index = cursor
                break
        else:
            index = opener_start + opener_length
    return "".join(masked)


def strip_markdown_code_and_comments(markdown):
    """Mask non-rendered Markdown/HTML contexts without changing source offsets.

    This supports the deliberately narrow publication contract: one top-level
    inline link with the exact label. It is not intended to implement CommonMark.
    """
    source = _mask_markdown_comments(markdown)
    source = _mask_markdown_code_blocks(source)
    source = _mask_markdown_reference_definitions(source)
    source = _mask_markdown_html(source)
    return _mask_markdown_code_spans(source)


def _markdown_delimiter_context(source, stop):
    bracket_depth = 0
    parenthesis_stack = []
    index = 0
    while index < stop:
        character = source[index]
        if character == "\\":
            index += 2
            continue
        if character == "[":
            bracket_depth += 1
        elif character == "]" and bracket_depth:
            bracket_depth -= 1
        elif character == "(":
            parenthesis_stack.append(index)
        elif character == ")" and parenthesis_stack:
            parenthesis_stack.pop()
        index += 1

    inside_link_destination = any(
        position > 0 and source[position - 1] == "]"
        for position in parenthesis_stack
    )
    return bracket_depth, inside_link_destination


def has_markdown_contact_link(markdown, email):
    source = strip_markdown_code_and_comments(markdown)
    escaped_email = re.escape(email)
    contact_link = re.compile(
        rf"\[{escaped_email}\]\([ \t]*"
        rf"(?:(?i:mailto):{escaped_email}|<(?i:mailto):{escaped_email}>)[ \t]*\)"
    )

    for match in contact_link.finditer(source):
        if _is_escaped(source, match.start()):
            continue
        if match.start() > 0 and source[match.start() - 1] == "!":
            if not _is_escaped(source, match.start() - 1):
                continue
        bracket_depth, inside_link_destination = _markdown_delimiter_context(
            source, match.start()
        )
        if bracket_depth == 0 and not inside_link_destination:
            return True
    return False


checks = []


def check(name, ok, detail=""):
    checks.append({"name": name, "ok": bool(ok), "detail": detail})


ROOT_ENGINE = (ROOT / "robot-navigation.js").read_text(encoding="utf-8").strip()

check(
    "Root RobotNav copy matches algorithm source",
    ROOT_ENGINE == JS,
    f"root={len(ROOT_ENGINE)} chars; algorithm={len(JS)} chars",
)

standalone_syntax = subprocess.run(
    ["node", "--check", "-"], input=JS, capture_output=True, text=True
)
check(
    "Standalone JavaScript syntax",
    standalone_syntax.returncode == 0,
    (standalone_syntax.stderr or standalone_syntax.stdout).strip(),
)

android_engine = ANDROID_ASSETS / "robot-navigation.js"
check(
    "Android RobotNav asset matches algorithm source",
    android_engine.is_file()
    and android_engine.read_text(encoding="utf-8").strip() == JS,
    f"asset exists={android_engine.is_file()}",
)

check("HTML document has one html root", len(re.findall(r"<html\b", HTML, re.I)) == 1)
check(
    "Android HTML asset matches index.html byte for byte",
    ANDROID_HTML.is_file() and ANDROID_HTML.read_bytes() == HTML_BYTES,
)
check(
    "RobotNav loads via standalone script tag",
    '<script src="robot-navigation.js"' in HTML
    and "RobotNav v2.9.5" in JS
    and "RobotNav v2.7.0" not in HTML,
)
check(
    "Standalone engine has no fetch/XHR/WebSocket",
    not re.search(r"\b(?:fetch\s*\(|XMLHttpRequest\b|WebSocket\b)", JS),
)
check(
    "Version chain is consistent (DATA, title, manifest, sw.js, package)",
    DATA_VERSION
    == MANIFEST_VERSION
    == SW_VERSION
    == PKG_VERSION
    and DATA_VERSION in HTML_TITLE,
    f"DATA={DATA_VERSION}; manifest={MANIFEST_VERSION}; sw={SW_VERSION}; tests={PKG_VERSION}; title={HTML_TITLE!r}",
)
check("No polling interval used", not re.search(r"\bsetInterval\s*\(", JS))
check(
    "No self-scheduling animation loop used",
    "requestAnimationFrame(flush)" in JS and "requestAnimationFrame(update)" not in JS,
)

for component in [
    "DOM Inventory",
    "Obstacle Cache",
    "Position Planner",
    "Motion Controller",
    "Event Scheduler",
]:
    check(
        f"Architecture component: {component}",
        component.lower() in ARCHITECTURE.lower(),
    )

for feature in [
    "dirtyFlags |= flags",
    "processing = true",
    "requestAnimationFrame(flush)",
    "mutationObserver.disconnect()",
    "resizeObserver.disconnect()",
    "position === 'sticky'",
    "RobotNav.destroy",
]:
    check(f"Engine feature: {feature}", feature in JS)


def same_file(relative):
    root_file = ROOT / relative
    android_file = ANDROID_ASSETS / relative
    return (
        root_file.is_file()
        and android_file.is_file()
        and root_file.read_bytes() == android_file.read_bytes()
    )


def webp_names(base):
    directory = base / "bg"
    found = {}
    for size in ("d", "m"):
        folder = directory / size
        found[size] = sorted(path.name for path in folder.glob("*.webp")) if folder.is_dir() else []
    return found


root_frames = webp_names(ROOT)
android_frames = webp_names(ANDROID_ASSETS)
frame_files = [
    Path("bg") / size / name
    for size, names in root_frames.items()
    for name in names
]
pwa_parity = all(same_file(name) for name in PWA_FILES) and all(
    same_file(path.as_posix()) for path in frame_files
)
check(
    "Root and Android PWA assets match byte for byte",
    pwa_parity and root_frames == android_frames and root_frames["d"] == root_frames["m"] and len(root_frames["d"]) == 29,
    f"frames={len(root_frames['d'])}",
)
check(
    "Root PWA shell files and .nojekyll exist",
    all((ROOT / name).is_file() for name in PWA_FILES) and (ROOT / ".nojekyll").is_file(),
)

try:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as error:
    manifest = {}
    manifest_error = str(error)
else:
    manifest_error = ""
icon_specs = {
    ("./icon-192.png", "192x192", "any"),
    ("./icon-512.png", "512x512", "any"),
    ("./icon-512-maskable.png", "512x512", "maskable"),
}
icon_found = {
    (item.get("src"), item.get("sizes"), item.get("purpose"))
    for item in manifest.get("icons", [])
    if isinstance(item, dict)
}
check(
    "PWA manifest uses relative scope and start_url",
    manifest.get("start_url") == "./"
    and manifest.get("scope") == "./"
    and manifest.get("display") == "standalone"
    and manifest.get("id") == "./"
    and not str(manifest.get("start_url", "")).startswith("/")
    and not str(manifest.get("scope", "")).startswith("/"),
    manifest_error,
)
check(
    "PWA manifest icons are relative and present",
    icon_specs <= icon_found
    and all((ROOT / src.removeprefix("./")).is_file() for src, _, _ in icon_specs),
)

sw_text = (ROOT / "sw.js").read_text(encoding="utf-8") if (ROOT / "sw.js").is_file() else ""
frame_match = re.search(r"var FRAMES = (\[[\s\S]*?\]);", sw_text)
try:
    sw_frames = json.loads(frame_match.group(1)) if frame_match else []
except json.JSONDecodeError:
    sw_frames = []
check(
    "Service worker cache version is current",
    "var VERSION = '2.9.5';" in sw_text
    and f"var BUILD = '{SERVICE_WORKER_BUILD}';" in sw_text
    and "anfoevo_v2_cache_" in sw_text
    and "robotnav-v2.8.0" not in sw_text,
)
check(
    "Service worker precaches relative core assets and both frame sets",
    all(token in sw_text for token in ("'./'", "'./index.html'", "'./manifest.json'", "'./bg/d/'", "'./bg/m/'"))
    and sw_frames == root_frames["d"] == root_frames["m"]
    and not re.search(r"""['"]/(?:index\.html|manifest\.json|sw\.js|icon-)""", sw_text),
    f"frames={len(sw_frames)}",
)

pwa_scripts = [
    block
    for block in re.findall(r"<script>([\s\S]*?)</script>", HTML)
    if "serviceWorker.register" in block
]
registration = pwa_scripts[0] if len(pwa_scripts) == 1 else ""
register_at = registration.find("serviceWorker.register")
check(
    "Service worker registration is limited to http(s) and skips android_asset",
    len(pwa_scripts) == 1
    and HTML.count("serviceWorker.register") == 1
    and "file:" in registration
    and "register('./sw.js')" in registration
    and 0 <= registration.find("http:") < register_at
    and 0 <= registration.find("https:") < register_at
    and 0 <= registration.find("android_asset") < register_at,
)
check(
    "index.html links manifest and icons with relative URLs",
    '<link rel="manifest" href="./manifest.json">' in HTML
    and '<link rel="icon" href="./icon-192.png"' in HTML
    and '<link rel="apple-touch-icon" href="./icon-192.png">' in HTML
    and 'href="/manifest.json"' not in HTML
    and 'href="data:,"' not in HTML,
)
impressum = re.search(r'id="imp-h"[\s\S]*?</section>', HTML)
impressum_text = impressum.group(0) if impressum else ""
required_provider_details = (PROVIDER_NAME, PROVIDER_ADDRESS, CONTACT_EMAIL)
html_has_provider_details = (
    "v2.9.5" in impressum_text
    and "v2.7.0" not in impressum_text
    and "§ 5 DDG" in impressum_text
    and all(detail in impressum_text for detail in required_provider_details)
    and has_html_contact_link(impressum_text, CONTACT_EMAIL)
    and PLACEHOLDER not in impressum_text
)
markdown_has_provider_details = (
    "§ 5 DDG" in IMPRESSUM_MD
    and all(detail in IMPRESSUM_MD for detail in required_provider_details)
    and has_markdown_contact_link(IMPRESSUM_MD, CONTACT_EMAIL)
    and PLACEHOLDER not in IMPRESSUM_MD
)
check(
    "Impressum contains the required DDG provider details",
    html_has_provider_details and markdown_has_provider_details,
)
prepare_script = ROOT / "scripts" / "prepare-pages-surface.sh"
prepare_text = prepare_script.read_text(encoding="utf-8") if prepare_script.is_file() else ""
check(
    "Pages prepare script copies a web-only surface and does not publish",
    "dist/pages" in prepare_text
    and "IMPRESSUM.md" in prepare_text
    and "android" in prepare_text
    and "tests" in prepare_text
    and "Gradle" in prepare_text
    and "does not enable GitHub Pages" in prepare_text
    and ".pages-surface" in prepare_text
    and "anfoevo-pages-surface" in prepare_text
    and prepare_text.find("Refusing to delete") != -1
    and prepare_text.find("Refusing to delete") < prepare_text.find("rm -rf"),
)


class _SubpathHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        prefix = "/AnFoVO-Lernkompendium"
        if path != prefix and not path.startswith(prefix + "/"):
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        relative = path[len(prefix):].lstrip("/")
        if relative == "":
            relative = "index.html"
        candidate = (ROOT / relative).resolve()
        root_resolved = ROOT.resolve()
        if candidate != root_resolved and root_resolved not in candidate.parents:
            self.send_error(403)
            return
        if candidate.is_dir():
            candidate = candidate / "index.html"
        if not candidate.is_file():
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        payload = candidate.read_bytes()
        content_type = {
            ".html": "text/html",
            ".js": "text/javascript",
            ".json": "application/json",
            ".png": "image/png",
            ".webp": "image/webp",
        }.get(candidate.suffix, "application/octet-stream")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def fetch(url):
    last_error = ""
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                return response.status, response.read(), response.headers.get_content_type()
        except urllib.error.HTTPError as error:
            return error.code, error.read(), ""
        except (OSError, urllib.error.URLError) as error:
            last_error = f"{url}: {error!r}"
            if attempt < 4:
                time.sleep(0.05)
    return 0, b"", last_error


def pages_subpath_detail():
    server = ThreadingHTTPServer(("127.0.0.1", 0), _SubpathHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.05)
    port = server.server_address[1]
    base = f"http://127.0.0.1:{port}/AnFoVO-Lernkompendium"
    try:
        page_status, page, page_type = fetch(base + "/")
        manifest_status, manifest_body, _ = fetch(base + "/manifest.json")
        worker_status, worker_body, _ = fetch(base + "/sw.js")
        icon_status, icon_body, icon_type = fetch(base + "/icon-192.png")
        frame_status, frame_body, frame_type = fetch(base + "/bg/d/r00.webp")
        mobile_status, _, _ = fetch(base + "/bg/m/z13.webp")
        marker_status, _, _ = fetch(base + "/.nojekyll")
        outside_status, _, _ = fetch(f"http://127.0.0.1:{port}/manifest.json")
        served_manifest = json.loads(manifest_body.decode("utf-8"))
        ok = (
            page_status == 200
            and page_type == "text/html"
            and b'href="./manifest.json"' in page
            and b"register('./sw.js')" in page
            and manifest_status == 200
            and served_manifest.get("start_url") == "./"
            and served_manifest.get("scope") == "./"
            and worker_status == 200
            and SERVICE_WORKER_BUILD.encode("utf-8") in worker_body
            and icon_status == 200
            and icon_type == "image/png"
            and icon_body.startswith(b"\x89PNG")
            and frame_status == 200
            and frame_type == "image/webp"
            and frame_body.startswith(b"RIFF")
            and mobile_status == 200
            and marker_status == 200
            and outside_status == 404
        )
        return ok, f"page={page_status}/{page_type} manifest={manifest_status} worker={worker_status} icon={icon_status}/{icon_type} frame={frame_status}/{frame_type} mobile={mobile_status} nojekyll={marker_status} outside={outside_status}"
    except (OSError, json.JSONDecodeError, urllib.error.URLError) as error:
        return False, str(error)
    finally:
        server.shutdown()
        server.server_close()


subpath_ok, subpath_detail = pages_subpath_detail()
check(
    "Pages subpath serves manifest, worker, icon, and background frames",
    subpath_ok,
    subpath_detail,
)

failed = [item for item in checks if not item["ok"]]
passed = len(checks) - len(failed)
report = {
    "version": "2.9.5",
    "static_checks": len(checks),
    "passed": passed,
    "failed": len(failed),
    "checks": checks,
}

import argparse

parser = argparse.ArgumentParser(description="Static build verification for the Lernkompendium PWA.")
parser.add_argument(
    "--out",
    default=None,
    help="Verzeichnis fuer die Testberichte (Default: build/verify/ - gitignoriert, kein Tree-Drift). "
    "Fuer ein Release bewusst ein Release-Verzeichnis waehen und die Berichte committen.",
)
args = parser.parse_args()
OUT_DIR = Path(args.out) if args.out else ROOT / "build" / "verify"
OUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_JSON = OUT_DIR / "TESTBERICHT_v2.9.5.json"
REPORT_TXT = OUT_DIR / "TESTBERICHT_v2.9.5.txt"

REPORT_JSON.write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
REPORT_TXT.write_text(
    "\n".join(
        ("PASS" if item["ok"] else "FAIL")
        + " "
        + item["name"]
        + ((" — " + item["detail"]) if item["detail"] else "")
        for item in checks
    )
    + f"\n\nStatische Prüfungen: {passed} bestanden, {len(failed)} fehlgeschlagen.\n",
    encoding="utf-8",
)

print(
    json.dumps(
        {"passed": passed, "failed": len(failed), "failed_checks": failed},
        ensure_ascii=False,
        indent=2,
    )
)
sys.exit(1 if failed else 0)
