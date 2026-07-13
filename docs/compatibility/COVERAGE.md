# Compatibility Layer — Rule Coverage KPI

> The health metric of the Compatibility Layer. Two independent ratios per pass:
> - **Evidence coverage** = `(Stable + Verified) / total` — how much is proven.
> - **Stable coverage** = `Stable / total` — how much the compiler may auto-apply
>   silently. **Release gate uses Stable coverage.**
>
> A rule is only `Stable` after the generated artifact installs + passes tests on
> that series' Docker instance. `Verified` means source-proven but not yet
> Docker-confirmed.

## Snapshot (helpdesk-community, pre-Docker)

| Pass         | Total | Stable | Verified | Draft | Evidence | Stable |
| ------------ | ----- | ------ | -------- | ----- | -------- | ------ |
| ManifestPass | 1     | 0      | 1        | 0     | 100%     | 0%     |
| TrackingPass | 3     | 0      | 2        | 1     | 67%      | 0%     |
| ViewPass     | 7     | 1      | 4        | 2     | 71%      | 14%    |
| SecurityPass | 1     | 0      | 1        | 0     | 100%     | 0%     |
| ReportPass   | 1     | 0      | 1        | 0     | 100%     | 0%     |
| AssetPass    | 1     | 0      | 0        | 1     | 0%       | 0%     |
| **TOTAL**    | **14**| **1**  | **10**   | **3** | **79%**  | **7%** |

## Reading the snapshot

- **77% evidence** — most rules are already source-proven; the knowledge base is
  no longer just notes.
- **8% Stable** — almost nothing has been Docker-confirmed yet. This is the
  honest gate: **do not release / do not auto-apply** until Stable climbs.
- **AssetPass 0%** — expected; helpdesk-community has no OWL. Will be exercised by
  the first asset-bearing module (module #2).

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
| Golden install + 14 tests green | ✅ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| R-ORM-002 (group_expand)        | ✅ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| F-001 (view groups= resolves)   | ✅ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

- 2026-07-13: Docker 19 (`odoo:19.0`, db `test_hd`) — `14 tests, 0 failed,
  0 error`, **0 "group does not exist" warnings**. `test_13_group_expand_orm_path`
  drives the real ORM path (proves 3-arg golden signature);
  `test_14_security_groups_resolve` guards F-001. R-ORM-002 + F-001 fix are
  **verified on 19** (1/6); full Stable needs 18→14 green under ADR-001.
- Golden bumped to **19.0.1.0.1** (patch: F-001 + R-ORM-002 fixes).

## Open findings (surfaced during verification, NOT compatibility rules)

- **F-001 view groups unresolved** — ✅ FIXED in 19.0.1.0.1. All view/menu
  `groups=` now use `helpdesk_community.group_*`; Docker 19 logs 0 warnings;
  guarded by `test_14`. Recorded as FA-003 in `KNOWN_FALSE_ASSUMPTIONS.md`.
  Version-independent fix — inherited by 18→14 branches when built.
- **F-002 read_group deprecation** — `test_13` uses `read_group` (deprecated in
  19, works 14–19). Portable now; revisit for Odoo 20 (`formatted_read_group`).

## Draft backlog (promote before they can ever be Stable)

| Rule        | Pass     | Blocker to Verified                          |
| ----------- | -------- | -------------------------------------------- |
| R-ORM-003   | Tracking | confirm `aggregator` kwarg name 17 vs 18 in `fields.py` |
| R-VIEW-005  | View     | confirm `states` removal in 19 source        |
| R-VIEW-006  | View     | confirm search `<group expand>` removal in 19 source |
| R-ASSET-001 | Asset    | confirm manifest `assets` vs XML bundle on 14 |
