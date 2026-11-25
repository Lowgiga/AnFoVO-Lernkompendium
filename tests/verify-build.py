from pathlib import Path
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
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

class _ContactAnchorParser(HTMLParser):
    def __init__(self, email):
        super().__init__(convert_charrefs=True)
        self.email = email
        self.found = False
        self._anchors = []
        self._script_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "script":
            self._script_depth += 1
        if tag == "a":
            self._anchors.append({"href": dict(attrs).get("href"), "text": []})

    def handle_data(self, data):
        if self._script_depth:
            return
        for anchor in self._anchors:
            anchor["text"].append(data)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "script" and self._script_depth:
            self._script_depth -= 1
        if tag == "a" and self._anchors:
            anchor = self._anchors.pop()
            visible_text = " ".join("".join(anchor["text"]).split())
            if (
                anchor["href"] == f"mailto:{self.email}"
                and visible_text == self.email
            ):
                self.found = True


def has_html_contact_link(fragment, email):
    parser = _ContactAnchorParser(email)
    parser.feed(fragment)
    parser.close()
    return parser.found


def markdown_code_span_ranges(source):
    ranges = []
    index = 0
    while index < len(source):
        if source[index] != "`":
            index += 1
            continue
        opener_start = index
        while index < len(source) and source[index] == "`":
            index += 1
        opener_end = index
        opener_length = opener_end - opener_start
        cursor = opener_end
        while cursor < len(source):
            if source[cursor] != "`":
                cursor += 1
                continue
            closer_start = cursor
            while cursor < len(source) and source[cursor] == "`":
                cursor += 1
            closer_length = cursor - closer_start
            if closer_length == opener_length:
                ranges.append(
                    (opener_start, cursor, source[opener_end:closer_start])
                )
                index = cursor
                break
        else:
            index = opener_end
    return ranges


def mask_markdown_code_spans(source, ranges):
    masked = list(source)
    for start, end, _ in ranges:
        for index in range(start, end):
            if masked[index] not in "\r\n":
                masked[index] = " "
    return "".join(masked)


def render_markdown_code_span(content):
    rendered = re.sub(r"\r\n|\r|\n", " ", content)
    if rendered.startswith(" ") and rendered.endswith(" ") and rendered.strip(" "):
        rendered = rendered[1:-1]
    return rendered


def strip_markdown_code_and_comments(markdown):
    text = re.sub(r"<!--[\s\S]*?-->", "", markdown)
    text = re.sub(
        r"<(pre|code)\b[^>]*>[\s\S]*?</\1\s*>",
        "",
        text,
        flags=re.IGNORECASE,
    )

    lines = []
    fence = None
    previous_blank = True
    indented_code = False
    for line in text.splitlines():
        marker_match = re.match(r"^[ \t]{0,3}(`{3,}|~{3,})(.*)$", line)
        marker = marker_match.group(1) if marker_match else None
        if fence:
            if marker:
                suffix = marker_match.group(2)
                if (
                    marker[0] == fence[0]
                    and len(marker) >= fence[1]
                    and not suffix.strip(" \t")
                ):
                    fence = None
                    previous_blank = True
            continue
        if marker:
            fence = (marker[0], len(marker))
            previous_blank = True
            continue

        expanded = line.expandtabs(4)
        indent = len(expanded) - len(expanded.lstrip(" "))
        blank = not line.strip()
        if indented_code:
            if blank:
                continue
            if indent >= 4:
                continue
            indented_code = False
        elif indent >= 4 and (previous_blank or not lines):
            indented_code = True
            continue
        lines.append(line)
        previous_blank = blank
    return "\n".join(lines)


def protect_markdown_code_spans(label):
    ranges = markdown_code_span_ranges(label)
    if not ranges:
        return label, {}
    parts = []
    rendered_spans = {}
    cursor = 0
    for index, (start, end, content) in enumerate(ranges):
        parts.append(label[cursor:start])
        token = f"\ue000{index}\ue001"
        rendered_spans[token] = render_markdown_code_span(content)
        parts.append(token)
        cursor = end
    parts.append(label[cursor:])
    return "".join(parts), rendered_spans


def protect_markdown_escapes(label):
    escaped = {}

    def replace_escape(match):
        token = f"\ue100{len(escaped)}\ue101"
        escaped[token] = match.group(1)
        return token

    return re.sub(r"\\([\\`*{}\[\]()#+\-.!_>~|])", replace_escape, label), escaped


def strip_balanced_markdown_emphasis(label):
    for marker in ("***", "___", "~~~", "**", "__", "~~", "*", "_"):
        escaped_marker = re.escape(marker)
        delimiter = re.escape(marker[0])
        pattern = re.compile(
            rf"(?<!{delimiter}){escaped_marker}"
            rf"(?P<body>\S(?:.*?\S)?)"
            rf"{escaped_marker}(?!{delimiter})",
            flags=re.S,
        )
        label = pattern.sub(lambda match: match.group("body"), label)
    return label


def plain_markdown_label(label):
    label, rendered_spans = protect_markdown_code_spans(label)
    label, escaped = protect_markdown_escapes(label)
    label = re.sub(r"</?[A-Za-z][^<>]*>", "", label)
    label = strip_balanced_markdown_emphasis(label)
    for token, character in escaped.items():
        label = label.replace(token, character)
    for token, rendered in rendered_spans.items():
        label = label.replace(token, rendered)
    return " ".join(label.split())


def has_markdown_contact_link(markdown, email):
    source = strip_markdown_code_and_comments(markdown)
    masked = mask_markdown_code_spans(
        source, markdown_code_span_ranges(source)
    )
    links = re.finditer(
        r"(?<![\\!])\[(?P<label>[^\]\n]+)\]\(\s*"
        r"(?P<destination><[^>\n]+>|[^)\s]+)"
        r"(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^()]*\)))?\s*\)",
        masked,
    )
    expected_destination = f"mailto:{email}"
    for link in links:
        destination = link.group("destination")
        if destination.startswith("<") and destination.endswith(">"):
            destination = destination[1:-1]
        label = source[link.start("label") : link.end("label")]
        if (
            destination.casefold() == expected_destination.casefold()
            and plain_markdown_label(label) == email
        ):
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
