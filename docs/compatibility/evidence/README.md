# Evidence Packs

Per-rule audit trail. Each folder proves (or corrects) one rule from
`../RULES.md` using **primary source** — the actual code shipped in the official
`odoo:<series>` Docker images (`/usr/lib/python3/dist-packages/odoo`).

Layout per rule:
- `evidence.md` — claim, upstream citations (file:line per series), boundary,
  impact pass, regression risk, decision.
- `confidence.json` — machine-readable summary for the Compiler / KPI tooling.

| Rule | Verified boundary | Decision | Note |
| ---- | ----------------- | -------- | ---- |
| R-ORM-003 | 18.0 | Draft→Verified 100% | aggregator↔group_operator |
| R-VIEW-005 | **17.0** (was 19) | Draft→Verified 100% | boundary corrected → FA-005 |
| R-VIEW-006 | 19.0 | Draft→Verified 100% | group `expand` removed in 19 |
| R-ASSET-001 | 15.0 | Draft→Verified 95% | manifest `assets` needs `ir.asset` |
| R-TEST-001 | **15.0** | Discovered→**Stable** 100% | `TransactionCase` class env; 14 needs `SavepointCase` (source + Docker 14) |

Boundaries were read from source on 2026-07-13; `last_validated` in each
`confidence.json` tracks freshness.
