#!/usr/bin/env python3
"""Odoo Apps Store description validator (Publisher Platform / odoo_store target).

Validates a module description HTML file (static/description/index.html) against
the Odoo Apps Store sanitizer rules. The store renders descriptions through
``odoo.tools.html_sanitize``, which:

  * removes a fixed set of tags (<style>, <link>, <head>, <script>, ...),
  * keeps only a whitelist of inline ``style`` properties,
  * drops external web-font references and absolute image URLs,
  * keeps relative image paths (resolved under static/description/).

This validator catches those mistakes BEFORE upload, so every module ships a
description that renders correctly on apps.odoo.com.

Usage:
    python validator.py <index.html> [--rules sanitizer_rules.yaml]

Exit code: 0 = PASS (no unsupported constructs), 1 = FAIL.

Design note:
    Rules live in sanitizer_rules.yaml (single source of truth). If PyYAML is
    not installed, an embedded copy is used as a fallback; keep it in sync.
"""
import argparse
import os
import sys
from html.parser import HTMLParser

try:
    import yaml  # type: ignore
    _HAVE_YAML = True
except ImportError:
    _HAVE_YAML = False

# --------------------------------------------------------------------------- #
# Embedded fallback (kept in sync with sanitizer_rules.yaml).
# --------------------------------------------------------------------------- #
EMBEDDED_RULES = {
    "kill_tags": [
        "base", "embed", "frame", "head", "iframe", "link", "meta",
        "noscript", "object", "script", "style", "title",
    ],
    "allowed_inline_style_properties": [
        "font-size", "font-family", "font-weight", "background-color",
        "background", "color", "text-align", "line-height", "letter-spacing",
        "text-transform", "text-decoration", "opacity", "float",
        "vertical-align", "display", "padding", "padding-top", "padding-left",
        "padding-bottom", "padding-right", "margin", "margin-top",
        "margin-left", "margin-bottom", "margin-right", "white-space",
        "border", "border-color", "border-radius", "border-style",
        "border-width", "border-top", "border-bottom", "border-left",
        "border-right", "border-top-style", "border-top-color",
        "border-top-width", "border-top-left-radius", "border-top-right-radius",
        "border-bottom-style", "border-bottom-color", "border-bottom-width",
        "border-bottom-left-radius", "border-bottom-right-radius", "height",
        "width", "max-width", "min-width", "min-height", "border-collapse",
        "border-spacing", "caption-side", "empty-cells", "table-layout",
    ],
    "forbidden_external_schemes": [
        "fonts.googleapis.com", "fonts.gstatic.com",
    ],
    "allowed_external_schemes": [
        "https://www.youtube.com", "https://youtu.be",
        "https://teams.microsoft.com", "mailto:", "skype:",
    ],
    "allowed_class_patterns": [
        "oe_", "col-", "row", "container", "container-fluid", "badge",
        "table", "img-fluid", "img-thumbnail", "rounded", "border", "bg-",
        "text-", "mb-", "mt-", "ml-", "mr-", "mx-", "my-", "p-", "pt-",
        "pb-", "d-flex", "d-block", "d-inline", "d-none", "shadow-",
        "font-weight-", "text-center", "text-left", "text-right",
        "align-items-", "justify-content-", "flex-",
    ],
    "image_path_policy": "relative_only",
}


