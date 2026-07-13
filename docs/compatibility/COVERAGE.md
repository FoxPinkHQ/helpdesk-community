# Compatibility Layer — Rule Coverage KPI

> The health metric of the Compatibility Layer. Two independent ratios per pass:
> - **Evidence coverage** = `(Stable + Verified) / total` — how much is proven.
> - **Stable coverage** = `Stable / total` — how much the compiler may auto-apply
>   silently. **Release gate uses Stable coverage.**
>
> A rule is only `Stable` after the generated artifact installs + passes tests on
> that series' Docker instance. `Verified` means source-proven but not yet
> Docker-confirmed.

## Snapshot (helpdesk-community, post-Docker 14–19)

| Pass         | Total | Stable | Verified | Draft | Evidence | Stable |
| ------------ | ----- | ------ | -------- | ----- | -------- | ------ |
| ManifestPass | 1     | 1      | 0        | 0     | 100%     | 100%   |
| TrackingPass | 3     | 2      | 1        | 0     | 100%     | 67%    |
| ViewPass     | 8     | 5      | 2        | 1     | 88%      | 63%    |
| SecurityPass | 1     | 1      | 0        | 0     | 100%     | 100%   |
| ReportPass   | 1     | 1      | 0        | 0     | 100%     | 100%   |
| AssetPass    | 1     | 0      | 1        | 0     | 100%     | 0%     |
| TestPass     | 1     | 1      | 0        | 0     | 100%     | 100%   |
| **TOTAL**    | **16**| **11** | **4**    | **1** | **94%**  | **69%**|

## Reading the snapshot

- **94% evidence · 69% Stable** — the whole golden was compiled to 18→14 through
  the layer and **installed + passed 14/14 tests on all six series** (see log).
- **Every rule *exercised* by this module is now Stable** (Manifest, Tracking
  R-ORM-001/002, View R-VIEW-001/002/003/004/007, Security, Report, Test). The
  4 non-Stable rules are **not exercised** by helpdesk-community:
  - R-ORM-003 (aggregator), R-ASSET-001 (assets) — Verified, need an exercising
    module + Docker → Stable.
  - R-VIEW-005 (states), R-VIEW-006 (group expand) — Verified golden-lints;
    nothing to run.
  - R-VIEW-008 (attrs↔invisible) — Draft (Unknown), transform unmapped.
- **Market gate result:** for this module's exercised rule set, **Stable coverage
  = 100% across 14–19**. Install + Tests columns of the ADR-001 DoD are green;
  Package/screenshots/CI remain before an actual Market Release.

## Compiler safety KPIs (correctness, not just coverage)

Coverage answers "how much do we know". These answer "can we trust auto-apply".
The Compiler must optimise for **being right or silent, never wrong**.

| KPI | Target | Meaning | Current |
| --- | ------ | ------- | ------- |
| **False Positive** | **0** | a rule auto-applied where it should not fire (wrong transform emitted) | 0 known |
| **False Negative** | low | a needed rule missed → *golden ships unchanged*, not miscompiled | 1 known gap: R-VIEW-008 (flagged, not silent) |
| **Unknown > Wrong** | always | when unsure, Compiler emits "Unknown" (Draft/warn + human confirm) instead of guessing | enforced: only `Stable` auto-applies; `Draft` warns |

Governing principle: a **False Positive is a release blocker**; a **False
Negative that leaves the golden untouched is tolerable** (the module may not build
for that series, but it never ships *wrong* code). FA-005 is the cautionary tale —
a wrong boundary (states "removed in 19") would have been a False Positive on
17/18; it was caught by source verification before any artifact was generated.

## Path to release (Stable → 100% for exercised passes)

The exercised passes for this module are Manifest, Tracking, View, Security,
Report (Asset is n/a). To publish, each must reach **Stable = 100%** for the
rules it actually fires:

1. Build the 6 artifacts through the layer.
2. Docker-install each series; run the test suite (incl. the new group_expand
   regression test).
3. Flip `Verified → Stable` per rule as each series goes green.
4. Recompute this table. Release only when Stable coverage of exercised passes
   = 100% across all 6 series (ADR-001 coordinated gate).

## Docker verification log (per-series)

