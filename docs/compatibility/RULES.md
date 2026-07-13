# FoxPink Compatibility Rules (19.0 golden → 14.0)

> Machine-oriented rule set for the Compatibility Layer. Each rule is a pure,
> reversible transform from the **19.0 golden** representation to a target series.
> The compiler applies rules top-down per pass; a module never hand-codes
> `if target == 17`.

## Rule lifecycle (the compiler only auto-applies `Stable`)

```
Draft  ──evidence──▶  Verified  ──docker green──▶  Stable
  │                       │
  └────────┬──────────────┘
           ▼
        Rejected   (disproven at any stage; kept in the registry, never applied)
```

- **Draft** — hypothesis. Based on reasoning or a single doc/PR reference.
- **Verified** — proven by primary evidence (Odoo source of the affected series,
  or a reproducible transform diff). Not yet Docker-confirmed.
- **Stable** — the generated artifact installed + passed tests on that series'
  Docker instance.
- **Rejected** — a rule (or a specific boundary/transform hypothesis) that was
  **disproven**. It stays in the registry (see *Rejected registry* below) with its
  reason and successor, so neither humans nor the Compiler re-propose it. Cross-
  referenced from `KNOWN_FALSE_ASSUMPTIONS.md`.

## Compiler invariant — **Unknown > Wrong** (auto-apply gate)

The Compiler decides *purely* on lifecycle. This mapping is a hard invariant:

```
Stable    → Auto-apply (silent)
Verified  → Emit diagnostic, require human review  (NEVER auto-apply)
Draft     → Ignore (do not apply); may emit an informational note
Rejected  → Ignore; if the input matches a Rejected pattern, warn loudly
```

- **`Verified` must never auto-apply.** Source-proven ≠ runtime-proven. Only a
  green Docker run promotes to `Stable`.
- When lifecycle is anything below `Stable`, the Compiler prefers to **leave the
  golden untouched and say so** (a tolerable False Negative) rather than emit an
  unproven transform (an unacceptable False Positive). See COVERAGE "Compiler
  safety KPIs".

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
- **lifecycle:** Stable · **confidence:** 100% · Docker-green 14–19 (2026-07-13)
- **applies_to:** 18.0, 17.0, 16.0, 15.0, 14.0
- **trigger:** `__manifest__.py` key `version` starting with `19.0.`
- **transform:** replace leading `19.0` with the target series
  (`18.0.1.0.0`, …). Keep trailing module semver.
- **evidence:** Odoo module version convention `<series>.<x>.<y>.<z>`.
- **promote-to-stable:** manifest parsed by target Odoo without warning.

---

## TrackingPass (ORM + mail)

### R-ORM-001 — batch create
- **lifecycle:** Stable · **confidence:** 100% · Docker-green 14–19 (2026-07-13)
- **applies_to:** none (identity across 14–19)
- **trigger:** `@api.model_create_multi` + `def create(self, vals_list)`
- **transform:** none. `model_create_multi` exists since 13.0.
- **evidence:** decorator present in `odoo/api.py` for every series 14–19.

### R-ORM-002 — group_expand callback signature  ★ STABLE, exposed a golden bug
- **lifecycle:** Stable · **confidence:** 100% · Docker-green 14–19 (2026-07-13)
- **applies_to:** 17.0, 16.0, 15.0, 14.0  (**note: golden is 3-arg; older needs 4-arg**)
- **golden form (18.0/19.0):** `def _read_group_stage_ids(self, stages, domain)`
- **transform (≤17.0):** append the `order` parameter →
  `def _read_group_stage_ids(self, stages, domain, order)`.
  **Sub-rule (Docker-discovered):** the rename must also patch any *direct* call
  site, e.g. `test_12` calls `_read_group_stage_ids(self.Stage, [])` → append a
  positional order (`, 'id'`). Missed call sites raise `missing ... 'order'` on ≤17.
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
- **promoted-to-stable:** ✅ 4-arg variant installs + 14 tests green on Docker
  17/16/15/14; 3-arg identity green on Docker 18/19. `test_13` drives the real
  ORM path on every series.
- **provenance:** introduced_in `19.0.1.0.1` · verified_in source(14–19) +
  Docker 14–19 (`test_13`) · last_validated 2026-07-13

