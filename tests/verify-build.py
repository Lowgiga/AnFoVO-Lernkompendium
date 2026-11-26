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

CSS_WIDE_KEYWORDS = {"inherit", "initial", "revert", "revert-layer", "unset"}


def css_opacity_number(value):
    value = value.strip().lower()
    value = re.sub(r"!\s*important\s*$", "", value).strip()
    if value.startswith("calc(") and value.endswith(")"):
        expression = value[5:-1].replace(" ", "")
        if re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:%)?", expression):
            number = expression[:-1] if expression.endswith("%") else expression
            try:
                return float(number)
            except ValueError:
                return None
        match = re.fullmatch(
            r"([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:%)?)"
            r"([*/])([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:%)?)",
            expression,
        )
        if match:
            left = float(match.group(1).rstrip("%"))
            right = float(match.group(3).rstrip("%"))
            if match.group(2) == "*":
                return left * right
            if right == 0:
                return None
            return left / right
        return None
    if value.endswith("%"):
        value = value[:-1].strip()
    try:
        return float(value)
    except ValueError:
        return None


def css_opacity_is_zero(value):
    number = css_opacity_number(value)
    return number is not None and number == 0.0


def css_color_is_transparent(value):
    value = re.sub(
        r"!\s*important\s*$", "", (value or "").strip(), flags=re.IGNORECASE
    ).strip().lower()
    if value == "transparent":
        return True

    hexadecimal = re.fullmatch(r"#([0-9a-f]{3,8})", value)
    if hexadecimal:
        digits = hexadecimal.group(1)
        if len(digits) == 4:
            return digits[-1] == "0"
        if len(digits) == 8:
            return digits[-2:] == "00"
        return False

    functional = re.fullmatch(r"(?:rgba?|hsla?)\((.*)\)", value, re.DOTALL)
    if not functional:
        return False
    components = functional.group(1).strip()
    if "/" in components:
        alpha = components.rsplit("/", 1)[1].strip()
    elif components.count(",") == 3:
        alpha = components.rsplit(",", 1)[1].strip()
    else:
        return False
    alpha = alpha.removesuffix("%").strip()
    try:
        return float(alpha) == 0.0
    except ValueError:
        return False


CSS_NAMED_COLORS = set(
    """
    aliceblue antiquewhite aqua aquamarine azure beige bisque black
    blanchedalmond blue blueviolet brown burlywood cadetblue chartreuse
    chocolate coral cornflowerblue cornsilk crimson cyan darkblue darkcyan
    darkgoldenrod darkgray darkgreen darkgrey darkkhaki darkmagenta
    darkolivegreen darkorange darkorchid darkred darksalmon darkseagreen
    darkslateblue darkslategray darkslategrey darkturquoise darkviolet
    deeppink deepskyblue dimgray dimgrey dodgerblue firebrick floralwhite
    forestgreen fuchsia gainsboro ghostwhite gold goldenrod gray green
    greenyellow grey honeydew hotpink indianred indigo ivory khaki lavender
    lavenderblush lawngreen lemonchiffon lightblue lightcoral lightcyan
    lightgoldenrodyellow lightgray lightgreen lightgrey lightpink lightsalmon
    lightseagreen lightskyblue lightslategray lightslategrey lightsteelblue
    lightyellow lime limegreen linen magenta maroon mediumaquamarine
    mediumblue mediumorchid mediumpurple mediumseagreen mediumslateblue
    mediumspringgreen mediumturquoise mediumvioletred midnightblue mintcream
    mistyrose moccasin navajowhite navy oldlace olive olivedrab orange
    orangered orchid palegoldenrod palegreen paleturquoise palevioletred
    papayawhip peachpuff peru pink plum powderblue purple rebeccapurple red
    rosybrown royalblue saddlebrown salmon sandybrown seagreen seashell sienna
    silver skyblue slateblue slategray slategrey snow springgreen steelblue tan
    teal thistle tomato turquoise violet wheat white whitesmoke yellow
    yellowgreen
    """.split()
)
CSS_COLOR_FUNCTIONS = {
    "color",
    "color-mix",
    "env",
    "hsl",
    "hsla",
    "hwb",
    "lab",
    "lch",
    "light-dark",
    "oklab",
    "oklch",
    "rgb",
    "rgba",
    "var",
}
CSS_DISPLAY_KEYWORDS = {
    "block",
    "contents",
    "flow",
    "flow-root",
    "flex",
    "grid",
    "inline",
    "inline-block",
    "inline-flex",
    "inline-grid",
    "inline-list-item",
    "inline-table",
    "list-item",
    "none",
    "ruby",
    "ruby-base",
    "ruby-base-container",
    "ruby-text",
    "ruby-text-container",
    "run-in",
    "table",
    "table-caption",
    "table-cell",
    "table-column",
    "table-column-group",
    "table-footer-group",
    "table-header-group",
    "table-row",
    "table-row-group",
}
CSS_FILTER_FUNCTIONS = {
    "blur",
    "brightness",
    "contrast",
    "drop-shadow",
    "env",
    "grayscale",
    "hue-rotate",
    "invert",
    "opacity",
    "saturate",
    "sepia",
    "url",
    "var",
}
CSS_CLIP_PATH_FUNCTIONS = {
    "circle",
    "ellipse",
    "env",
    "inset",
    "path",
    "polygon",
    "url",
    "var",
}


def css_function_arguments(value):
    """Return function calls in a CSS value, or None for invalid syntax."""
    calls = []
    index = 0
    while index < len(value):
        if value[index].isspace():
            index += 1
            continue
        name_match = re.match(r"[-A-Za-z_][-\w]*", value[index:])
        if not name_match:
            return None
        name = name_match.group(0).lower()
        index += name_match.end()
        if index >= len(value) or value[index] != "(":
            return None
        depth = 1
        argument_start = index + 1
        index += 1
        while index < len(value) and depth:
            if value[index] == "(":
                depth += 1
            elif value[index] == ")":
                depth -= 1
            index += 1
        if depth:
            return None
        calls.append((name, value[argument_start : index - 1].strip()))
    return calls


