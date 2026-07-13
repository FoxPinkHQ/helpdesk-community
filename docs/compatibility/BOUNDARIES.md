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
- _No View transforms._ Golden uses legacy `oe_chatter` div and `kanban-box`
  template, both accepted by 18.

**Insight:** the 19→18 gap is nearly empty (only the version bump). Manual
backporting here would have produced an almost byte-identical tree — confirming
the effort belongs in the layer, not per-module edits.

## 18.0 → 17.0  (the heavy boundary)
- **R-MANIFEST-001** — version → `17.0.*`
- **R-VIEW-001** — `<list>` → `<tree>`; `view_mode` `list` → `tree`
- **R-VIEW-002** — kanban `<card>` → `<div class="oe_kanban_card">`
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
- **R-ASSET-001** — n/a here (no OWL); would fire for asset-bearing modules

## Summary — rule firing count per target (post-verification)

| Target | Rules firing (this module)                                  |
| ------ | ----------------------------------------------------------- |
| 18.0   | R-MANIFEST-001                                              |
| 17.0   | R-MANIFEST-001, R-VIEW-001, R-VIEW-002, R-ORM-002           |
| 16.0   | same as 17.0                                                |
| 15.0   | same as 17.0                                                |
| 14.0   | same as 17.0 (+ R-ASSET-001 for future asset-bearing modules)|

All firing rules are now **Verified** (source-proven). None are **Stable** yet —
Stable requires a Docker green run per series.

## Next actions before promoting `Verified` → `Stable`
1. Re-test golden on Docker 19 (group_expand fix changed the source of truth).
2. Build 18.0 artifact via layer, install on `odoo18` Docker, run 13 tests
   (incl. new `test_13_group_expand_orm_path`).
3. Build 17.0 artifact; confirm R-VIEW-001/002 + R-ORM-002 (4-arg) on Docker 17.
4. Repeat down to 14.0. Only then flip statuses and open the coordinated release.