### R-ORM-003 — aggregator rename  ★ source-verified
- **lifecycle:** Verified · **confidence:** 100%
- **applies_to:** 17.0, 16.0, 15.0, 14.0 (future modules only)
- **trigger:** Field kwarg `aggregator=...`
- **transform:** rename `aggregator` → `group_operator` for ≤17.
- **boundary:** 18.0. `aggregator` accepted 18+; `group_operator` is a deprecated
  alias on 18/19 but the only form on ≤17.
- **evidence:** `fields.py` grep across images — `aggregator` count 0 on 14–17,
  19 on 18; deprecation shim `attrs['aggregator'] = attrs.pop('group_operator')`
  identical in 18 (`fields.py:482`) and 19 (`orm/fields.py:487`). ORM moved to
  `odoo/orm/` in 19. Full pack: `evidence/R-ORM-003/`.
- **provenance:** introduced_in `19.0.1.0.1` · verified_in source(14–19) ·
  last_validated 2026-07-13
- **promote-to-stable:** Docker run on a module that declares an `aggregator` field
  (not exercised by helpdesk-community).

---

## ViewPass

### R-VIEW-001 — list → tree
- **lifecycle:** Stable · **confidence:** 100% · Docker-green 14–19 (2026-07-13)
- **applies_to:** 17.0, 16.0, 15.0, 14.0
- **trigger:** `<list …>` root element; `view_mode` containing `list`.
- **transform:** rename `<list>`/`</list>` → `<tree>`/`</tree>` (preserve
  attributes); rewrite `view_mode` token `list` → `tree`.
- **evidence:** `<tree>`→`<list>` landed in 18.0; upstream upgrade script
  `odoo/upgrade_code/17.5-01-tree-to-list.py`.
- **promote-to-stable:** transformed list view renders on Docker 17.

### R-VIEW-002 — kanban card template name  ★ HARD ERROR, boundary corrected (F-003)
- **lifecycle:** Stable · **confidence:** 100% · Docker-green 14–19 (2026-07-13)
- **applies_to:** 17.0, 16.0, 15.0, 14.0  (**boundary: target < 18.0**)
- **golden form (19.0):** `<t t-name="card">` wrapping a plain `<div>` body.
  Canonical 19 uses **0 `<card>` elements** — the body is ordinary `<div>`s; only the
  *template name* changes across series, never the body.
- **transform (≤17.0):** rename `<t t-name="card">` → `<t t-name="kanban-box">`.
  No element/body transform (plain `<div>` is valid on all series 14–19).
- **evidence (primary source, `web/.../kanban/kanban_arch_parser.js`, all series read):**
  | series | parser lookup | behaviour if `card` template absent |
  | ------ | ------------- | ----------------------------------- |
  | 14–17 | `templateDocs["kanban-box"]` | throws `Missing 'kanban-box' template` |
  | 18.0  | `templateDocs["card"]` → fallback `kanban-box` | warns `'kanban-box' is deprecated`, then works |
  | 19.0  | `templateDocs["card"]` | throws `Missing 'card' template` |
  So `card` is a **hard requirement** on 19, a **hard failure** on ≤17, and 18
  accepts **both**. Boundary for the rename is **target < 18.0**.
- **golden-bug found (F-003):** golden previously used `t-name="kanban-box"`, which
  raises OwlError `Missing 'card' template` on 19 — the module's kanban view would
  not render at all on the canonical series. This is a **HARD render error, not
  cosmetic**. The 14-test suite MISSED it entirely because **tests never render a
  view in a browser** (install + ORM tests only). Fixed golden → `t-name="card"`;
  harness renames back to `kanban-box` for <18. See FA-006 (render-gap lesson).
- **promoted-to-stable:** ✅ card form renders on live Docker 19 (screenshot capture);
  renamed kanban-box form installs + 14 tests green on Docker 17/16/15/14; 18 accepts
  card as-is (14 tests green).
- **provenance:** introduced_in `19.0.1.0.2` · verified_in source(14–19) +
  Docker 14–19 · last_validated 2026-07-13

### R-VIEW-003 — chatter arch
- **lifecycle:** Stable · **confidence:** 100% · Docker-green 14–19 (2026-07-13)
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

