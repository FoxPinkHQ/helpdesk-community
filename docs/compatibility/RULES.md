# FoxPink Compatibility Rules (19.0 golden → 14.0)

> Machine-oriented rule set for the Compatibility Layer. Each rule is a pure,
> reversible transform from the **19.0 golden** representation to a target series.
> The compiler applies rules top-down per pass; a module never hand-codes
> `if target == 17`.

## Rule lifecycle (the compiler only auto-applies `Stable`)

```
Draft  ──evidence──▶  Verified  ──docker green──▶  Stable
```

- **Draft** — hypothesis. Based on reasoning or a single doc/PR reference.
  Compiler must **warn** and require human confirmation before applying.
- **Verified** — proven by primary evidence (Odoo source of the affected series,
  or a reproducible transform diff). Compiler may apply but flags for a Docker run.
- **Stable** — the generated artifact installed + passed tests on that series'
  Docker instance. Compiler applies silently.

## Confidence

`confidence` is an independent 0–100% signal of evidence strength, distinct from
lifecycle (which tracks the *validation pipeline*). A rule can be
`Verified / 100%` (source-proven) yet not `Stable` until Docker confirms it.

## Rule schema
`id · pass · lifecycle · confidence · applies_to · trigger · transform · evidence`

**Provenance** (required once a rule is Docker-validated):
`introduced_in` (engineering milestone) · `verified_in` (source read / Docker
series) · `last_validated` (date). Lets the Compiler pinpoint which milestone a
rule came from when a future Odoo series breaks it.

---

## ManifestPass

### R-MANIFEST-001 — version prefix
- **lifecycle:** Verified · **confidence:** 100%
- **applies_to:** 18.0, 17.0, 16.0, 15.0, 14.0
- **trigger:** `__manifest__.py` key `version` starting with `19.0.`
- **transform:** replace leading `19.0` with the target series
  (`18.0.1.0.0`, …). Keep trailing module semver.
- **evidence:** Odoo module version convention `<series>.<x>.<y>.<z>`.
- **promote-to-stable:** manifest parsed by target Odoo without warning.

---

## TrackingPass (ORM + mail)

### R-ORM-001 — batch create
- **lifecycle:** Verified · **confidence:** 100%
- **applies_to:** none (identity across 14–19)
- **trigger:** `@api.model_create_multi` + `def create(self, vals_list)`
- **transform:** none. `model_create_multi` exists since 13.0.
- **evidence:** decorator present in `odoo/api.py` for every series 14–19.

### R-ORM-002 — group_expand callback signature  ★ VERIFIED, exposed a golden bug
- **lifecycle:** Verified · **confidence:** 100%
- **applies_to:** 17.0, 16.0, 15.0, 14.0  (**note: golden is 3-arg; older needs 4-arg**)
- **golden form (18.0/19.0):** `def _read_group_stage_ids(self, stages, domain)`
- **transform (≤17.0):** append the `order` parameter →
  `def _read_group_stage_ids(self, stages, domain, order)`