def css_display_is_valid(value):
    value = value.strip().lower()
    if value in CSS_WIDE_KEYWORDS:
        return True
    tokens = value.split()
    return bool(tokens) and all(token in CSS_DISPLAY_KEYWORDS for token in tokens)


def css_filter_is_valid(value):
    value = value.strip().lower()
    if value in CSS_WIDE_KEYWORDS or value == "none":
        return True
    calls = css_function_arguments(value)
    if not calls:
        return False
    for name, arguments in calls:
        if name not in CSS_FILTER_FUNCTIONS or not arguments:
            return False
        if name == "opacity" and css_opacity_number(arguments) is None:
            return False
    return True


def css_clip_path_is_valid(value):
    value = value.strip().lower()
    if value in CSS_WIDE_KEYWORDS or value == "none":
        return True
    calls = css_function_arguments(value)
    if not calls:
        return False
    return all(
        name in CSS_CLIP_PATH_FUNCTIONS and arguments
        for name, arguments in calls
    )


def css_color_is_valid(value):
    value = value.strip().lower()
    if value in CSS_WIDE_KEYWORDS:
        return True
    if value in {"currentcolor", "transparent"}:
        return True
    if value in CSS_NAMED_COLORS:
        return True
    if re.fullmatch(r"#(?:[0-9a-f]{3}|[0-9a-f]{4}|[0-9a-f]{6}|[0-9a-f]{8})", value):
        return True
    calls = css_function_arguments(value)
    if not calls:
        return False
    return all(
        name in CSS_COLOR_FUNCTIONS and arguments
        for name, arguments in calls
    )


def css_declaration_is_valid(property_name, value):
    property_name = property_name.strip().lower()
    value = value.strip()
    if property_name == "display":
        return css_display_is_valid(value)
    if property_name == "visibility":
        return value.strip().lower() in {
            "collapse",
            "hidden",
            "visible",
            *CSS_WIDE_KEYWORDS,
        }
    if property_name == "content-visibility":
        return value.strip().lower() in {
            "auto",
            "hidden",
            "visible",
            *CSS_WIDE_KEYWORDS,
        }
    if property_name == "opacity":
        return (
            value.strip().lower() in CSS_WIDE_KEYWORDS
            or css_opacity_number(value) is not None
        )
    if property_name == "filter":
        return css_filter_is_valid(value)
    if property_name == "clip-path":
        return css_clip_path_is_valid(value)
    if property_name in {"color", "-webkit-text-fill-color"}:
        return css_color_is_valid(value)
    return False


def inline_style_declarations(style):
    style = re.sub(r"/\*.*?\*/", "", style or "", flags=re.S)
    declarations = []
    for declaration in style.split(";"):
        if ":" not in declaration:
            continue
        property_name, value = declaration.split(":", 1)
        property_name = property_name.strip().lower()
        value = value.strip()
        if not property_name or not value:
            continue
        important = bool(re.search(r"!\s*important\s*$", value, re.IGNORECASE))
        if important:
            value = re.sub(r"!\s*important\s*$", "", value, flags=re.IGNORECASE)
            value = value.strip()
        declarations.append((property_name, value, important))
    return declarations


def effective_inline_style(style):
    normal = {}
    important = {}
    for property_name, value, is_important in inline_style_declarations(style):
        if not css_declaration_is_valid(property_name, value):
            # Invalid declarations are discarded by the CSS parser and must
            # not replace an earlier valid declaration during cascade.
            continue
        declarations = important if is_important else normal
        declarations[property_name] = value
    effective = dict(normal)
    effective.update(important)
    return effective


def filter_has_zero_opacity(value):
    for match in re.finditer(
        r"(?:^|[,\s])opacity\s*\(\s*(calc\([^)]*\)|[^)]*)\)",
        value.lower(),
    ):
        if css_opacity_is_zero(match.group(1).strip()):
            return True
    return False


def clip_path_fully_clips(value):
    match = re.fullmatch(r"inset\s*\(([^)]*)\)", value.strip(), re.IGNORECASE)
    if not match:
        return False
    parts = [part.strip() for part in match.group(1).split()]
    if not parts or any(not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)%", part) for part in parts):
        return False
    numbers = [float(part[:-1]) for part in parts]
    if len(numbers) == 1:
        top = right = bottom = left = numbers[0]
    elif len(numbers) == 2:
        top = bottom = numbers[0]
        right = left = numbers[1]
    elif len(numbers) == 3:
        top, right, bottom = numbers
        left = right
    elif len(numbers) == 4:
        top, right, bottom, left = numbers
    else:
        return False
    return top + bottom >= 100.0 or left + right >= 100.0


def style_hides_content_except_visibility(style):
    effective = effective_inline_style(style)
    if effective.get("display", "").strip().lower() == "none":
        return True
    if effective.get("content-visibility", "").strip().lower() == "hidden":
        return True
    if "opacity" in effective and css_opacity_is_zero(effective["opacity"]):
        return True
    if "filter" in effective and filter_has_zero_opacity(effective["filter"]):
        return True
    if "clip-path" in effective and clip_path_fully_clips(effective["clip-path"]):
        return True
    color = effective.get("color", "")
    text_fill = effective.get("-webkit-text-fill-color", "")
    if css_color_is_transparent(color) or css_color_is_transparent(text_fill):
        return True
    return False


def style_visibility_is_hidden(style):
    effective = effective_inline_style(style)
    return effective.get("visibility", "").strip().lower() in {"hidden", "collapse"}


def style_hides_content(style):
    return style_hides_content_except_visibility(style) or style_visibility_is_hidden(
        style
    )


