# Version Boundary Diffs — helpdesk-community (golden 19.0)

> Result of the "trial backport" done as **rule extraction**, not hand-editing.
> Each boundary lists exactly which rules fire when the Compatibility Layer
> lowers the golden 19.0 by one series. A boundary with only a version bump means
> the golden already sits on the lowest-common-denominator syntax.

## 19.0 → 18.0
- **R-MANIFEST-001** — version `19.0.*` → `18.0.*`
- _No ORM transform._ **VERIFIED** by reading Odoo source: 18.0 and 19.0 both call
  `group_expand(self, groups, domain)` (3 args). Identity — R-ORM-002 does NOT
  fire here.
- _No View transforms._ Golden uses legacy `oe_chatter` div; kanban `t-name="card"`
  is accepted by 18 (`card` preferred, `kanban-box` fallback). Identity — R-VIEW-002
  does NOT fire here (boundary is 18→17).

**Insight:** the 19→18 gap is nearly empty (only the version bump). Manual
backporting here would have produced an almost byte-identical tree — confirming
the effort belongs in the layer, not per-module edits.

## 18.0 → 17.0  (the heavy boundary)
- **R-MANIFEST-001** — version → `17.0.*`
- **R-VIEW-001** — `<list>` → `<tree>`; `view_mode` `list` → `tree`
- **R-VIEW-002** — kanban template name `t-name="card"` → `t-name="kanban-box"`
  (body is plain `<div>`, unchanged). VERIFIED: ≤17 `kanban_arch_parser.js` looks
  up `templateDocs["kanban-box"]` and throws `Missing 'kanban-box' template`
  otherwise; 19 requires `card`; 18 accepts both. Hard error, not cosmetic (F-003).
- **R-ORM-002** — **append `order`** to the `group_expand` callback signature.
  VERIFIED: 17.0 calls `group_expand(self, groups, domain, order)` (4 args);
  18.0 dropped `order`. The boundary is exactly here (odoo/odoo#110737).

**Insight:** this is where most divergence concentrates. Any FoxPink module
supporting ≤17 pays the cost once, in ViewPass + one ORM signature tweak.

## 17.0 → 16.0
- **R-MANIFEST-001** — version → `16.0.*`
- (inherits 17.0 view forms)

## 16.0 → 15.0
- **R-MANIFEST-001** — version → `15.0.*`

## 15.0 → 14.0
- **R-MANIFEST-001** — version → `14.0.*`
- **R-TEST-001** — `common.TransactionCase` → `common.SavepointCase` (class-level
  `cls.env`/`setUpClass` only landed on `SavepointCase` in 14.0). Docker-discovered.
- **R-ASSET-001** — n/a here (no OWL); would fire for asset-bearing modules

## Summary — rule firing count per target (post-verification)

| Target | Rules firing (this module)                                  |
| ------ | ----------------------------------------------------------- |
| 18.0   | R-MANIFEST-001                                              |
| 17.0   | R-MANIFEST-001, R-VIEW-001, R-VIEW-002, R-ORM-002           |
| 16.0   | same as 17.0                                                |
| 15.0   | same as 17.0                                                |
| 14.0   | same as 17.0 + R-TEST-001 (+ R-ASSET-001 for future asset modules)|

All firing rules are now **Stable** — source-proven AND Docker-green (install +
14/14 tests, 0 error) on their target series, re-confirmed on golden `19.0.1.0.2`
(2026-07-13). Boundaries above are frozen for this module.

## Render-smoke follow-up (FA-006)
Install+tests do not render views in a browser. F-003 (kanban), the `view_mode`
view-type change, and the portal ACL gap were only caught by rendering on live 19.
Browser render smoke is done on **19** (screenshot capture) and pending backfill on
**14–18** before those series can be called render-green (they are install+test-green).