- **evidence (primary source, all 6 series read directly):**
  | series | ORM call site | params |
  | ------ | ------------- | ------ |
  | 14.0 | `getattr(self, field.group_expand)(groups, domain, order)` | 4 |
  | 15.0 | `group_expand(self, groups, domain, order)` | 4 |
  | 16.0 | `group_expand(self, groups, domain, order)` | 4 |
  | 17.0 | `group_expand(self, groups, domain, order)` | 4 |
  | 18.0 | `group_expand(self, groups, domain)` | 3 |
  | 19.0 | `group_expand(self, groups, domain)` | 3 |
  Boundary is **18.0** (odoo/odoo#110737 `_read_group` rewrite).
- **golden-bug found:** golden previously declared the 4-arg form, which raises
  `TypeError: missing 1 required positional argument: 'order'` on 18/19 whenever
  kanban groups by `stage_id`. Fixed golden → 3-arg. The 12-test suite missed it
  (no test triggers an empty-group kanban read). **Add a regression test.**
- **promote-to-stable:** kanban grouped-by-stage renders empty columns on Docker
  18 AND on a re-tested Docker 19; 4-arg variant renders on Docker 17/16/15/14.
- **provenance:** introduced_in `19.0.1.0.1` · verified_in source(14–19) +
  Docker 19 (`test_13`) · last_validated 2026-07-13

### R-ORM-003 — aggregator rename
- **lifecycle:** Draft · **confidence:** 80%
- **applies_to:** 17.0, 16.0, 15.0, 14.0 (future modules only)
- **trigger:** Field kwarg `aggregator=...`
- **transform:** rename `aggregator` → `group_operator` for ≤17.
- **evidence:** Odoo 18 ORM changelog — `group_operator` renamed to `aggregator`
  (odoo/odoo#127353). Not yet source-confirmed per series.
- **promote-to-verified:** confirm kwarg name in `odoo/fields.py` for 17 vs 18.

---

## ViewPass

### R-VIEW-001 — list → tree
- **lifecycle:** Verified · **confidence:** 100%
- **applies_to:** 17.0, 16.0, 15.0, 14.0
- **trigger:** `<list …>` root element; `view_mode` containing `list`.
- **transform:** rename `<list>`/`</list>` → `<tree>`/`</tree>` (preserve
  attributes); rewrite `view_mode` token `list` → `tree`.
- **evidence:** `<tree>`→`<list>` landed in 18.0; upstream upgrade script
  `odoo/upgrade_code/17.5-01-tree-to-list.py`.
- **promote-to-stable:** transformed list view renders on Docker 17.

### R-VIEW-002 — kanban card template
- **lifecycle:** Verified · **confidence:** 90%
- **applies_to:** 17.0, 16.0, 15.0, 14.0
- **trigger:** `<card …>` element inside `<templates>`; template name `card`/`kanban-card`.
- **transform:** for ≤17 replace `<card>` with `<div class="oe_kanban_card">…</div>`
  and set template name to `kanban-box`.
- **evidence:** `kanban-box` deprecated for `kanban-card` in 18.0 (odoo/odoo);
  docs commit renames `kanban-card` → `card` in 19.0.
- **residual 10%:** exact inner-attribute mapping on `<div>` per series unconfirmed.
- **promote-to-stable:** kanban renders on Docker 17.
- **note:** align golden to `t-name="card"` + `<card>` so this stays 1 clean transform.

### R-VIEW-003 — chatter arch
- **lifecycle:** Verified · **confidence:** 100%
- **applies_to:** none (identity 14–19)
- **trigger:** `<div class="oe_chatter">` with follower/activity/message fields.
- **transform:** none. Legacy div accepted (deprecated) down to 14 and up to 19.
- **evidence:** `<chatter/>` introduced 18.0 (odoo/odoo#156463); legacy div retained.

### R-VIEW-004 — kanban font-awesome title
- **lifecycle:** Stable · **confidence:** 100%
- **applies_to:** none (already satisfied in golden)
- **trigger:** `<i class="fa fa-*"/>` inside kanban without `title`.
- **transform:** ensure a `title` attribute exists.
- **evidence:** Odoo 19 kanban accessibility lint; golden 19 installs + tests green.
- **provenance:** introduced_in `19.0.1.0.0` · verified_in Docker 19 ·
  last_validated 2026-07-13

### R-VIEW-005 — `states` attribute (removed in 19)
- **lifecycle:** Draft · **confidence:** 70%
- **applies_to:** documents a 19 golden constraint (older accept it → no reverse)
- **trigger:** field attribute `states="..."`.
- **transform:** golden must not emit `states`; use `invisible` domains.
- **evidence:** `states` removed in 19; not source-confirmed. Not exercised.

### R-VIEW-006 — search `<group expand>` (removed in 19)
- **lifecycle:** Draft · **confidence:** 70%
- **applies_to:** documents a 19 golden constraint (older accept it → no reverse)
- **trigger:** `<group expand="...">` inside `<search>`.
- **transform:** golden must not emit `expand` on search groups.
- **evidence:** removed in 19; not source-confirmed. Not exercised.

### R-VIEW-007 — fully-qualified group xmlids  ★ from F-001
- **lifecycle:** Verified · **confidence:** 100%
- **applies_to:** all series (golden correctness lint, version-independent)
- **trigger:** view node or `<menuitem>` with `groups="name"` where `name` has no
  `module.` prefix and refers to a group defined in this module.
- **transform:** rewrite to `groups="<module>.<name>"`.
- **evidence:** Docker 19 logged `The group "…" defined in view does not exist!`
  for bare names; `ir.ui.view` resolves `groups=` via `ir.model.data`, unlike
  `ir.rule` eval `ref()`. Fix verified: 0 warnings, `test_14` guards it.
- **provenance:** introduced_in `19.0.1.0.1` · verified_in Docker 19 (`test_14`) ·
  last_validated 2026-07-13
- **cross-ref:** FA-003 in `KNOWN_FALSE_ASSUMPTIONS.md`.

---

## SecurityPass (rides ManifestPass ordering)

### R-SEC-001 — res.groups category_id
- **lifecycle:** Verified · **confidence:** 90%
- **applies_to:** none (identity 14–19)
- **trigger:** `<record model="res.groups">` without `category_id`.
- **transform:** none. `category_id` optional on all series.
- **evidence:** golden 19 installs with groups lacking `category_id`; field
  optional 14–18 (documented, not per-series source-read).

---

## ReportPass

### R-REPORT-001 — QWeb report + paperformat
- **lifecycle:** Verified · **confidence:** 85%
- **applies_to:** none (identity 14–19)
- **trigger:** `report` feature; QWeb template + `report_paperformat`.
- **transform:** none structural; manifest data ordering via ManifestPass.
- **evidence:** MCP `analyze_project` reports `ReportPass` with 0 transformed
  fields on all series. Needs a real report render to reach Stable.

---

## AssetPass (future modules with OWL)

### R-ASSET-001 — asset bundle declaration
- **lifecycle:** Draft · **confidence:** 75%
- **applies_to:** 14.0
- **trigger:** manifest `assets` key referencing `web.assets_backend`.
- **transform:** for 14.0 emit `<template inherit_id="web.assets_backend">` XML
  bundle instead of the manifest `assets` dict.
- **evidence:** manifest `assets` key introduced in 15.0. Not exercised by
  helpdesk-community (no OWL); confirm with module #2.