def html_first_attribute(tag_text, name):
    """Return (present, raw value) for the first matching HTML attribute."""
    if not tag_text:
        return False, None
    position = 1
    while position < len(tag_text) and tag_text[position].isspace():
        position += 1
    if position < len(tag_text) and tag_text[position] == "/":
        position += 1
    while position < len(tag_text) and not tag_text[position].isspace() and tag_text[position] not in ">/":
        position += 1
    found = False
    value = None
    while position < len(tag_text):
        while position < len(tag_text) and (tag_text[position].isspace() or tag_text[position] == "/"):
            position += 1
        if position >= len(tag_text) or tag_text[position] == ">":
            break
        name_start = position
        while (
            position < len(tag_text)
            and not tag_text[position].isspace()
            and tag_text[position] not in "=/>"
        ):
            position += 1
        attribute_name = tag_text[name_start:position].lower()
        while position < len(tag_text) and tag_text[position].isspace():
            position += 1
        attribute_value = None
        if position < len(tag_text) and tag_text[position] == "=":
            position += 1
            while position < len(tag_text) and tag_text[position].isspace():
                position += 1
            if position < len(tag_text) and tag_text[position] in "\"'":
                quote = tag_text[position]
                position += 1
                value_start = position
                while position < len(tag_text) and tag_text[position] != quote:
                    position += 1
                attribute_value = tag_text[value_start:position]
                if position < len(tag_text):
                    position += 1
            else:
                value_start = position
                while (
                    position < len(tag_text)
                    and not tag_text[position].isspace()
                    and tag_text[position] != ">"
                ):
                    position += 1
                attribute_value = tag_text[value_start:position]
        if attribute_name == name.lower() and not found:
            found = True
            value = attribute_value
    return found, value


