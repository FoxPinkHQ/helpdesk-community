#!/usr/bin/env python3
"""Compiler-invariance check: Menu -> Action -> Model -> ACL (Invariant 13).

This is the **Compiler Validator** pass for the *Build* stage of the FoxPink
pipeline. It runs on the generated module code (after PackageIR) and BEFORE the
Install Harness, so an orphan menu is caught statically instead of only at
runtime install.

Invariant 13 (see docs/adr/013-menu-visibility-invariant.md):

    If the Compiler emits a Menu that points (via an Action) to a Model,
    then at least one readable ACL (perm_read=1) MUST exist for a group that
    can actually see the menu. Otherwise the menu is invisible to everyone and
    the module ships a dead entry point.

Odoo filters ``ir.ui.menu`` entries by the read right on the action's
``res_model``. A menu with an action but no readable ACL for any visible group
is silently dropped from the UI -- install succeeds, tests pass, but the
feature is gone.

Checks performed:
    E2001  Menu "X" -> model "m" has NO readable ACL for ANY group.
           The menu is invisible to the whole instance.
    E2002  Menu "X" -> model "m": none of the menu's ``groups`` has a readable
           ACL. The intended audience can never open it.
    E2003  Menu "X" action "a" cannot be resolved to a res_model
           (missing action / wrong ref). Cannot verify -> flag.

Usage:
    python module_consistency_validator.py <module_dir>

Exit code: 0 = PASS, 1 = FAIL. Stdlib only (CI-friendly, py2/py3).
"""
import csv
import os
import sys
import xml.etree.ElementTree as ET

# base.group_system implies base.group_user in Odoo; treat it as covered when
# the user group already has a readable ACL on the model.
SYSTEM_IMPLIES_USER = True


def _iter_xml_files(module_dir):
    for root, _dirs, files in os.walk(module_dir):
        for fn in files:
            if fn.endswith(".xml"):
                yield os.path.join(root, fn)


def _field_text_or_ref(elem):
    """Return (text, ref) for an <field> element."""
    ref = elem.attrib.get("ref")
    text = (elem.text or "").strip()
    return text, ref


def _split_xmlids(s):
    if not s:
        return []
    return [x.strip() for x in s.split(",") if x.strip()]


def _collect_menus_and_actions(module_dir):
    menus = []          # (xmlid, name, action_ref, [group_xmlids])
    actions = {}        # xmlid -> res_model (or None)
    for path in _iter_xml_files(module_dir):
        try:
            tree = ET.parse(path)
        except ET.ParseError as exc:
            sys.stderr.write("WARNING: cannot parse %s: %s\n" % (path, exc))
            continue
        root = tree.getroot()
        for el in root.iter():
            tag = el.tag
            # ---- menuitem shortcut -------------------------------------------
            if tag == "menuitem":
                xmlid = el.attrib.get("id")
                if not xmlid:
                    continue
                name = el.attrib.get("name", xmlid)
                action_ref = el.attrib.get("action")
                groups = _split_xmlids(el.attrib.get("groups"))
                if action_ref:
                    menus.append((xmlid, name, action_ref, groups))
                continue
            # ---- <record model="..."> ----------------------------------------
            if tag == "record":
                model = el.attrib.get("model")
                xmlid = el.attrib.get("id")
                if not xmlid:
                    continue
                if model == "ir.ui.menu":
                    name = xmlid
                    action_ref = None
                    groups = []
                    for f in el:
                        if f.tag != "field":
                            continue
                        fname = f.attrib.get("name")
                        if fname == "name":
                            name = (f.text or "").strip() or name
                        elif fname == "action":
                            _t, ref = _field_text_or_ref(f)
                            action_ref = ref or _t
                        elif fname == "groups":
                            groups = _split_xmlids((f.text or "").strip())
                    if action_ref:
                        menus.append((xmlid, name, action_ref, groups))
                elif model in (
                    "ir.actions.act_window",
                    "ir.actions.server",
                    "ir.actions.report",
                    "ir.actions.act_url",
                ):
                    res_model = None
                    for f in el:
                        if f.tag == "field" and f.attrib.get("name") == "res_model":
                            res_model = (f.text or "").strip() or None
                    actions[xmlid] = res_model
            # ---- act_window / act_url / act_server shortcuts -----------------
            elif tag in ("act_window", "act_url", "act_server"):
                xmlid = el.attrib.get("id")
                if xmlid:
                    actions[xmlid] = el.attrib.get("res_model")
    return menus, actions


