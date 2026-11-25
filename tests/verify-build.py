from pathlib import Path
from html import unescape
from html.entities import html5
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

def css_opacity_is_zero(value):
    value = value.strip().lower()
    if value.endswith("!important"):
        value = value[: -len("!important")].strip()
    if value.endswith("%"):
        value = value[:-1].strip()
    try:
        return float(value) == 0.0
    except ValueError:
        return False


def style_hides_content(style):
    style = re.sub(r"/\*.*?\*/", "", style or "", flags=re.S)
    normalized = re.sub(r"\s+", "", style).lower()
    if re.search(
        r"(?:^|;)(?:display:none|visibility:(?:hidden|collapse)|"
        r"content-visibility:hidden)(?:!important|;|$)",
        normalized,
    ):
        return True
    opacity = re.search(r"(?:^|;)opacity:([^;]*)", normalized)
    return bool(opacity and css_opacity_is_zero(opacity.group(1)))


class _ContactAnchorParser(HTMLParser):
    NON_RENDERED_TAGS = {
        "canvas",
        "datalist",
        "head",
        "iframe",
        "listing",
        "math",
        "noembed",
        "noframes",
        "noscript",
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
    CONDITIONAL_VISIBILITY_TAGS = {"details", "dialog"}
    VOID_TAGS = {
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

    def __init__(self, email):
        super().__init__(convert_charrefs=True)
        self.email = email
        self.found = False
        self._anchor = None
        self._nonrendered_tags = []
        self._hidden_tags = []

    @staticmethod
    def _attribute(attrs, name):
        return next(
            (value for attribute, value in attrs if attribute.lower() == name),
            None,
        )

    @staticmethod
    def _has_attribute(attrs, name):
        return any(attribute.lower() == name for attribute, _ in attrs)

    @classmethod
    def _hides_content(cls, attrs):
        if any(attribute.lower() == "hidden" for attribute, _ in attrs):
            return True
        style = cls._attribute(attrs, "style") or ""
        return style_hides_content(style)

    @staticmethod
    def _pop_context(context, tag):
        for index in range(len(context) - 1, -1, -1):
            if context[index] == tag:
                del context[index]
                return

    def _finish_anchor(self):
        if not self._anchor:
            return
        visible_text = " ".join("".join(self._anchor["text"]).split())
        if (
            self._anchor["renderable"]
            and self._anchor["href"] == f"mailto:{self.email}"
            and visible_text == self.email
        ):
            self.found = True
        self._anchor = None

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "a":
            # Browsers implicitly close an active anchor when another starts.
            self._finish_anchor()

        hidden = self._hides_content(attrs)
        if tag in self.CONDITIONAL_VISIBILITY_TAGS and not self._has_attribute(
            attrs, "open"
        ):
            hidden = True
        if self._has_attribute(attrs, "popover"):
            hidden = True
        renderable = not (
            self._nonrendered_tags or self._hidden_tags or hidden
        )
        if tag in self.NON_RENDERED_TAGS:
            self._nonrendered_tags.append(tag)
        if hidden and tag not in self.VOID_TAGS:
            self._hidden_tags.append(tag)
        if tag == "a" and renderable:
            self._anchor = {
                "href": self._attribute(attrs, "href"),
                "text": [],
                "renderable": True,
            }

    def handle_startendtag(self, tag, attrs):
        # HTML ignores the self-closing slash on non-void elements. Keeping the
        # element open also keeps script/style/template contents inert.
        self.handle_starttag(tag, attrs)

    def handle_data(self, data):
        if self._nonrendered_tags or self._hidden_tags:
            return
        if self._anchor:
            self._anchor["text"].append(data)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "a":
            self._finish_anchor()
        self._pop_context(self._nonrendered_tags, tag)
        self._pop_context(self._hidden_tags, tag)

    def close(self):
        super().close()
        self._finish_anchor()


def has_html_contact_link(fragment, email):
    parser = _ContactAnchorParser(email)
    try:
        parser.feed(fragment)
        parser.close()
    except (AssertionError, ValueError):
        return False
    return parser.found


def markdown_code_span_ranges(source):
    ranges = []
    index = 0
    while index < len(source):
        if source[index] != "`":
            index += 1
            continue

        backslashes = 0
        cursor = index - 1
        while cursor >= 0 and source[cursor] == "\\":
            backslashes += 1
            cursor -= 1
        if backslashes % 2:
            # An odd backslash run escapes this backtick.
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


def mask_html_comments(source, replacement=" "):
    masked = list(source)
    index = 0
    while index < len(source):
        start = source.find("<!--", index)
        if start < 0:
            break
        close = source.find("-->", start + 4)
        end = len(source) if close < 0 else close + 3
        for position in range(start, end):
            if masked[position] not in "\r\n":
                masked[position] = replacement
        index = end
    return "".join(masked)


def markdown_closing_bracket(source, start):
    depth = 0
    index = start
    while index < len(source):
        character = source[index]
        if character == "\\" and index + 1 < len(source):
            index += 2
            continue
        if character == "[":
            depth += 1
        elif character == "]":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return None


def markdown_closing_parenthesis(source, start):
    depth = 0
    quote = None
    angle = False
    index = start
    while index < len(source):
        character = source[index]
        if character == "\\" and index + 1 < len(source):
            index += 2
            continue
        if quote:
            if character == quote:
                quote = None
        elif character in "\"'":
            quote = character
        elif character == "<" and depth == 0:
            angle = True
        elif character == ">" and angle:
            angle = False
        elif not angle:
            if character == "(":
                depth += 1
            elif character == ")":
                depth -= 1
                if depth == 0:
                    return index + 1
        index += 1
    return None


def markdown_unclosed_comment_start(source, ignored_ranges=()):
    index = 0
    while True:
        start = source.find("<!--", index)
        while start >= 0 and any(
            range_start <= start < range_end
            for range_start, range_end, _ in ignored_ranges
        ):
            start = source.find("<!--", start + 4)
        if start < 0:
            return None
        close = source.find("-->", start + 4)
        while close >= 0 and any(
            range_start <= close < range_end
            for range_start, range_end, _ in ignored_ranges
        ):
            close = source.find("-->", close + 3)
        if close < 0:
            return start
        index = close + 3


def mask_markdown_line(source):
    return "".join(
        character if character in "\r\n" else " " for character in source
    )


def markdown_has_comment_outside_code(source, code_ranges):
    for match in re.finditer(r"<!--", source):
        position = match.start()
        if not any(start <= position < end for start, end, _ in code_ranges):
            return True
    return False


def markdown_is_escaped(source, index):
    backslashes = 0
    cursor = index - 1
    while cursor >= 0 and source[cursor] == "\\":
        backslashes += 1
        cursor -= 1
    return backslashes % 2 == 1


def markdown_title_end(source, start):
    opener = source[start]
    closer = opener if opener in "\"'" else ")"
    cursor = start + 1
    while cursor < len(source):
        character = source[cursor]
        if character == "\\" and cursor + 1 < len(source):
            cursor += 2
            continue
        if character == closer:
            return cursor
        if opener == "(" and character == "(":
            return None
        cursor += 1
    return None


def parse_markdown_inline_link(source, closing_bracket):
    if closing_bracket + 1 >= len(source) or source[closing_bracket + 1] != "(":
        return None

    cursor = closing_bracket + 2
    while cursor < len(source) and source[cursor] in " \t\r\n":
        cursor += 1
    if cursor >= len(source):
        return None

    if source[cursor] == "<":
        destination_start = cursor + 1
        cursor = source.find(">", destination_start)
        if cursor < 0 or "\n" in source[destination_start:cursor]:
            return None
        destination = source[destination_start:cursor]
        cursor += 1
    else:
        destination_start = cursor
        while cursor < len(source) and source[cursor] not in " \t\r\n)":
            cursor += 1
        if cursor == destination_start:
            return None
        destination = source[destination_start:cursor]

    after_destination = cursor
    while cursor < len(source) and source[cursor] in " \t\r\n":
        cursor += 1
    had_whitespace = cursor > after_destination

    if cursor < len(source) and source[cursor] in "\"'(":
        if not had_whitespace:
            return None
        title_end = markdown_title_end(source, cursor)
        if title_end is None:
            return None
        cursor = title_end + 1
        while cursor < len(source) and source[cursor] in " \t\r\n":
            cursor += 1

    if cursor >= len(source) or source[cursor] != ")":
        return None
    return {
        "destination": destination,
        "end": cursor + 1,
    }


def markdown_label_contains_inline_link(source, start, end):
    index = start + 1
    while index < end:
        if source[index] != "[" or markdown_is_escaped(source, index):
            index += 1
            continue
        closing_bracket = markdown_closing_bracket(source, index)
        if closing_bracket is None or closing_bracket >= end:
            index += 1
            continue
        if parse_markdown_inline_link(source, closing_bracket) is not None:
            return True
        index = closing_bracket + 1
    return False


def markdown_inline_links(source):
    links = []
    index = 0
    while index < len(source):
        if source[index] != "[" or markdown_is_escaped(source, index):
            index += 1
            continue
        closing_bracket = markdown_closing_bracket(source, index)
        if closing_bracket is None:
            index += 1
            continue
        if markdown_label_contains_inline_link(source, index, closing_bracket):
            # GitHub renders a link nested in another link label as its own
            # anchor rather than as part of the outer link.
            index += 1
            continue
        link = parse_markdown_inline_link(source, closing_bracket)
        if link is None:
            index += 1
            continue
        links.append(
            {
                "label_start": index + 1,
                "label_end": closing_bracket,
                "destination": link["destination"],
            }
        )
        # Skip the complete construct so text in another link's label,
        # destination, or title cannot be mistaken for a separate anchor.
        index = link["end"]
    return links


def mask_markdown_image_descriptions(source):
    masked = list(source)
    index = 0
    while index < len(source) - 1:
        if source[index] != "!" or source[index + 1] != "[":
            index += 1
            continue
        backslashes = 0
        cursor = index - 1
        while cursor >= 0 and source[cursor] == "\\":
            backslashes += 1
            cursor -= 1
        if backslashes % 2:
            index += 1
            continue
        end = markdown_closing_bracket(source, index + 1)
        if end is None:
            end = len(source)
        else:
            end += 1
            destination = end
            while destination < len(source) and source[destination] in " \t":
                destination += 1
            if destination < len(source) and source[destination] == "(":
                close = markdown_closing_parenthesis(source, destination)
                end = len(source) if close is None else close
        for position in range(index + 1, end):
            if masked[position] not in "\r\n":
                masked[position] = " "
        index = end
    return "".join(masked)


def mask_html_tags(source):
    masked = list(source)
    index = 0
    while index < len(source):
        if source[index] != "<":
            index += 1
            continue
        name_start = index + 1
        if name_start < len(source) and source[name_start] == "/":
            name_start += 1
        name_end = name_start
        while name_end < len(source) and (
            source[name_end].isalnum() or source[name_end] == "-"
        ):
            name_end += 1
        if (
            name_end == name_start
            or name_end >= len(source)
            or source[name_end] not in " \t\r\n/>"
        ):
            index += 1
            continue
        quote = None
        cursor = name_end
        while cursor < len(source):
            character = source[cursor]
            if quote:
                if character == quote:
                    quote = None
            elif character in "\"'":
                quote = character
            elif character == ">":
                for position in range(index, cursor + 1):
                    if masked[position] not in "\r\n":
                        masked[position] = " "
                index = cursor + 1
                break
            cursor += 1
        else:
            index += 1
    return "".join(masked)


def render_markdown_code_span(content):
    rendered = re.sub(r"\r\n|\r|\n", " ", content)
    if rendered.startswith(" ") and rendered.endswith(" ") and rendered.strip(" "):
        rendered = rendered[1:-1]
    return rendered


def parse_markdown_container(line):
    expanded = line.expandtabs(4)
    position = 0
    blockquote_depth = 0
    list_markers = []
    list_indent = 0
    list_base = 0
    while position < len(expanded):
        blockquote = re.match(r"[ ]{0,3}>[ ]?", expanded[position:])
        if blockquote:
            position += blockquote.end()
            blockquote_depth += 1
            list_base = position
            list_markers = []
            list_indent = 0
            continue
        list_item = re.match(
            r"[ ]{0,3}([-+*]|\d{1,9}[.)])([ ]+)",
            expanded[position:],
        )
        if list_item:
            marker = list_item.group(1)
            spaces = list_item.group(2)
            consumed_spaces = len(spaces) if len(spaces) <= 4 else 1
            position += len(marker) + consumed_spaces
            list_markers.append(marker)
            list_indent = position - list_base
            continue
        break
    return {
        "blockquote_depth": blockquote_depth,
        "list_markers": list_markers,
        "list_indent": list_indent,
        "content": expanded[position:],
    }


def mask_markdown_definition_blocks(source):
    footnote_definition = re.compile(
        r"^[ ]{0,3}\[\^(?:\\.|[^\]\\])+\]:"
    )
    reference_definition = re.compile(
        r"^[ ]{0,3}\[(?!\^)(?:\\.|[^\]\\])+\]:"
    )
    lines = []
    in_definition = False

    for line in source.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        ending = line[len(body) :]
        parsed = parse_markdown_container(body)
        content = parsed["content"]

        if in_definition:
            if not content.strip():
                in_definition = False
                lines.append(line)
            else:
                lines.append(" " * len(body) + ending)
            continue

        if footnote_definition.match(content) or reference_definition.match(content):
            lines.append(" " * len(body) + ending)
            in_definition = True
            continue

        lines.append(line)

    return "".join(lines)


def markdown_fence_candidate(line, expected=None):
    parsed = parse_markdown_container(line)
    content = parsed["content"]
    if expected:
        if parsed["blockquote_depth"] != expected["blockquote_depth"]:
            return None
        if expected["list_markers"]:
            if parsed["list_markers"]:
                # Repeating a list marker starts another item; it does not close
                # a fence opened in the previous item.
                return None
            leading = len(content) - len(content.lstrip(" "))
            if leading < expected["list_indent"]:
                return None
            content = content[expected["list_indent"] :]
        elif parsed["list_markers"]:
            return None
    marker = re.match(r"^[ ]{0,3}(`{3,}|~{3,})(.*)$", content)
    if not marker:
        return None
    return parsed, marker.group(1), marker.group(2)


def html_tag_end(source, start=0):
    if start >= len(source) or source[start] != "<":
        return None
    name_start = start + 1
    if name_start < len(source) and source[name_start] == "/":
        name_start += 1
    name_end = name_start
    while name_end < len(source) and (
        source[name_end].isalnum() or source[name_end] == "-"
    ):
        name_end += 1
    if (
        name_end == name_start
        or name_end >= len(source)
        or source[name_end] not in " \t\r\n/>"
    ):
        return None
    quote = None
    cursor = name_end
    while cursor < len(source):
        character = source[cursor]
        if quote:
            if character == quote:
                quote = None
        elif character in "\"'":
            quote = character
        elif character == ">":
            return cursor + 1
        cursor += 1
    return None


def html_tag_only(source):
    end = html_tag_end(source)
    return end is not None and not source[end:].strip()


def markdown_has_hidden_html_context(source):
    nonrendered = {
        "canvas",
        "datalist",
        "iframe",
        "listing",
        "noembed",
        "noframes",
        "noscript",
        "optgroup",
        "option",
        "plaintext",
        "script",
        "select",
        "style",
        "template",
        "textarea",
        "title",
        "xmp",
    }
    index = 0
    while index < len(source):
        start = source.find("<", index)
        if start < 0:
            break
        end = html_tag_end(source, start)
        if end is None:
            index = start + 1
            continue
        tag = source[start:end]
        name_match = re.match(r"<\s*/?\s*([A-Za-z][A-Za-z0-9-]*)", tag)
        if name_match:
            name = name_match.group(1).lower()
            if not tag.lstrip().startswith("</") and name in nonrendered:
                return True
            if name in {"details", "dialog"} and not re.search(
                r"(?:^|\s)open(?:\s|=|/?>)", tag, flags=re.IGNORECASE
            ):
                return True
            if re.search(
                r"(?:^|\s)popover(?=\s|=|/?>)", tag, flags=re.IGNORECASE
            ):
                return True
            if re.search(
                r"(?:^|\s)hidden(?=\s|=|/?>)", tag, flags=re.IGNORECASE
            ):
                return True
            style = re.search(
                r"(?:^|\s)style\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))",
                tag,
                flags=re.IGNORECASE,
            )
            if style:
                value = next(
                    (group for group in style.groups() if group is not None),
                    "",
                )
                if style_hides_content(value):
                    return True
        index = end
    return False


def strip_markdown_code_and_comments(markdown):
    raw_text_tags = {"script", "pre", "style", "textarea", "xmp"}
    raw_block_tags = {
        "address",
        "article",
        "aside",
        "base",
        "basefont",
        "blockquote",
        "body",
        "caption",
        "center",
        "code",
        "col",
        "colgroup",
        "dd",
        "details",
        "dialog",
        "dir",
        "div",
        "dl",
        "dt",
        "fieldset",
        "figcaption",
        "figure",
        "footer",
        "form",
        "frame",
        "frameset",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "head",
        "header",
        "hr",
        "html",
        "iframe",
        "legend",
        "li",
        "link",
        "main",
        "menu",
        "menuitem",
        "nav",
        "noframes",
        "noscript",
        "ol",
        "optgroup",
        "option",
        "p",
        "param",
        "search",
        "section",
        "summary",
        "table",
        "tbody",
        "td",
        "template",
        "tfoot",
        "th",
        "thead",
        "title",
        "tr",
        "track",
        "ul",
    }
    raw_block_pattern = re.compile(
        rf"^</?(?:{'|'.join(sorted(raw_block_tags))})(?=[ \t/>])",
        re.IGNORECASE,
    )

    lines = []
    fence = None
    raw_text_tag = None
    raw_block_until_blank = False
    comment_until_close = False
    previous_blank = True
    indented_code = False

    for line in markdown.splitlines():
        if raw_text_tag:
            if re.search(
                rf"</{raw_text_tag}[ \t]*>", line, flags=re.IGNORECASE
            ):
                raw_text_tag = None
                previous_blank = True
            continue
        if raw_block_until_blank:
            if not line.strip():
                raw_block_until_blank = False
                previous_blank = True
            continue
        if comment_until_close:
            close = line.find("-->")
            if close < 0:
                lines.append(mask_markdown_line(line))
                previous_blank = True
                continue
            end = close + 3
            line = mask_markdown_line(line[:end]) + line[end:]
            comment_until_close = False
            previous_blank = True
        if fence:
            fence_parsed = parse_markdown_container(line)
            if fence_parsed["blockquote_depth"] < fence["blockquote_depth"]:
                # A quoted fenced block ends when its containing quote ends.
                fence = None
            else:
                candidate = markdown_fence_candidate(line, fence)
                if candidate:
                    _, marker, suffix = candidate
                    if (
                        marker[0] == fence["marker"]
                        and len(marker) >= fence["length"]
                        and not suffix.strip(" \t")
                    ):
                        fence = None
                        previous_blank = True
                continue

        parsed = parse_markdown_container(line)
        content = parsed["content"]
        if "<!--" in content:
            code_ranges = markdown_code_span_ranges(content)
            if markdown_has_comment_outside_code(content, code_ranges):
                if (
                    markdown_unclosed_comment_start(content, code_ranges)
                    is not None
                ):
                    comment_until_close = True
                    opener = line.find("<!--")
                    if opener >= 0:
                        line = line[:opener] + mask_markdown_line(line[opener:])
                    else:
                        line = mask_markdown_line(line)
                    lines.append(line)
                    previous_blank = True
                    continue
                line = mask_html_comments(line, "\ue102")
                parsed = parse_markdown_container(line)
                content = parsed["content"]

        blank = not content.replace("\ue102", "").strip()
        leading = len(content) - len(content.lstrip(" "))
        if blank:
            if indented_code:
                previous_blank = True
                continue
            lines.append("")
            previous_blank = True
            continue
        if indented_code:
            if leading >= 4:
                continue
            indented_code = False
        elif leading >= 4 and (previous_blank or not lines):
            indented_code = True
            continue

        candidate = markdown_fence_candidate(line)
        if candidate:
            parsed, marker, suffix = candidate
            if marker[0] != "`" or "`" not in suffix:
                fence = {
                    "marker": marker[0],
                    "length": len(marker),
                    "blockquote_depth": parsed["blockquote_depth"],
                    "list_markers": parsed["list_markers"],
                    "list_indent": parsed["list_indent"],
                }
                previous_blank = True
                continue

        stripped = content.lstrip(" ")
        indent = len(content) - len(stripped)
        if indent <= 3:
            raw_text = re.match(
                r"^<(script|pre|style|textarea|xmp)(?=[ \t/>])",
                stripped,
                flags=re.IGNORECASE,
            )
            if raw_text:
                tag = raw_text.group(1).lower()
                if not re.search(
                    rf"</{tag}[ \t]*>", stripped, flags=re.IGNORECASE
                ):
                    raw_text_tag = tag
                previous_blank = True
                continue
            if (
                raw_block_pattern.match(stripped)
                or re.match(r"^<[!?]", stripped)
                or html_tag_only(stripped)
            ):
                raw_block_until_blank = True
                previous_blank = True
                continue

        lines.append(line)
        previous_blank = False

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

    return re.sub(
        r"\\([\\`*{}\[\]()#+\-.!_<>~|])",
        replace_escape,
        label,
    ), escaped


def strip_balanced_markdown_emphasis(label):
    # Only whole-label wrappers are accepted. This avoids treating unmatched or
    # intraword punctuation as formatting while keeping the documented subset
    # deterministic.
    wrappers = (
        ("***", "***"),
        ("___", "___"),
        ("**", "**"),
        ("__", "__"),
        ("~~", "~~"),
        ("~", "~"),
        ("*", "*"),
        ("_", "_"),
    )
    for opening, closing in wrappers:
        if (
            len(label) >= len(opening) + len(closing)
            and label.startswith(opening)
            and label.endswith(closing)
        ):
            return label[len(opening) : -len(closing)]
    return label


def commonmark_unescape(text):
    entity = re.compile(
        r"&(?:#[xX]([0-9A-Fa-f]{1,8})|#([0-9]{1,8})|"
        r"([A-Za-z][A-Za-z0-9]+));"
    )

    def replace(match):
        if match.group(3) is not None:
            return html5.get(match.group(0)[1:], match.group(0))
        return unescape(match.group(0))

    return entity.sub(replace, text)


def plain_markdown_label(label):
    label, rendered_spans = protect_markdown_code_spans(label)
    label = label.replace("\ue102", "")
    label, escaped = protect_markdown_escapes(label)
    if re.search(r"</?[A-Za-z][^<>]*>", label):
        return None
    label = strip_balanced_markdown_emphasis(label)
    for token, character in escaped.items():
        label = label.replace(token, character)
    label = commonmark_unescape(label)
    for token, rendered in rendered_spans.items():
        label = label.replace(token, rendered)
    return " ".join(label.split())


def has_markdown_contact_link(markdown, email):
    source = mask_markdown_definition_blocks(
        strip_markdown_code_and_comments(markdown)
    )
    if markdown_has_hidden_html_context(source):
        return False
    masked = mask_markdown_code_spans(
        source, markdown_code_span_ranges(source)
    )
    masked = mask_markdown_image_descriptions(masked)
    masked = mask_html_tags(masked)
    links = markdown_inline_links(masked)
    expected_destination = f"mailto:{email}"
    for link in links:
        label = source[link["label_start"] : link["label_end"]]
        if (
            link["destination"] == expected_destination
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