def inline_style_creates_block_boundary(style):
    effective = effective_inline_style(style)
    display = effective.get("display", "").strip().lower()
    if not display:
        return False
    return display.split()[0] in {
        "block",
        "flow-root",
        "flex",
        "grid",
        "list-item",
        "table",
    }


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
    BLOCK_LEVEL_TAGS = {
        "address",
        "article",
        "aside",
        "blockquote",
        "body",
        "caption",
        "center",
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
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "hgroup",
        "hr",
        "html",
        "legend",
        "li",
        "main",
        "menu",
        "nav",
        "ol",
        "p",
        "pre",
        "search",
        "section",
        "summary",
        "table",
        "tbody",
        "td",
        "tfoot",
        "th",
        "thead",
        "tr",
        "ul",
    }
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
    FOREIGN_SELF_CLOSING_ROOTS = {"math", "svg"}

    def __init__(
        self,
        email,
        required_aria_labelledby=None,
        required_ancestor_tags=(),
    ):
        super().__init__(convert_charrefs=True)
        self.email = email
        self.required_aria_labelledby = required_aria_labelledby
        self.required_ancestor_tags = tuple(required_ancestor_tags)
        self.found = False
        self._anchor = None
        self._contexts = []
        self._next_context_id = 0

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
    def _hides_content(cls, attrs, include_visibility=True):
        if any(attribute.lower() == "hidden" for attribute, _ in attrs):
            return True
        style = cls._attribute(attrs, "style") or ""
        if include_visibility:
            return style_hides_content(style)
        return style_hides_content_except_visibility(style)

    def _pop_context(self, tag):
        for index in range(len(self._contexts) - 1, -1, -1):
            if self._contexts[index]["tag"] == tag:
                popped = self._contexts[index:]
                del self._contexts[index:]
                return popped
        return []

    def _visibility_is_hidden(self, visibility_visible=False):
        hidden = False
        for context in self._contexts:
            if context["visibility_visible"]:
                hidden = False
            elif context["visibility_hidden"]:
                hidden = True
        if visibility_visible:
            hidden = False
        return hidden

    def _is_hidden_context(
        self,
        summary_details_id=None,
        visibility_visible=False,
    ):
        if any(
            context["hidden"] or context["nonrendered"]
            for context in self._contexts
        ):
            return True
        if self._visibility_is_hidden(visibility_visible):
            return True
        for index, context in enumerate(self._contexts):
            if not context["closed_details"]:
                continue
            if context["id"] == summary_details_id:
                continue
            if any(
                later["summary_details_id"] == context["id"]
                for later in self._contexts[index + 1 :]
            ):
                continue
            return True
        return False

    def _is_in_scope(self):
        if self.required_aria_labelledby is not None and not any(
            context["target"] for context in self._contexts
        ):
            return False
        return all(
            any(context["tag"] == tag for context in self._contexts)
            for tag in self.required_ancestor_tags
        )

    def _finish_anchor(self):
        if not self._anchor:
            return
        visible_text = re.sub(
            r"[ \t\n\f\r]+", " ", "".join(self._anchor["text"])
        ).strip(" \t\n\f\r")
        if (
            self._anchor["renderable"]
            and self._anchor["in_scope"]
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
            self._pop_context("a")

        style = self._attribute(attrs, "style") or ""
        hidden = self._hides_content(attrs, include_visibility=False)
        if tag == "dialog" and not self._has_attribute(attrs, "open"):
            hidden = True
        if self._has_attribute(attrs, "popover"):
            hidden = True
        nonrendered = tag in self.NON_RENDERED_TAGS

        effective_visibility = (
            effective_inline_style(style).get("visibility", "").strip().lower()
        )
        visibility_hidden = effective_visibility in {"hidden", "collapse"}
        visibility_visible = effective_visibility == "visible"
        closed_details = tag == "details" and not self._has_attribute(
            attrs, "open"
        )
        summary_details_id = None
        if tag == "summary":
            for context in reversed(self._contexts):
                if context["closed_details"]:
                    summary_details_id = context["id"]
                    break

        renderable = not (
            self._is_hidden_context(
                summary_details_id=summary_details_id,
                visibility_visible=visibility_visible,
            )
            or hidden
            or visibility_hidden
            or nonrendered
        )
        block_boundary = (
            tag in self.BLOCK_LEVEL_TAGS
            or inline_style_creates_block_boundary(style)
        )
        target = False
        if self.required_aria_labelledby is not None and tag == "section":
            labelled_by = self._attribute(attrs, "aria-labelledby") or ""
            target = self.required_aria_labelledby in labelled_by.split()

        if tag == "a" and renderable:
            raw_tag = self.get_starttag_text() or ""
            has_href, raw_href = html_first_attribute(raw_tag, "href")
            self._anchor = {
                "href": raw_href if has_href else None,
                "text": [],
                "renderable": True,
                "in_scope": self._is_in_scope(),
            }
        elif tag == "br" and self._anchor and renderable:
            self._anchor["text"].append("\n")
        elif (
            tag != "a"
            and self._anchor
            and renderable
            and block_boundary
        ):
            self._anchor["text"].append("\n")
        if tag not in self.VOID_TAGS:
            context_id = self._next_context_id
            self._next_context_id += 1
            self._contexts.append(
                {
                    "id": context_id,
                    "tag": tag,
                    "hidden": hidden,
                    "nonrendered": nonrendered,
                    "target": target,
                    "visible_block": renderable and block_boundary,
                    "visibility_hidden": visibility_hidden,
                    "visibility_visible": visibility_visible,
                    "closed_details": closed_details,
                    "summary_details_id": summary_details_id,
                }
            )

    def handle_startendtag(self, tag, attrs):
        tag = tag.lower()
        if tag in self.FOREIGN_SELF_CLOSING_ROOTS:
            # Foreign-content roots honor the self-closing slash.
            return
        # HTML ignores the self-closing slash on non-void elements. Keeping the
        # element open also keeps script/style/template contents inert.
        self.handle_starttag(tag, attrs)

    def handle_data(self, data):
        if self._is_hidden_context():
            return
        if self._anchor:
            self._anchor["text"].append(data)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "a":
            self._finish_anchor()
        popped = self._pop_context(tag)
        if self._anchor and popped and popped[0]["visible_block"]:
            self._anchor["text"].append("\n")

    def close(self):
        super().close()
        self._finish_anchor()


def has_html_contact_link(
    fragment,
    email,
    required_aria_labelledby=None,
    required_ancestor_tags=(),
):
    parser = _ContactAnchorParser(
        email,
        required_aria_labelledby=required_aria_labelledby,
        required_ancestor_tags=required_ancestor_tags,
    )
    try:
        parser.feed(fragment)
        parser.close()
    except (AssertionError, ValueError):
        return False
    return parser.found


def labelled_html_section_bounds(source, label):
    """Return the bounds of the section labelled by an aria-labelledby ID."""
    for match in re.finditer(r"<section\b", source, re.IGNORECASE):
        start = match.start()
        end = html_tag_end(source, start)
        if end is None:
            continue
        has_label, raw_label = html_first_attribute(
            source[start:end],
            "aria-labelledby",
        )
        if not has_label or label not in (raw_label or "").split():
            continue

        depth = 1
        section_tag = re.compile(
            r"<section\b[^>]*>|</section\s*>",
            re.IGNORECASE,
        )
        for nested in section_tag.finditer(source, end):
            if nested.group(0).lower().startswith("</"):
                depth -= 1
            else:
                depth += 1
            if depth == 0:
                return start, nested.end()
        return start, len(source)
    return None


def html_ancestor_context(source, end):
    """Return opening tags for the elements that contain the given offset."""
    prefix = source[:end]
    raw_text = re.compile(
        r"(<(?P<tag>script|style|textarea|xmp)\b[^>]*>).*?"
        r"(?P<close></(?P=tag)\s*>)",
        re.IGNORECASE | re.DOTALL,
    )
    prefix = raw_text.sub(lambda match: match.group(1) + match.group("close"), prefix)
    stack = []
    tag_pattern = re.compile(
        r"<!--.*?-->|<![^>]*>|</?[A-Za-z][^>]*>",
        flags=re.DOTALL,
    )
    name_pattern = re.compile(r"</?\s*([A-Za-z][A-Za-z0-9:-]*)")
    for match in tag_pattern.finditer(prefix):
        raw_tag = match.group(0)
        if raw_tag.startswith("<!--") or raw_tag.startswith("<!"):
            continue
        name_match = name_pattern.match(raw_tag)
        if not name_match:
            continue
        name = name_match.group(1).lower()
        if raw_tag.startswith("</"):
            for index in range(len(stack) - 1, -1, -1):
                if stack[index][0] == name:
                    del stack[index:]
                    break
            continue
        if name in _ContactAnchorParser.VOID_TAGS:
            continue
        if (
            name in _ContactAnchorParser.FOREIGN_SELF_CLOSING_ROOTS
            and raw_tag.rstrip().endswith("/>")
        ):
            continue
        stack.append((name, raw_tag))
    return "".join(raw_tag for _, raw_tag in stack)


def has_html_contact_link_in_labelled_section(
    source,
    email,
    label,
    required_ancestor_tags=(),
):
    bounds = labelled_html_section_bounds(source, label)
    if bounds is None:
        return False
    start, end = bounds
    parser = _ContactAnchorParser(
        email,
        required_aria_labelledby=label,
        required_ancestor_tags=required_ancestor_tags,
    )
    try:
        # Keep the ancestor stack, but avoid parsing unrelated text and data
        # before the target section (the document can contain large blobs).
        parser.feed(html_ancestor_context(source, start))
        parser.feed(source[start:end])
        parser.close()
    except (AssertionError, ValueError):
        return False
    return parser.found


def markdown_inline_block_end(source, start):
    # Delimiter state is local to one Markdown leaf block. It must not leak
    # across blank lines, new list items, blockquote containers, or headings.
    opener_line_start = source.rfind("\n", 0, start) + 1
    opener_line_end = source.find("\n", start)
    if opener_line_end < 0:
        opener_line_end = len(source)
    opener = parse_markdown_container(
        source[opener_line_start:opener_line_end]
    )
    opener_quote_depth = opener["blockquote_depth"]

    boundary = re.search(r"\r?\n[ \t]*\r?\n", source[start:])
    block_end = len(source) if boundary is None else start + boundary.start()

    line_start = opener_line_end + 1
    while line_start < block_end:
        line_end = source.find("\n", line_start)
        if line_end < 0 or line_end > block_end:
            line_end = block_end
        parsed = parse_markdown_container(source[line_start:line_end])
        quote_depth = parsed["blockquote_depth"]

        if parsed["list_markers"]:
            # A list marker starts a different leaf container.
            return line_start
        if quote_depth and quote_depth != opener_quote_depth:
            # A blockquote marker at a different depth starts a different
            # container. A missing marker may be a lazy paragraph continuation.
            return line_start
        if markdown_is_block_boundary_line(parsed["content"]):
            return line_start

        line_start = line_end + 1

    return block_end


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
        block_end = markdown_inline_block_end(source, opener_start)
        cursor = opener_end
        while cursor < block_end:
            if source[cursor] != "`":
                cursor += 1
                continue
            closer_start = cursor
            while cursor < block_end and source[cursor] == "`":
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


def markdown_comment_openers(source, ignored_ranges=()):
    """Return unescaped HTML-comment openers outside ignored ranges."""
    openers = []
    for match in re.finditer(r"<!--", source):
        position = match.start()
        if markdown_is_escaped(source, position):
            continue
        if any(
            range_start <= position < range_end
            for range_start, range_end, _ in ignored_ranges
        ):
            continue
        openers.append(position)
    return openers


def markdown_comment_close(source, start):
    # Once an opener outside code has been recognized, comment content is raw
    # HTML: the first following terminator closes it even when backticks would
    # otherwise make the terminator look like part of a code span.
    return source.find("-->", start + 4)


def mask_html_comments(source, replacement=" ", ignored_ranges=()):
    masked = list(source)
    for start in markdown_comment_openers(source, ignored_ranges):
        close = markdown_comment_close(source, start)
        end = len(source) if close < 0 else close + 3
        for position in range(start, end):
            if masked[position] not in "\r\n":
                masked[position] = replacement
    return "".join(masked)


def markdown_closing_bracket(source, start):
    depth = 0
    index = start
    block_end = markdown_inline_block_end(source, start)
    while index < block_end:
        character = source[index]
        if character == "\\" and index + 1 < block_end:
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
    block_end = markdown_inline_block_end(source, start)
    while index < block_end:
        character = source[index]
        if character == "\\" and index + 1 < block_end:
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
    for start in markdown_comment_openers(source, ignored_ranges):
        close = markdown_comment_close(source, start)
        if close < 0:
            return start
    return None


def mask_markdown_line(source):
    return "".join(
        character if character in "\r\n" else " " for character in source
    )


def markdown_has_comment_outside_code(source, code_ranges):
    return bool(markdown_comment_openers(source, code_ranges))


def markdown_is_escaped(source, index):
    backslashes = 0
    cursor = index - 1
    while cursor >= 0 and source[cursor] == "\\":
        backslashes += 1
        cursor -= 1
    return backslashes % 2 == 1


def markdown_title_end(source, start, end=None):
    if end is None:
        end = len(source)
    opener = source[start]
    closer = opener if opener in "\"'" else ")"
    cursor = start + 1
    while cursor < end:
        character = source[cursor]
        if character == "\\" and cursor + 1 < end:
            cursor += 2
            continue
        if character == closer:
            return cursor
        if opener == "(" and character == "(":
            return None
        cursor += 1
    return None


def parse_markdown_inline_link(source, closing_bracket):
    block_end = markdown_inline_block_end(source, closing_bracket)
    if (
        closing_bracket + 1 >= block_end
        or source[closing_bracket + 1] != "("
    ):
        return None

    cursor = closing_bracket + 2
    while cursor < block_end and source[cursor] in " \t\r\n":
        cursor += 1
    if cursor >= block_end:
        return None

    if source[cursor] == "<":
        destination_start = cursor + 1
        cursor = source.find(">", destination_start, block_end)
        if cursor < 0 or "\n" in source[destination_start:cursor]:
            return None
        destination = source[destination_start:cursor]
        cursor += 1
    else:
        destination_start = cursor
        while (
            cursor < block_end
            and source[cursor] not in " \t\r\n)"
        ):
            cursor += 1
        if cursor == destination_start:
            return None
        destination = source[destination_start:cursor]

    after_destination = cursor
    while cursor < block_end and source[cursor] in " \t\r\n":
        cursor += 1
    had_whitespace = cursor > after_destination

    if cursor < block_end and source[cursor] in "\"'(":
        if not had_whitespace:
            return None
        title_end = markdown_title_end(source, cursor, block_end)
        if title_end is None:
            return None
        cursor = title_end + 1
        while cursor < block_end and source[cursor] in " \t\r\n":
            cursor += 1

    if cursor >= block_end or source[cursor] != ")":
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


def markdown_inline_links(source, masked=None):
    if masked is None:
        masked = source
    links = []
    index = 0
    while index < len(masked):
        if masked[index] != "[" or markdown_is_escaped(masked, index):
            index += 1
            continue
        closing_bracket = markdown_closing_bracket(masked, index)
        if closing_bracket is None:
            index += 1
            continue
        if markdown_label_contains_inline_link(masked, index, closing_bracket):
            # The supported contract is deliberately limited to top-level
            # inline links. A complete outer link construct hides any nested
            # source link from this verifier.
            outer_link = parse_markdown_inline_link(source, closing_bracket)
            if outer_link is not None:
                index = outer_link["end"]
            else:
                index = closing_bracket + 1
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
        closing_bracket = markdown_closing_bracket(source, index + 1)
        if closing_bracket is None:
            # An unmatched image opener is literal text. It must not mask a
            # later paragraph.
            index += 1
            continue
        destination = closing_bracket + 1
        while destination < len(source) and source[destination] in " \t":
            destination += 1
        if destination < len(source) and source[destination] == "(":
            close = markdown_closing_parenthesis(source, destination)
            if close is None:
                index += 1
                continue
            end = close
        elif destination < len(source) and source[destination] == "[":
            reference_end = markdown_closing_bracket(source, destination)
            if reference_end is None:
                index += 1
                continue
            end = reference_end + 1
        else:
            index += 1
            continue
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
    list_marker_positions = []
    list_indent = 0
    list_base = 0
    while position < len(expanded):
        blockquote = re.match(r"[ ]{0,3}>[ ]?", expanded[position:])
        if blockquote:
            position += blockquote.end()
            blockquote_depth += 1
            list_base = position
            list_markers = []
            list_marker_positions = []
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
            list_marker_positions.append(position + list_item.start(1))
            position += len(marker) + consumed_spaces
            list_markers.append(marker)
            list_indent = position - list_base
            continue
        break
    return {
        "blockquote_depth": blockquote_depth,
        "list_markers": list_markers,
        "list_marker_positions": list_marker_positions,
        "list_indent": list_indent,
        "list_base": list_base,
        "content": expanded[position:],
    }


def markdown_is_table_delimiter_row(content):
    stripped = content.strip()
    if "|" not in stripped:
        return False
    cells = stripped.strip("|").split("|")
    return bool(cells) and all(
        re.fullmatch(r":?-+:?", cell.strip()) for cell in cells
    )


def markdown_is_block_boundary_line(content):
    stripped = content
    if re.match(r"^[ ]{0,3}#{1,6}(?:[ \t]+|$)", stripped):
        return True
    if re.match(
        r"^[ ]{0,3}(?:(?:\*[ \t]*){3,}|(?:-[ \t]*){3,}|"
        r"(?:_[ \t]*){3,})$",
        stripped,
    ):
        return True
    # Setext heading underlines end the preceding paragraph as a block. A
    # single or double hyphen is a valid setext underline; three or more
    # hyphens can also be a thematic break, which has the same block boundary.
    return bool(
        re.match(r"^[ ]{0,3}(?:=+|-+)[ \t]*$", stripped)
    )


def mask_markdown_definition_blocks(source):
    footnote_definition = re.compile(
        r"^[ ]{0,3}\[\^(?:\\.|[^\]\\])+\]:"
    )
    reference_definition = re.compile(
        r"^[ ]{0,3}\[(?!\^)(?:\\.|[^\]\\])+\]:"
    )

    def title_closer(text, opener):
        closer = opener if opener in "\"'" else ")"
        cursor = 1
        while cursor < len(text):
            if text[cursor] == "\\":
                cursor += 2
                continue
            if text[cursor] == closer:
                return cursor
            cursor += 1
        return None

    def split_destination_and_title(rest):
        stripped = rest.strip()
        if not stripped:
            return None
        if stripped.startswith("<"):
            end = stripped.find(">")
            if end < 0:
                return None
            destination = stripped[1:end]
            remainder = stripped[end + 1 :]
        else:
            match = re.match(r"(\S+)(.*)$", stripped, re.DOTALL)
            if not match:
                return None
            destination = match.group(1)
            remainder = match.group(2)
        return destination, remainder.lstrip()

    lines = []
    state = None
    for line in source.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        ending = line[len(body) :]
        parsed = parse_markdown_container(body)
        content = parsed["content"]
        stripped = content.strip()

        if state:
            kind = state["kind"]
            if kind == "footnote":
                if not stripped:
                    state = None
                    lines.append(line)
                else:
                    lines.append(" " * len(body) + ending)
                continue
            if kind == "destination":
                if not stripped:
                    state = None
                    lines.append(line)
                    continue
                if stripped.startswith(("\"", "'", "(")):
                    state = None
                else:
                    parts = split_destination_and_title(stripped)
                    is_inline_link = bool(
                        re.fullmatch(r"\[[^\]]*\]\([^\n]*\)", stripped)
                    )
                    if parts is None or is_inline_link:
                        state = None
                    else:
                        lines.append(" " * len(body) + ending)
                        remainder = parts[1]
                        if remainder and remainder[0] in "\"'(":
                            closer = title_closer(remainder, remainder[0])
                            if closer is None:
                                state = {
                                    "kind": "title_continuation",
                                    "opener": remainder[0],
                                }
                            else:
                                state = None
                        else:
                            state = {"kind": "title"}
                        continue
            elif kind == "title":
                if not stripped:
                    state = None
                    lines.append(line)
                    continue
                if stripped[0] in "\"'(":
                    lines.append(" " * len(body) + ending)
                    closer = title_closer(stripped, stripped[0])
                    if closer is None:
                        state = {
                            "kind": "title_continuation",
                            "opener": stripped[0],
                        }
                    continue
                state = None
            elif kind == "title_continuation":
                lines.append(" " * len(body) + ending)
                closer = title_closer(stripped, state["opener"])
                if closer is not None:
                    state = None
                continue

        footnote_match = footnote_definition.match(content)
        reference_match = reference_definition.match(content)
        if footnote_match:
            lines.append(" " * len(body) + ending)
            state = {"kind": "footnote"}
            continue
        if reference_match:
            lines.append(" " * len(body) + ending)
            rest = content[reference_match.end() :]
            parts = split_destination_and_title(rest)
            if parts is None:
                state = {"kind": "destination"}
            else:
                remainder = parts[1]
                if remainder and remainder[0] in "\"'(":
                    closer = title_closer(remainder, remainder[0])
                    if closer is None:
                        state = {
                            "kind": "title_continuation",
                            "opener": remainder[0],
                        }
                else:
                    state = {"kind": "title"}
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


def markdown_hidden_html_ranges(source):
    """Return source ranges occupied by hidden or non-rendered HTML subtrees."""
    code_ranges = markdown_code_span_ranges(source)
    nonrendered = {
        "canvas",
        "datalist",
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
    void_tags = {
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
    ranges = []
    next_frame_id = 0

    def append_without(start, end, exclusions):
        if end <= start:
            return
        cursor = start
        for exclusion_start, exclusion_end in sorted(exclusions):
            if exclusion_end <= cursor:
                continue
            if exclusion_start >= end:
                break
            if exclusion_start > cursor:
                ranges.append((cursor, min(exclusion_start, end)))
            cursor = max(cursor, exclusion_end)
            if cursor >= end:
                break
        if cursor < end:
            ranges.append((cursor, end))

    def close_frames(frames, ancestors, end):
        for index, frame in enumerate(frames):
            outer_frames = ancestors + frames[:index]
            if frame["visibility_visible"]:
                for ancestor in outer_frames:
                    if ancestor["visibility_hidden"]:
                        ancestor["visibility_overrides"].append((frame["start"], end))
            if frame["summary_details_id"] is not None:
                for ancestor in outer_frames:
                    if ancestor["id"] == frame["summary_details_id"]:
                        ancestor["summary_ranges"].append((frame["start"], end))
                        break

        for frame in frames:
            frame_end = end
            if frame["hidden"] or frame["nonrendered"]:
                ranges.append((frame["start"], frame_end))
            if frame["visibility_hidden"]:
                append_without(
                    frame["start"],
                    frame_end,
                    frame["visibility_overrides"],
                )
            if frame["closed_details"]:
                append_without(
                    frame["start"],
                    frame_end,
                    frame["summary_ranges"],
                )

    index = 0
    while index < len(source):
        start = source.find("<", index)
        if start < 0:
            break
        if markdown_is_escaped(source, start):
            # An escaped opening angle bracket is literal Markdown text.
            index = start + 1
            continue
        # HTML-looking text inside a code span is literal, not a hidden context.
        if any(
            range_start <= start < range_end
            for range_start, range_end, _ in code_ranges
        ):
            index = start + 1
            continue
        end = html_tag_end(source, start)
        if end is None:
            index = start + 1
            continue
        tag = source[start:end]
        name_match = re.match(r"<\s*/?\s*([A-Za-z][A-Za-z0-9-]*)", tag)
        if not name_match:
            index = end
            continue
        name = name_match.group(1).lower()
        if tag.lstrip().startswith("</"):
            for stack_index in range(len(stack) - 1, -1, -1):
                if stack[stack_index]["tag"] != name:
                    continue
                popped = stack[stack_index:]
                close_frames(popped, stack[:stack_index], end)
                del stack[stack_index:]
                break
        else:
            has_open, _ = html_first_attribute(tag, "open")
            has_popover, _ = html_first_attribute(tag, "popover")
            has_hidden, _ = html_first_attribute(tag, "hidden")
            has_style, style = html_first_attribute(tag, "style")
            style = unescape(style or "")
            hidden = (
                has_hidden
                or has_popover
                or (name == "dialog" and not has_open)
                or (has_style and style_hides_content_except_visibility(style))
            )
            visibility = (
                effective_inline_style(style).get("visibility", "").strip().lower()
            )
            visibility_hidden = visibility in {"hidden", "collapse"}
            visibility_visible = visibility == "visible"
            closed_details = name == "details" and not has_open
            summary_details_id = None
            if name == "summary":
                for frame in reversed(stack):
                    if frame["closed_details"]:
                        summary_details_id = frame["id"]
                        break

            nonrendered_element = name in nonrendered
            self_closing = tag[:-1].rstrip().endswith("/")
            if name not in void_tags and not (
                self_closing and name in {"math", "svg"}
            ):
                frame_id = next_frame_id
                next_frame_id += 1
                stack.append(
                    {
                        "id": frame_id,
                        "tag": name,
                        "start": start,
                        "hidden": hidden,
                        "nonrendered": nonrendered_element,
                        "visibility_hidden": visibility_hidden,
                        "visibility_visible": visibility_visible,
                        "visibility_overrides": [],
                        "closed_details": closed_details,
                        "summary_details_id": summary_details_id,
                        "summary_ranges": [],
                    }
                )
        index = end
    if stack:
        close_frames(stack, [], len(source))
    return sorted(ranges)


def strip_markdown_code_and_comments(markdown):
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
    processing_instruction_until_close = False
    comment_until_close = False
    previous_blank = True
    paragraph_open = False
    previous_quote_depth = 0
    in_table = False
    indented_code = False
    active_list_indent = None
    active_list_base = 0

    for line in markdown.splitlines():
        if processing_instruction_until_close:
            close = line.find("?>")
            if close < 0:
                # A processing instruction does not end at a blank line.
                lines.append(mask_markdown_line(line))
                previous_blank = True
                continue
            processing_instruction_until_close = False
            remainder = line[close + 2 :]
            if remainder.strip():
                lines.append(remainder)
                previous_blank = False
                paragraph_open = True
            else:
                lines.append("")
                previous_blank = True
            continue
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
            # The complete line belongs to the HTML comment block, including
            # any Markdown-looking text after the closing delimiter.
            line = mask_markdown_line(line)
            comment_until_close = False
            previous_blank = True
        if fence:
            fence_parsed = parse_markdown_container(line)
            fence_content = fence_parsed["content"]
            fence_leading = len(fence_content) - len(fence_content.lstrip(" "))
            exits_fence = (
                fence_parsed["blockquote_depth"] < fence["blockquote_depth"]
            )
            if fence["list_markers"]:
                marker_positions = fence_parsed["list_marker_positions"]
                if marker_positions:
                    relative_marker = min(
                        position - fence_parsed["list_base"]
                        for position in marker_positions
                    )
                    exits_fence = exits_fence or relative_marker < fence["list_indent"]
                elif fence_content.strip():
                    # A blank line can occur inside a list-item fence even when
                    # it has no indentation. Only a nonblank dedent leaves it.
                    exits_fence = exits_fence or fence_leading < fence["list_indent"]
            if exits_fence:
                # A quoted/list-item fence ends with its container. The current
                # line must then be processed again outside the old fence.
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
                        paragraph_open = False
                continue

        parsed = parse_markdown_container(line)
        content = parsed["content"]
        quote_depth = parsed["blockquote_depth"]
        if quote_depth != previous_quote_depth:
            # A new quote container starts a fresh paragraph context.
            paragraph_open = False
            active_list_indent = None
            active_list_base = 0
            in_table = False
        if parsed["list_markers"]:
            # A new list item starts a fresh paragraph context.
            paragraph_open = False
            active_list_indent = parsed["list_indent"]
            in_table = False
        previous_quote_depth = quote_depth
        fence_candidate = markdown_fence_candidate(line)
        if fence_candidate:
            _, fence_marker, fence_suffix = fence_candidate
            if fence_marker[0] == "`" and "`" in fence_suffix:
                fence_candidate = None
        if "<!--" in content and fence_candidate is None:
            code_ranges = markdown_code_span_ranges(line)
            if markdown_has_comment_outside_code(line, code_ranges):
                opener = markdown_unclosed_comment_start(line, code_ranges)
                if opener is not None:
                    comment_until_close = True
                    line = line[:opener] + mask_markdown_line(line[opener:])
                    lines.append(line)
                    previous_blank = True
                    paragraph_open = False
                    continue
                if line.startswith("<!--"):
                    # A column-zero comment starts an HTML block whose complete
                    # line is raw HTML, even when the comment closes mid-line.
                    line = mask_markdown_line(line)
                else:
                    line = mask_html_comments(line, "\ue102", code_ranges)
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
            paragraph_open = False
            in_table = False
            continue
        if active_list_indent is not None and leading < active_list_indent:
            # A dedented block start leaves the active list item. Plain text
            # may still be a lazy paragraph continuation, but an HTML block
            # cannot interrupt that paragraph from outside the list item.
            paragraph_open = False
        if markdown_is_table_delimiter_row(content):
            in_table = True
            paragraph_open = False
        elif in_table:
            # Table rows are a block and cannot be interrupted by a type-7
            # HTML block until the table ends.
            paragraph_open = False

        if parsed["list_markers"]:
            active_list_indent = parsed["list_indent"]
            active_list_base = parsed["list_base"]
            relative_leading = leading
        elif active_list_indent is not None:
            if leading < active_list_indent:
                active_list_indent = None
                active_list_base = 0
                relative_leading = leading
            else:
                relative_leading = leading - active_list_indent
        else:
            relative_leading = leading
        if indented_code:
            if relative_leading >= 4:
                paragraph_open = False
                continue
            indented_code = False
        elif relative_leading >= 4 and (previous_blank or not lines):
            indented_code = True
            paragraph_open = False
            lines.append("")
            continue

        candidate = fence_candidate or markdown_fence_candidate(line)
        if candidate:
            parsed, marker, suffix = candidate
            if marker[0] != "`" or "`" not in suffix:
                fence = {
                    "marker": marker[0],
                    "length": len(marker),
                    "blockquote_depth": parsed["blockquote_depth"],
                    "list_markers": parsed["list_markers"],
                    "list_marker_positions": parsed["list_marker_positions"],
                    "list_indent": parsed["list_indent"],
                    "list_base": parsed["list_base"],
                }
                previous_blank = True
                paragraph_open = False
                in_table = False
                lines.append("")
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
                paragraph_open = False
                in_table = False
                lines.append("")
                continue
            if re.match(r"^<\?", stripped):
                close = stripped.find("?>")
                if close < 0:
                    processing_instruction_until_close = True
                    previous_blank = True
                    paragraph_open = False
                    in_table = False
                    lines.append("")
                    continue
                remainder = stripped[close + 2 :]
                if remainder.strip():
                    lines.append(remainder)
                    previous_blank = False
                    paragraph_open = True
                else:
                    lines.append("")
                    previous_blank = True
                paragraph_open = bool(remainder.strip())
                in_table = False
                continue
            if (
                raw_block_pattern.match(stripped)
                or re.match(r"^<!", stripped)
                or (not paragraph_open and html_tag_only(stripped))
            ):
                raw_block_until_blank = True
                previous_blank = True
                paragraph_open = False
                in_table = False
                lines.append("")
                continue

        if markdown_is_block_boundary_line(content):
            lines.append(line)
            # Every block boundary ends the current paragraph. The next line
            # may therefore begin an indented-code block, including after a
            # setext heading underline or a thematic break.
            previous_blank = True
            indented_code = False
            paragraph_open = False
            in_table = False
            continue

        lines.append(line)
        previous_blank = False
        paragraph_open = not in_table

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
        r"&(?:#[xX]([0-9A-Fa-f]{1,6})|#([0-9]{1,7})|"
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
    return re.sub(r"[ \t\n\f\r]+", " ", label).strip(" \t\n\f\r")


def has_markdown_contact_link(markdown, email):
    source = mask_markdown_definition_blocks(
        strip_markdown_code_and_comments(markdown)
    )
    hidden_ranges = markdown_hidden_html_ranges(source)
    masked = mask_markdown_code_spans(
        source, markdown_code_span_ranges(source)
    )
    masked = mask_markdown_image_descriptions(masked)
    masked = mask_html_tags(masked)
    links = markdown_inline_links(source, masked)
    expected_destination = f"mailto:{email}"
    for link in links:
        if any(
            range_start <= link["label_start"] < range_end
            for range_start, range_end in hidden_ranges
        ):
            continue
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
impressum = re.search(
    r'<footer\b[^>]*>[\s\S]*?<section\b[^>]*'
    r'aria-labelledby\s*=\s*["\']imp-h["\'][^>]*>[\s\S]*?</section>',
    HTML,
    flags=re.IGNORECASE,
)
impressum_text = impressum.group(0) if impressum else ""
required_provider_details = (PROVIDER_NAME, PROVIDER_ADDRESS, CONTACT_EMAIL)
html_has_provider_details = (
    "v2.9.5" in impressum_text
    and "v2.7.0" not in impressum_text
    and "§ 5 DDG" in impressum_text
    and all(detail in impressum_text for detail in required_provider_details)
    and has_html_contact_link_in_labelled_section(
        HTML,
        CONTACT_EMAIL,
        "imp-h",
        required_ancestor_tags=("footer",),
    )
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
