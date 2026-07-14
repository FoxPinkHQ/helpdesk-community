#!/usr/bin/env python3
"""Publisher asset acceptance pre-flight for the Odoo Apps Store target.

Complements validator.py (which checks HTML sanitizer compliance). This check
verifies the *assets* the description references actually exist on disk, so the
manual Store preview cannot fail on a missing banner / icon / screenshot.

Usage:
    python acceptance.py <index.html> [--static-dir <path>]

Exit code: 0 = PASS, 1 = FAIL.
"""
import argparse
import os
import sys
from html.parser import HTMLParser


class AssetScanner(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.imgs = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag.lower() == "img":
            self.imgs.append(d.get("src", ""))


def _is_relative(src):
    return src and not src.startswith(("http://", "https://", "//", "data:"))


def run(index_path, static_dir):
    with open(index_path, encoding="utf-8") as fh:
        html = fh.read()
    scanner = AssetScanner()
    scanner.feed(html)

    missing = []
    for src in scanner.imgs:
        if _is_relative(src):
            p = os.path.join(static_dir, src)
            if not os.path.exists(p):
                missing.append(src)

    # icon.png is required by the store manifest, not by index.html; still a
    # hard requirement for the listing to render.
    if not os.path.exists(os.path.join(static_dir, "icon.png")):
        missing.append("icon.png (required by store manifest)")

    lines = []
    status = "PASS" if not missing else "FAIL"
    lines.append(status)
    lines.append("")
    if missing:
        lines.append("Missing assets:")
        for m in missing:
            lines.append(f"- {m}")
        lines.append("")
    else:
        lines.append(
            "Assets: OK (all referenced images present, icon.png present)"
        )
        lines.append("")
    lines.append(
        "Note: Preview PASS and Store PASS are manual checks on apps.odoo.com."
    )
    return status, "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Pre-flight asset check for Odoo Store description."
    )
    parser.add_argument("file", help="Path to index.html")
    parser.add_argument(
        "--static-dir",
        default=None,
        help="static/description dir (default: index.html's directory)",
    )
    args = parser.parse_args()

    if not os.path.exists(args.file):
        sys.stderr.write(f"ERROR: file not found: {args.file}\n")
        return 2

    static_dir = args.static_dir or os.path.dirname(os.path.abspath(args.file))
    status, report = run(args.file, static_dir)
    print(report)
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
