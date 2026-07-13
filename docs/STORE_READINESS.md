# Store Readiness — helpdesk_community (release 1.0.3)

Report date: 2026-07-13
Repo: `git@github.com:FoxPinkHQ/helpdesk-community.git`
Canonical: branch `19.0` @ `c7951a9` (FA-008 chatter fix)

This report certifies readiness for Odoo Apps Store submission after the
**Minimum Viable Restructure (MVR)** — see `docs/adr/` and the STORE rules in
`docs/compatibility/store-rules/RULES.md`.

## 1. Repository layout (STORE-001)

```
helpdesk-community/            (repo — hyphenated name, NOT a module)
├── helpdesk_community/        ← the one module (valid Odoo name)
├── docs/                      (knowledge / evidence / ADR / store-rules)
├── README.md
├── MARKET_RELEASE_CHECKLIST.md
├── SPEC.md / BACKLOG.md / IMPLEMENTATION_PLAN.md
├── LICENSE
└── .gitignore
```

MVR scope (deliberate): module moved into a valid-name subfolder; build
tooling (`odoo_store/`) and the Compiler stay in their own workspaces. They
will be split into a dedicated FoxPink Builder / OdooGen project only once
multiple modules exist.

## 2. Branch = series = version prefix (STORE-002/003)

Each branch is a **compiled artifact** produced by the Compatibility Layer
(`build_version.ps1`) from the canonical `19.0`. Branches are never hand-edited.

| Branch | Module folder | Manifest version | list-tag | kanban | chatter | Transforms |
|--------|---------------|------------------|----------|--------|---------|------------|
| 14.0 | `helpdesk_community/` | `14.0.1.0.3` | `<tree>` | `kanban-box` | `oe_chatter` div | R-MANIFEST-001, R-VIEW-001, R-VIEW-002, R-VIEW-003, R-ORM-002, R-TEST-001 |
| 15.0 | `helpdesk_community/` | `15.0.1.0.3` | `<tree>` | `kanban-box` | `oe_chatter` div | R-MANIFEST-001, R-VIEW-001, R-VIEW-002, R-VIEW-003, R-ORM-002 |
| 16.0 | `helpdesk_community/` | `16.0.1.0.3` | `<tree>` | `kanban-box` | `oe_chatter` div | R-MANIFEST-001, R-VIEW-001, R-VIEW-002, R-VIEW-003, R-ORM-002 |
| 17.0 | `helpdesk_community/` | `17.0.1.0.3` | `<tree>` | `kanban-box` | `oe_chatter` div | R-MANIFEST-001, R-VIEW-001, R-VIEW-002, R-VIEW-003, R-ORM-002 |
| 18.0 | `helpdesk_community/` | `18.0.1.0.3` | `<list>` | `card` | `<chatter/>` | R-MANIFEST-001 (identity) |
| 19.0 | `helpdesk_community/` | `19.0.1.0.3` | `<list>` | `card` | `<chatter/>` | canonical (identity) |

## 3. Validation evidence

### 3.1 Build + package + manifest prefix (this release)
`build_market_release.ps1` → **6/6 VALIDATION PASSED**, `dist/market-release.json`
`validated:true`. icon.png 512×512 verified per artifact.

| Series | Artifact | sha256 |
|--------|----------|--------|
| 14.0 | `dist/14.0/helpdesk_community-14.0.1.0.3.zip` | `274c6882f0678c8833ac0fdea4c56964f65488a5f2dd94f4c174f165fe0cb42c` |
| 15.0 | `dist/15.0/helpdesk_community-15.0.1.0.3.zip` | `3d863893a2af539dfb13f743f06fecc007ce1ad11882e42c8b683a0e0f104990` |
| 16.0 | `dist/16.0/helpdesk_community-16.0.1.0.3.zip` | `18734857f9bfcc02e33ec72f46d2e05f7a4842f101e9ace48939a1714455daf4` |
| 17.0 | `dist/17.0/helpdesk_community-17.0.1.0.3.zip` | `8452d9ccc97c9fec2b1659a1f35cdb8f296593fcaeffbf00d9baae14b3888667` |
| 18.0 | `dist/18.0/helpdesk_community-18.0.1.0.3.zip` | `c52516c514f1973684c1404af4c097baaae476c686f851d6571007570d1c6780` |
| 19.0 | `dist/19.0/helpdesk_community-19.0.1.0.3.zip` | `3f4cba054ff2cc5c99a060d6cc6451003cb6347ddd313cf272ac4158dc190c67` |

### 3.2 Render smoke (ADR-002)
- Full matrix 14.0–19.0: **PASSED** (kanban/list/form render, 0 uncaught OwlError)
  after the FA-007 fix — the gate that previously caught the Odoo-16 form crash.
- FA-008 chatter fix re-confirmation on the boundary series: **17.0** (legacy
  `oe_chatter` div via R-VIEW-003) and **18.0** (bare `<chatter/>`) both PASSED
  (kanban 3 cards, list, form, 0 JS errors).

### 3.2b FA-008 overflow measurement (Playwright, live 19.0)
Before: chatter 1408px, sheet squeezed to 34px @ `left=-33`, statusbar off-canvas.
After `<chatter/>`: sheet 886px + chatter aside 530px; `docScrollWidth == innerWidth`,
`offenders: []` at viewports 1440 / 1366 / 1024 / 768 — zero horizontal overflow.

### 3.3 Tests
- 14.0–19.0: **14/14 tests pass, 0 error** (Phase 1.5).

### 3.4 Restructure code-identity proof
The restructure was a pure relocation: `git mv` reported **100% similarity** for
every module file, and `build_version` is deterministic. The runtime files Odoo
loads (`.py` / `.xml` / `.csv` / `static`) are byte-identical to the versions
validated in 3.2/3.3. The only packaging delta is that non-runtime docs
(`README.md`, `MARKET_RELEASE_CHECKLIST.md`) are no longer bundled into the zip
(1778 → 1775 KB), which Odoo ignores.

### 3.5 FA-007 guard
Form view (`helpdesk_ticket_views.xml`) has exactly one `stage_id` in the form
(statusbar in `<header>`); the redundant group field is gone. Other `stage_id`
usages are legitimate (tree column, search group_by).

### 3.6 FA-008 guard
Canonical form uses the modern `<chatter/>` tag (18.0+ correct flex aside).
R-VIEW-003 transforms it back to the legacy `<div class="oe_chatter">` idiom for
series ≤ 17.0 (endorsed through saas-17.4). No `oe_chatter` div remains on 18.0/19.0.

## 4. Compliance checklist

| Rule | Requirement | Status |
|------|-------------|--------|
| STORE-001 | Module in valid-name subfolder | READY |
| STORE-002 | branch == series == version prefix | READY (6/6) |
| STORE-003 | Each branch = compiled artifact, no hand-edit | READY |
| STORE-004 | English description / screenshots | READY (index.html listing + 9 captioned screenshots, all 6 branches) |
| STORE-005 | Real PNG icon (512×512) | READY |
| STORE-006 | No manifest error (would unpublish whole repo) | READY (6/6 validated) |
| STORE-007 | No embedded credentials | READY (old PAT revoked, SSH remote, credential store clean) |

## 5. Open items before "Submit"

1. Authorize the repository on the Odoo Apps Store account (`aduy000@gmail.com`)
   and submit per `docs/STORE_SUBMISSION_GUIDE.md`; log outcome to
   `docs/STORE_REVIEW_NOTES.md`.

## 6. Verdict

Engineering gates: **6/6 READY** (release 1.0.3, FA-008 fixed). Remaining item is
the Store portal submission itself, not code.