def _collect_acls(module_dir):
    """Return dict: model -> set(group_xmlid with perm_read=1)."""
    acl_path = os.path.join(module_dir, "security", "ir.model.access.csv")
    out = {}
    if not os.path.exists(acl_path):
        return out
    with open(acl_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            model = (row.get("model_id:id") or "").strip()
            if model.startswith("model_"):
                # Odoo model xmlid "model_helpdesk_ticket" -> "helpdesk.ticket"
                model = model[len("model_"):].replace("_", ".")
            group = (row.get("group_id:id") or "").strip()
            read = (row.get("perm_read") or "0").strip()
            if read not in ("1", "True", "true"):
                continue
            out.setdefault(model, set()).add(group)
    return out


def run(module_dir):
    if not os.path.isdir(module_dir):
        sys.stderr.write("ERROR: not a directory: %s\n" % module_dir)
        return 2, ""
    menus, actions = _collect_menus_and_actions(module_dir)
    acls = _collect_acls(module_dir)

    lines = []
    errors = []
    lines.append("Menu -> Action -> Model -> ACL (Invariant 13)")
    lines.append("")
    lines.append("menus with action: %d  actions: %d  models with read ACL: %d"
                 % (len(menus), len(actions), len(acls)))
    lines.append("")

    for xmlid, name, action_ref, groups in menus:
        res_model = actions.get(action_ref)
        if res_model is None:
            # Action may be a server action with no res_model, or unresolved.
            if action_ref not in actions:
                msg = ("E2003 Menu \"%s\" (%s) -> action \"%s\" not resolvable "
                       "to a res_model." % (name, xmlid, action_ref))
                errors.append(msg)
                lines.append("  [FAIL] %s" % msg)
            continue

        readers = set(acls.get(res_model, set()))
        if SYSTEM_IMPLIES_USER and "base.group_user" in readers:
            readers.add("base.group_system")

        if not readers:
            msg = ("E2001 Menu \"%s\" (%s) points to model \"%s\" but NO group "
                   "has a readable ACL. Menu is invisible to everyone."
                   % (name, xmlid, res_model))
            errors.append(msg)
            lines.append("  [FAIL] %s" % msg)
            lines.append("         Suggestion: grant read access to "
                         "base.group_user (or another visible group).")
            continue

        if groups:
            visible = set(groups)
            if SYSTEM_IMPLIES_USER and "base.group_system" in visible:
                visible.add("base.group_user")
            if not (visible & readers):
                msg = ("E2002 Menu \"%s\" (%s) -> model \"%s\": none of its "
                       "groups (%s) has a readable ACL."
                       % (name, xmlid, res_model, ", ".join(groups)))
                errors.append(msg)
                lines.append("  [FAIL] %s" % msg)
                lines.append("         Suggestion: grant read access to one of "
                             "the menu's groups, or base.group_user.")
                continue
        lines.append("  [PASS] %s (%s) -> %s (readers: %d)"
                     % (name, xmlid, res_model, len(readers)))

    lines.append("")
    status = "PASS" if not errors else "FAIL"
    lines.append("Invariant 13: %s (%d error(s))" % (status, len(errors)))
    return (0 if status == "PASS" else 1), "\n".join(lines)


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(
        description="Compiler Validator: Invariant 13 (Menu->Action->Model->ACL).")
    ap.add_argument("module_dir", help="Path to the Odoo module directory")
    args = ap.parse_args(argv)
    code, report = run(args.module_dir)
    print(report)
    return code


if __name__ == "__main__":
    sys.exit(main())
