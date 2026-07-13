# FoxPink Compatibility Matrix (Odoo 14 – 19)

> **Scope:** Publisher-wide knowledge base. Extracted from `helpdesk-community`
> (the golden 19.0 module) but intended to be reused by **every** FoxPink module.
> The golden source of truth is always **19.0**; older series are produced by the
> Compatibility Layer, not hand-edited.
>
> **Legend**
> - `=` : identical, no transform needed
> - `T` : transform required (see `RULES.md` rule id)
> - `?` : behavioural difference — verify per module before release
> - `n/a` : not used by this module (rule still documented for future modules)

## 1. Compiler pass mapping

The OdooGen Compatibility Layer exposes 5 passes. Every rule below is owned by
exactly one pass:

| Pass          | Owns                                                     |
| ------------- | ------------------------------------------------------- |
| `ManifestPass`| `__manifest__.py` version, keys, `assets`, `depends`    |
| `TrackingPass`| ORM API, mail/chatter model mixins, compute/create      |
| `ViewPass`    | list/tree, kanban, form, search, chatter arch           |
| `ReportPass`  | QWeb reports, paperformat                               |
| `AssetPass`   | JS/OWL/SCSS bundles, `web.assets_*`                     |

## 2. Component × version matrix

| Component / Primitive                     | 19 | 18 | 17 | 16 | 15 | 14 | Rule id        |
| ----------------------------------------- | -- | -- | -- | -- | -- | -- | -------------- |
| **Manifest** `version` prefix             | =  | T  | T  | T  | T  | T  | R-MANIFEST-001 |
| Manifest `depends` (base/mail/portal/web) | =  | =  | =  | =  | =  | =  | —              |
| Manifest `license` LGPL-3                 | =  | =  | =  | =  | =  | =  | —              |
| **ORM** `@api.model_create_multi`         | =  | =  | =  | =  | =  | =  | R-ORM-001      |
| ORM `create(vals_list)` batch             | =  | =  | =  | =  | =  | =  | R-ORM-001      |
| ORM `group_expand` callback signature     | =  | =  | T  | T  | T  | T  | R-ORM-002      |
| ORM `aggregator` vs `group_operator`      |n/a |n/a |n/a |n/a |n/a |n/a | R-ORM-003      |
| **Mail** `mail.thread` / activity mixin   | =  | =  | =  | =  | =  | =  | —              |
| **View** `<list>` vs `<tree>`             | =  | =  | T  | T  | T  | T  | R-VIEW-001     |
| View `view_mode` `list` token             | =  | =  | T  | T  | T  | T  | R-VIEW-001     |
| Kanban `<card>` element                   | =  | =  | T  | T  | T  | T  | R-VIEW-002     |
| Kanban `t-name="card"` vs `kanban-box`    | ?  | ?  | =  | =  | =  | =  | R-VIEW-002     |
| Kanban `<i class="fa">` needs `title`     | =  | =  | =  | =  | =  | =  | R-VIEW-004     |
| Chatter arch (legacy `oe_chatter` div)    | =  | =  | =  | =  | =  | =  | R-VIEW-003     |
| View `states` attribute                   |n/a |n/a |n/a |n/a |n/a |n/a | R-VIEW-005     |
| Search `<group expand>`                   |n/a |n/a |n/a |n/a |n/a |n/a | R-VIEW-006     |
| **Security** `res.groups` `category_id`   | =  | =  | =  | =  | =  | =  | R-SEC-001      |
| Security `ir.model.access.csv`            | =  | =  | =  | =  | =  | =  | —              |
| **Report** QWeb + paperformat             | =  | =  | =  | =  | =  | =  | R-REPORT-001   |
| **Test** `TransactionCase` class env      | =  | =  | =  | =  | =  | T  | R-TEST-001     |
| **Assets** `web.assets_backend` (manifest)|n/a |n/a |n/a |n/a |n/a | ?  | R-ASSET-001    |

## 3. Why this ordering matters

`helpdesk-community` is deliberately the **first** module through the layer: it
exercises Manifest, Tracking, View, Report and Security passes, but **not** Asset
(no OWL). The `n/a` rows are pre-documented so the second module (which will have
OWL components) does not restart the discovery from zero.

The `n/a` rows are **not exercised by this module** but their boundaries are now
**source-verified** (2026-07-13) for future modules — see `evidence/`:

| Primitive (n/a here) | Verified boundary | Transform for older |
| -------------------- | ----------------- | ------------------- |
| ORM `aggregator`     | 18.0 | rename → `group_operator` for ≤17 |
| View `states`/`attrs`| 17.0 | golden-lint (never emit); + R-VIEW-008 for ≤16 |
| Search `<group expand>` | 19.0 | golden-lint (never emit) |
| Manifest `assets`    | 15.0 | 14.0 → XML `web.assets_backend` bundle |

## 4. Verification gate

Per ADR-001, a rule is only promoted from `?` to `=`/`T` after the transformed
artifact **installs and passes tests** on a real Docker instance of that series.
No release until all 6 series are green.

**Status 2026-07-13:** ✅ all 6 series (14–19) install + 14/14 tests, 0 error. Every
`=`/`T` cell above is Docker-confirmed and its rule promoted to **Stable**. The
`kanban t-name` row is `?` on 18/19 (F-003: golden emits deprecated `kanban-box`;
works, cosmetic warning). `n/a` rows await an exercising module.