def load_rules(rules_path):
    if rules_path and os.path.exists(rules_path) and _HAVE_YAML:
        with open(rules_path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    if rules_path and os.path.exists(rules_path) and not _HAVE_YAML:
        sys.stderr.write(
            "WARNING: PyYAML not installed; using embedded fallback rules.\n"
        )
    return EMBEDDED_RULES


# --------------------------------------------------------------------------- #
# Scanner
# --------------------------------------------------------------------------- #
class DescScanner(HTMLParser):
    def __init__(self, rules):
        super().__init__(convert_charrefs=True)
        self.kill_tags = set(t.lower() for t in rules["kill_tags"])
        self.allowed_style = set(
            p.lower() for p in rules["allowed_inline_style_properties"]
        )
        self.forbidden = rules["forbidden_external_schemes"]
        self.found_kill = set()
        self.bad_style = []
        self.font_links = []
        self.img_srcs = []
        self.classes = []
        self.has_oe = False
        self.has_bootstrap = False
        self._class_prefixes = rules["allowed_class_patterns"]

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        d = dict(attrs)
        if tag in self.kill_tags:
            self.found_kill.add(tag)
        if tag == "link":
            href = d.get("href", "")
            if any(s in href for s in self.forbidden):
                self.font_links.append(href)
        if "style" in d:
            for prop in _split_style_props(d["style"]):
                if prop and prop not in self.allowed_style:
                    self.bad_style.append(prop)
        if "class" in d:
            for c in d["class"].split():
                self.classes.append(c)
                if c.startswith("oe_"):
                    self.has_oe = True
                if any(c.startswith(p) or c == p for p in self._class_prefixes):
                    self.has_bootstrap = True
        if tag == "img":
            self.img_srcs.append(d.get("src", ""))

    def unknown_classes(self):
        out = []
        for c in self.classes:
            ok = c.startswith("oe_") or any(
                c.startswith(p) or c == p for p in self._class_prefixes
            )
            if not ok:
                out.append(c)
        return out


def _split_style_props(style):
    props = []
    for decl in style.split(";"):
        decl = decl.strip()
        if not decl or ":" not in decl:
            continue
        prop = decl.split(":", 1)[0].strip().lower()
        props.append(prop)
    return props


def _is_absolute(src):
    if not src:
        return False
    return src.startswith("http://") or src.startswith("https://") or src.startswith("//")


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #
def run(path, rules):
    with open(path, "r", encoding="utf-8") as fh:
        html = fh.read()
    scanner = DescScanner(rules)
    scanner.feed(html)

    unsupported = []
    for t in sorted(scanner.found_kill):
        unsupported.append(f"{t} tag")
    seen_style = []
    for p in scanner.bad_style:
        if p not in seen_style:
            seen_style.append(p)
            unsupported.append(f"{p} (inline style)")
    for href in scanner.font_links:
        unsupported.append(f"external web-font ({href})")

    abs_imgs = [s for s in scanner.img_srcs if _is_absolute(s)]
    if abs_imgs:
        for s in abs_imgs:
            unsupported.append(f"absolute image URL ({s})")

    lines = []
    status = "PASS" if not unsupported else "FAIL"
    lines.append(status)
    lines.append("")
    if unsupported:
        lines.append("Unsupported:")
        for u in unsupported:
            lines.append(f"- {u}")
        lines.append("")
    else:
        lines.append("Unsupported:")
        lines.append("(none)")
        lines.append("")

    lines.append("Image paths:")
    if not scanner.img_srcs:
        lines.append("  (no images)")
    elif not abs_imgs:
        lines.append("  OK (all relative -> resolved under static/description/)")
    else:
        lines.append("  FAIL (absolute URLs are dropped by the store)")
    lines.append("")

    lines.append("Bootstrap classes:")
    lines.append("  OK" if scanner.has_bootstrap else "  (none used)")
    lines.append("")
    lines.append("oe_* classes:")
    lines.append("  OK" if scanner.has_oe else "  (none used)")
    lines.append("")

    unknown = scanner.unknown_classes()
    if unknown:
        lines.append("Custom classes (will NOT render on the store):")
        for c in sorted(set(unknown)):
            lines.append(f"- {c}")
        lines.append("")

    return status, "\n".join(lines)


def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    default_rules = os.path.join(here, "sanitizer_rules.yaml")
    parser = argparse.ArgumentParser(
        description="Validate an Odoo Apps Store description HTML file."
    )
    parser.add_argument("file", help="Path to index.html")
    parser.add_argument(
        "--rules",
        default=default_rules,
        help="Path to sanitizer_rules.yaml (default: alongside this script)",
    )
    args = parser.parse_args(argv)

    if not os.path.exists(args.file):
        sys.stderr.write(f"ERROR: file not found: {args.file}\n")
        return 2

    rules = load_rules(args.rules)
    status, report = run(args.file, rules)
    print(report)
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