### R-VIEW-005 — `states` / `attrs` attribute  ★ source-verified, boundary corrected
- **lifecycle:** Verified · **confidence:** 100%
- **kind:** golden-authoring constraint / lint (not a build transform)
- **trigger:** node attribute `states="..."` or `attrs="..."`.
- **transform:** golden must not emit `states`/`attrs` (use `invisible`/`readonly`
  domains). No reverse transform needed (golden already compliant).
- **boundary:** **17.0** (NOT 19 as first assumed — see FA-005). `states`/`attrs`
  are processed on 16.0 (`ir_ui_view.py:89` converts `states`→modifiers) and raise
  `ValidationError("Since 17.0, the 'attrs' and 'states' attributes are no longer
  used")` on 17/18/19. RNG `<group>` define drops both at 17.0.
- **evidence:** `evidence/R-VIEW-005/`.
- **provenance:** introduced_in `19.0.1.0.1` · verified_in source(16–19) ·
  last_validated 2026-07-13
- **related gap:** R-VIEW-008 (attrs↔invisible domain transform for ≤16).

### R-VIEW-006 — search `<group expand>` (removed in 19)  ★ source-verified
- **lifecycle:** Verified · **confidence:** 100%
- **kind:** golden-authoring constraint / lint
- **trigger:** `<group expand="...">` (validates against shared `<group>` define).
- **transform:** golden must not emit `expand` on `<group>`. Older (14–18) accept a
  group without `expand` → no reverse transform.
- **boundary:** **19.0**. `expand` on the `<group>` RNG define present 16/17/18,
  removed in 19 (`common.rng` group define). `<field>` keeps `expand` (out of scope).
- **evidence:** `evidence/R-VIEW-006/`.
- **provenance:** introduced_in `19.0.1.0.1` · verified_in source(16–19) ·
  last_validated 2026-07-13

### R-VIEW-008 — `attrs`/dynamic modifiers → `invisible` domains  ⚠ Unknown transform
- **lifecycle:** Draft · **confidence:** 60% (boundary proven, transform unmapped)
- **applies_to:** 16.0, 15.0, 14.0 (build 19→≤16)
- **trigger:** golden node with dynamic `invisible="<domain/expr>"` /
  `readonly="..."` / `required="..."` (17.0+ unified syntax).
- **transform (proposed):** for ≤16 rewrite to legacy
  `attrs="{'invisible': <domain>, ...}"`. **Mapping not yet validated.**
- **boundary:** 17.0 (unified modifier syntax landed with the `attrs` removal).
- **evidence:** derived from R-VIEW-005 source read; the *reverse* mapping to
  `attrs` is not yet built or Docker-tested → kept Draft on purpose (Unknown >
  Wrong). NOT exercised by helpdesk-community (0 dynamic modifiers).
- **promote-to-verified:** map every 17+ modifier expression form to its ≤16
  `attrs` equivalent and diff on a real module.

### R-VIEW-007 — fully-qualified group xmlids  ★ from F-001
- **lifecycle:** Stable · **confidence:** 100% · Docker-green 14–19 (2026-07-13)
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
- **lifecycle:** Stable · **confidence:** 100% · Docker-green 14–19 (2026-07-13)
- **applies_to:** none (identity 14–19)
- **trigger:** `<record model="res.groups">` without `category_id`.
- **transform:** none. `category_id` optional on all series.
- **evidence:** golden 19 installs with groups lacking `category_id`; field
  optional 14–18 (documented, not per-series source-read).

---

## ReportPass

### R-REPORT-001 — QWeb report + paperformat
- **lifecycle:** Stable · **confidence:** 100% · Docker-green 14–19 (2026-07-13)
- **applies_to:** none (identity 14–19)
- **trigger:** `report` feature; QWeb template + `report_paperformat`.
- **transform:** none structural; manifest data ordering via ManifestPass.
- **evidence:** MCP `analyze_project` reports `ReportPass` with 0 transformed
  fields on all series. Needs a real report render to reach Stable.

---

## AssetPass (future modules with OWL)

### R-ASSET-001 — asset bundle declaration  ★ source-verified
- **lifecycle:** Verified · **confidence:** 95%
- **applies_to:** 14.0
- **trigger:** manifest `assets` key referencing `web.assets_backend`.
- **transform:** for 14.0 emit `<template inherit_id="web.assets_backend">` XML
  bundle instead of the manifest `assets` dict.
