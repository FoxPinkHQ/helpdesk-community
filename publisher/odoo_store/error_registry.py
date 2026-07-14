#!/usr/bin/env python3
"""Odoogen Error Knowledge Base -- single source of truth loader (the "API").

``docs/errors/*.md`` is the canonical knowledge base. This module is the ONLY
reader: CLI, IDE extension, MCP tool and the documentation site all consume the
same parsed object, so there is never a second copy to drift.

The structured object every consumer receives:

    {
      "error_code":   "E2002",
      "message":      "Menu `groups` has no readable ACL",
      "meaning":      "...",
      "why":          "...",
      "example":      "...",
      "fix":          "...",
      "severity":     "Error",
      "invariant":    "13 -- Menu Visibility (ADR-013)",
      "documentation":"E2002"
    }

MCP / IDE contract: return this object verbatim. ``documentation`` is the
Markdown key; ``message`` is the one-line summary; ``error_code`` is the stable
key. Never return only free text -- always the structured object.

Schema per error file (six sections, all required except where noted):
    ## Meaning
    ## Why
    ## Example
    ## How to fix
    ## Severity      (Error | Warning)
    ## Invariant     (e.g. "13 -- Menu Visibility (ADR-013)" or "None")

Usage:
    python error_registry.py E2002            # human text
    python error_registry.py E2002 --json     # structured object (MCP/IDE)
    python error_registry.py list             # list all known codes

Exit code: 0 = found, 1 = not found. Stdlib only (py2/py3).
"""
import os
import sys


def _repo_root():
    # publisher/odoo_store/error_registry.py -> repo root
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(here))


def _errors_dir(base=None):
    if base:
        return base
    return os.path.join(_repo_root(), "docs", "errors")


def _parse(path):
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    title = ""
    sections = {}
    cur = None
    buf = []
    for ln in lines:
        if ln.startswith("# ") and not title:
            title = ln[2:].strip()
            continue
        if ln.startswith("## "):
            if cur is not None:
                sections[cur] = "\n".join(buf).strip()
            cur = ln[3:].strip()
            buf = []
            continue
        if cur is not None:
            buf.append(ln)
    if cur is not None:
        sections[cur] = "\n".join(buf).strip()

    # message = the part of the title after the first " -- " or em-dash
    message = title.replace("\u2014", " -- ")
    if " -- " in message:
        message = message.split(" -- ", 1)[1].strip()
    message = message.replace("`", "")
    return {
        "title": title,
        "message": message,
        "meaning": sections.get("Meaning", ""),
        "why": sections.get("Why", ""),
        "example": sections.get("Example", ""),
        "fix": sections.get("How to fix", sections.get("How to fix", "")),
        "severity": sections.get("Severity", "Error"),
        "invariant": sections.get("Invariant", "None"),
    }


def get_error_info(code, base=None):
    """Return the structured error object, or None if unknown."""
    code = code.upper()
    path = os.path.join(_errors_dir(base), "%s.md" % code)
    if not os.path.exists(path):
        return None
    data = _parse(path)
    data["error_code"] = code
    data["documentation"] = code
    return data


def list_codes(base=None):
    d = _errors_dir(base)
    if not os.path.isdir(d):
        return []
    out = []
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".md") and fn != "README.md":
            out.append(fn[:-3].upper())
    return out


def _to_text(obj):
    lines = []
    lines.append("Compiler error %s" % obj["error_code"])
    lines.append("")
    lines.append(obj["message"])
    lines.append("")
    lines.append("Severity : %s" % obj["severity"])
    lines.append("Invariant: %s" % obj["invariant"])
    lines.append("")
    for key, label in (("meaning", "Meaning"), ("why", "Why"),
                       ("example", "Example"), ("fix", "How to fix")):
        if obj[key]:
            lines.append("%s:" % label)
            lines.append(obj[key])
            lines.append("")
    return "\n".join(lines).rstrip()


def main(argv=None):
    import argparse
    import json
    ap = argparse.ArgumentParser(
        description="Odoogen Error Knowledge Base lookup (get_error_info).")
    ap.add_argument("code", help="error code (e.g. E2002) or 'list'")
    ap.add_argument("--json", action="store_true",
                    help="emit the structured object (MCP/IDE contract)")
    ap.add_argument("--base", default=None, help="override docs/errors dir")
    args = ap.parse_args(argv)

    if args.code.lower() == "list":
        codes = list_codes(args.base)
        if args.json:
            print(json.dumps({"codes": codes}, indent=2))
        else:
            print("Known error codes: %s" % ", ".join(codes))
        return 0

    obj = get_error_info(args.code, args.base)
    if obj is None:
        sys.stderr.write("ERROR: unknown error code: %s\n" % args.code)
        return 1
    if args.json:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
    else:
        print(_to_text(obj))
    return 0


if __name__ == "__main__":
    sys.exit(main())
