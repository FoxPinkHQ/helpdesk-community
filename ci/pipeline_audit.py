#!/usr/bin/env python3
"""FoxPink Pipeline Audit gate (cross-platform, CI-runnable).

Enforces the consistency invariants of the canonical->series model as a MANDATORY
gate (see docs/publisher/PER_SERIES_REPOSITORY_RULES.md and PIPELINE.md). It reads
committed content straight from git refs, so it validates what is actually pushed,
not a working tree.

Checks:
  MetadataPass  (R4/R5) : per branch, README tokens == branch == manifest version;
                          supported-range preserved; UTF-8 intact.
  ResearchPass          : matrix.json byte-identical across branches; each
                          THIS_BRANCH.md declares its own series and lists exactly
                          the Stable+exercised transforms matrix.json assigns to it.
   CanonicalKnowledge    : the version-independent docs are byte-identical everywhere.
   CompilerInvariant  (13): canonical module has no orphan menu (Menu->Action->Model
                           must have a readable ACL for a visible group).

Exit code 0 = PASS, 1 = FAIL (drift). No third-party deps.

Usage:  python ci/pipeline_audit.py [--ref-prefix origin/]
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys

CANON = "19.0"
MODULE = "helpdesk_community"
CANONICAL_IDENTICAL = [
    "docs/compatibility/matrix.json",
    "docs/compatibility/RULES.md",
    "docs/compatibility/MATRIX.md",
    "docs/publisher/PER_SERIES_REPOSITORY_RULES.md",
    "docs/publisher/PIPELINE.md",
    "ci/pipeline_audit.py",
    ".github/workflows/pipeline.yml",
]
REPL = "\ufffd"  # UTF-8 replacement char => corruption marker


def git_show(ref: str, path: str) -> str:
    out = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    ).stdout
    return out.decode("utf-8", errors="replace")


def blob_hash(ref: str, path: str) -> str:
    return subprocess.run(
        ["git", "rev-parse", f"{ref}:{path}"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    ).stdout.decode().strip()


def rx(pattern: str, text: str) -> str:
    m = re.search(pattern, text)
    return m.group(1) if m else ""


class Audit:
    def __init__(self, ref_prefix: str):
        self.rp = ref_prefix
        self.failures: list[str] = []
        self.matrix = json.loads(git_show(self.ref(CANON), "docs/compatibility/matrix.json"))
        self.series = self.matrix["series_all"]
        self.tail = re.sub(rf"^{re.escape(CANON)}\.", "", self._canon_version())

    def ref(self, s: str) -> str:
        return f"{self.rp}{s}"

    def _canon_version(self) -> str:
        man = git_show(self.ref(CANON), f"{MODULE}/__manifest__.py")
        return rx(r"'version'\s*:\s*'([\d.]+)'", man)

    def fail(self, msg: str) -> None:
        self.failures.append(msg)

    def expected_transforms(self, s: str) -> list[str]:
        return [
            r["id"] for r in self.matrix["rules"]
            if r["kind"] == "transform" and r["lifecycle"] == "Stable"
            and r["exercised"] and s in r["applies_to"]
        ]

    # ---- MetadataPass (R4/R5) ------------------------------------------------
    def audit_metadata(self) -> None:
        print("== MetadataPass (R4/R5) ==")
        for s in self.series:
            rd = git_show(self.ref(s), "README.md")
            man = git_show(self.ref(s), f"{MODULE}/__manifest__.py")
            exp = f"{s}.{self.tail}"
            got = {
                "tag": rx(r"for \*\*Odoo (\d+\.0)\*\*", rd),
                "clone": rx(r"git clone -b (\d+\.0) ", rd),
                "build": rx(r"This build:\*\* Odoo (\d+\.0) ", rd),
                "ver": rx(r"\*\*Version:\*\* (\d+\.0\.[\d.]+) ", rd),
                "latest": rx(r"Latest: \*\*(\d+\.0\.[\d.]+)\*\*", rd),
                "manifest": rx(r"'version'\s*:\s*'([\d.]+)'", man),
            }
            problems = []
            for k in ("tag", "clone", "build"):
                if got[k] != s:
                    problems.append(f"{k}={got[k]!r}!={s}")
            for k in ("ver", "latest", "manifest"):
                if got[k] != exp:
                    problems.append(f"{k}={got[k]!r}!={exp}")
            if "14.0, 15.0, 16.0, 17.0, 18.0, 19.0" not in rd:
                problems.append("supported-range missing")
            if REPL in rd:
                problems.append("UTF-8 corruption")
            self._line(s, problems)

    # ---- ResearchPass --------------------------------------------------------
    def audit_research(self) -> None:
        print("== ResearchPass ==")
        for s in self.series:
            tb = git_show(self.ref(s), "docs/compatibility/THIS_BRANCH.md")
            cur = rx(r"\*\*Current branch:\*\* (\d+\.0)", tb)
            exp_ids = self.expected_transforms(s)
            problems = []
            if cur != s:
                problems.append(f"current={cur!r}!={s}")
            if s == CANON:
                if "Back-transforms applied for" in tb:
                    problems.append("canonical must have no back-transforms")
            else:
                joined = ", ".join(exp_ids)
                if joined and joined not in tb:
                    problems.append(f"transforms not listed: [{joined}]")
            self._line(s, problems, extra=f"transforms=[{', '.join(exp_ids)}]")
        # matrix.json byte-identical
        hashes = {blob_hash(self.ref(s), "docs/compatibility/matrix.json") for s in self.series}
        ok = len(hashes) == 1
        print(f"  [{'PASS' if ok else 'FAIL'}] matrix.json unique blobs across branches: {len(hashes)}")
        if not ok:
            self.fail("matrix.json not byte-identical across branches")

    # ---- Canonical knowledge identical --------------------------------------
    def audit_canonical(self) -> None:
        print("== CanonicalKnowledge (byte-identical) ==")
        for path in CANONICAL_IDENTICAL:
            try:
                hashes = {blob_hash(self.ref(s), path) for s in self.series}
            except subprocess.CalledProcessError:
                print(f"  [FAIL] {path}: missing on some branch")
                self.fail(f"{path} missing on some branch")
                continue
            ok = len(hashes) == 1
            print(f"  [{'PASS' if ok else 'FAIL'}] {path}: unique={len(hashes)}")
            if not ok:
                self.fail(f"{path} not byte-identical (unique={len(hashes)})")

    # ---- Compiler Invariant 13 (Menu -> Action -> Model -> ACL) ------------
    def audit_compiler_invariant(self) -> None:
        print("== CompilerInvariant (Invariant 13: Menu->Action->Model->ACL) ==")
        here = os.path.dirname(os.path.abspath(__file__))
        repo = os.path.dirname(here)
        validator = os.path.join(repo, "publisher", "odoo_store",
                                 "module_consistency_validator.py")
        module_dir = os.path.join(repo, MODULE)
        if not os.path.exists(validator):
            print("  [SKIP] module_consistency_validator.py not present")
            return
        spec = importlib.util.spec_from_file_location("mcv", validator)
        mcv = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mcv)
        code, report = mcv.run(module_dir)
        print(report)
        if code != 0:
            self.fail("Invariant 13 (Menu->Action->Model->ACL) FAILED on "
                      "canonical module: orphan menu(s) detected")

    def _line(self, s: str, problems: list[str], extra: str = "") -> None:
        ok = not problems
        detail = extra if ok else "; ".join(problems)
        print(f"  [{'PASS' if ok else 'FAIL'}] {s}: {detail}")
        if not ok:
            self.fail(f"{s}: {'; '.join(problems)}")

    def run(self) -> int:
        print(f"FoxPink Pipeline Audit  canonical={CANON} tail={self.tail} refs={self.rp}*\n")
        self.audit_metadata()
        print()
        self.audit_research()
        print()
        self.audit_canonical()
        print()
        self.audit_compiler_invariant()
        print()
        if self.failures:
            print(f"PIPELINE AUDIT: FAIL ({len(self.failures)} issue(s))")
            for f in self.failures:
                print(f"  - {f}")
            return 1
        print("PIPELINE AUDIT: PASS")
        return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref-prefix", default="origin/",
                    help="git ref prefix for the series refs (default: origin/)")
    args = ap.parse_args()
    return Audit(args.ref_prefix).run()


if __name__ == "__main__":
    sys.exit(main())