| Rule / event                    | 19 | 18 | 17 | 16 | 15 | 14 |
| ------------------------------- | -- | -- | -- | -- | -- | -- |
| Golden install + 14 tests green | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R-ORM-002 (group_expand)        | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| F-001 (view groups= resolves)   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R-VIEW-001 (list→tree)          | =  | =  | ✅ | ✅ | ✅ | ✅ |
| R-VIEW-002 (t-name card→box)    | ✅ | =  | ✅ | ✅ | ✅ | ✅ |
| R-TEST-001 (Savepoint on 14)    | =  | =  | =  | =  | =  | ✅ |
| Render smoke (kanban/list/form/portal) | ✅ | ?  | ?  | ?  | ?  | ?  |

**✅ ALL SIX SERIES GREEN (14–19): install + 14/14 tests, 0 error.** (`=` = identity,
rule not required on that series.)

- 2026-07-13: Docker 19 (`test_hd`) — `14 tests, 0 failed, 0 error`, 0 "group does
  not exist" warnings. 3-arg golden signature + F-001 fix confirmed.
- 2026-07-13: Docker **18/17/16/15/14** — each compiled via `build_version.ps1`,
  installed with `-i helpdesk_community --test-enable`: **14 tests, 0 failed,
  0 error** on every series. 17→14 exercise R-ORM-002 (4-arg + `test_12` call-site
  rewrite); 14 additionally exercises **R-TEST-001** (`TransactionCase`→
  `SavepointCase`, discovered here).
- 2026-07-13: Re-validated after the golden bug fixes (F-003, view_mode, portal
  ACL, portal QWeb) on golden **19.0.1.0.2** — Docker **14/15/16/17/18** each
  rebuilt via `build_version.ps1` and `--test-tags=/helpdesk_community`: **0 failed,
  0 error(s) of 14 tests** on every series. R-VIEW-002 rename (card→kanban-box)
  confirmed on 17/16/15/14; card accepted as-is on 18.
- Golden = **19.0.1.0.2** (Engineering release). Phase 1.5 Docker validation +
  Phase 2A golden bug fixes complete → exercised rules re-confirmed **Stable**.
- **F-003 (was mislabeled "non-blocking" — actually a HARD render error):** golden
  kanban used `t-name="kanban-box"`, which throws OwlError `Missing 'card' template`
  on 19 → kanban does not render. Fixed golden → `t-name="card"`; compiler renames
  to `kanban-box` for ≤17 (R-VIEW-002, boundary <18). **Only caught by browser
  render, not by tests — see FA-006.** Also fixed same round: `view_mode
  tree,form`→`list,form` (×3 actions, tree view type removed on 19) and 3 missing
  `base.group_portal` ACLs (portal 403). All render clean on live 19.
- **Render-smoke backfill (14–16, 18):** open follow-up — install+tests are green
  on all 6 series, but browser render smoke is so far only done on 19 (screenshots)
  and Docker-install-confirmed (not browser-rendered) on 14–18. Marked `?` above.

## Open findings (surfaced during verification, NOT compatibility rules)

- **F-001 view groups unresolved** — ✅ FIXED in 19.0.1.0.1. All view/menu
  `groups=` now use `helpdesk_community.group_*`; Docker 19 logs 0 warnings;
  guarded by `test_14`. Recorded as FA-003 in `KNOWN_FALSE_ASSUMPTIONS.md`.
  Version-independent fix — inherited by 18→14 branches when built.
- **F-002 read_group deprecation** — `test_13` uses `read_group` (deprecated in
  19, works 14–19). Portable now; revisit for Odoo 20 (`formatted_read_group`).

## Draft backlog (promote before they can ever be Stable)

| Rule        | Pass     | Status | Blocker to next stage |
| ----------- | -------- | ------ | --------------------- |
| R-ORM-003   | Tracking | ✅ Verified (boundary 18.0) | Docker run on a module using `aggregator` → Stable |
| R-VIEW-005  | View     | ✅ Verified (boundary 17.0, corrected) | golden-lint; n/a to Stable pipeline |
| R-VIEW-006  | View     | ✅ Verified (boundary 19.0) | golden-lint; n/a to Stable pipeline |
| R-ASSET-001 | Asset    | ✅ Verified (boundary 15.0) | Docker 14 render of an OWL module → Stable |
| R-VIEW-008  | View     | ⚠ Draft (Unknown) | map 17+ modifier expr → ≤16 `attrs`, diff on a real module |

**Exercised-rule Stable coverage = 100% across 14–19.** The 4 non-Stable rules
above are not exercised by helpdesk-community (no `aggregator`, no OWL assets, no
`states`/dynamic-modifier views); they need an exercising module to reach Stable.

All 2026-07-13 verifications used primary source grepped inside the official
`odoo:14.0`–`odoo:19.0` images. Evidence Packs: `evidence/<RULE>/`.