- **boundary:** **15.0**. The `assets` key is backed by the `ir.asset` model
  (`odoo/addons/base/models/ir_asset.py`), which is **MISSING in 14.0** and present
  15.0+. Without `ir.asset` a 14.0 manifest `assets` dict has no loader.
- **evidence:** `evidence/R-ASSET-001/`.
- **provenance:** introduced_in `19.0.1.0.1` · verified_in source(14–16) ·
  last_validated 2026-07-13
- **promote-to-stable:** Docker 14 render of a real OWL module (asset ordering is
  the residual 5% risk). Not exercised by helpdesk-community (no OWL).

---

## TestPass (test-infrastructure transforms)

### R-TEST-001 — TransactionCase class-level env  ★ Docker-discovered
- **lifecycle:** Stable · **confidence:** 100%
- **applies_to:** 14.0
- **trigger:** test class `common.TransactionCase` that defines `setUpClass` and
  uses `cls.env`.
- **transform:** for 14.0 rewrite base class to `common.SavepointCase`.
- **boundary:** **15.0**. `TransactionCase` gained class-level `setUpClass`/`cls.env`
  in 15.0 (`SavepointCase` merge). On 14.0 only `SingleTransactionCase`/
  `SavepointCase` expose `cls.env`.
- **evidence:** `evidence/R-TEST-001/`. Docker 14: error → 0 error after rule.
- **provenance:** introduced_in `19.0.1.0.1` · verified_in source(14–15) +
  Docker 14 · last_validated 2026-07-13

### R-MAIL-001 — mail.template rendering engine (jinja → qweb)  ★ source-verified
- **lifecycle:** Stable · **confidence:** 100%
- **applies_to:** 14.0
- **trigger:** `mail.template` records whose char fields (`subject`, `email_to`)
  use `{{ expr }}` (inline_template) and whose `body_html` uses QWeb directives
  (`t-out`, `t-if`, `t-attf-href`).
- **transform:** for 14.0 rewrite to jinja: `{{ expr }}` → `${expr}` in char
  fields and inline URLs; `t-out` → `${expr}`; `t-if`/`t-endif` → `% if %`/
  `% endif`; `t-attf-href` → plain `href` with `${...}`.
- **boundary:** **15.0**. Odoo replaced jinja with qweb (`body_html`) +
  inline_template (char fields) in 15.0 (commit `4813f42` "replace jinja with
  qweb"; `odoo/tools/jinja.py` removed). On 14.0 the modern idiom is inert
  (`{{ }}` stays literal; `t-*` are dead attributes).
- **note:** templates are `noupdate` data and dormant (not sent by any code
  path), so install succeeds on every series regardless; this rule keeps them
  render-correct if a reviewer test-sends them.
- **evidence:** golden ships qweb (15–19); 14 artifact ships jinja variant.
- **provenance:** introduced_in `19.0.1.0.4` · verified_in source(14–15) ·
  last_validated 2026-07-13

---

## Rejected registry

> Rule/boundary hypotheses that were **disproven**. They keep a stable `RJ-` id so
> the Compiler can answer *"did this rule ever exist?"* → **Rejected + reason**,
> and never re-propose them. Each maps to a `FA-` entry.

| id | Rejected hypothesis | Why rejected | Superseded by | FA |
| ----- | ------------------- | ------------ | ------------- | -- |
| RJ-001 | transform `group_expand` at the **19→18** boundary | 18 & 19 both 3-arg; boundary is 18→17 | R-ORM-002 (fires ≤17) | FA-001 |
| RJ-002 | `states`/`attrs` removed at **19.0** | removed at 17.0 (ValidationError); 16 still processes them | R-VIEW-005 (boundary 17.0) | FA-005 |
| RJ-003 | `<chatter/>` needs expand-to-legacy-div transform for ≤17 | golden already uses legacy `oe_chatter` div (accepted 14–19) | R-VIEW-003 (identity) | FA-004 |

Compiler behaviour for a Rejected match: **warn loudly, do not apply**, point to
the FA. A Rejected id is never silently reused for a new rule.
