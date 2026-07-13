# Store Readiness — helpdesk_community (release 1.0.2)

Report date: 2026-07-13
Repo: `git@github.com:FoxPinkHQ/helpdesk-community.git`
Canonical: branch `19.0` @ `58c53df`

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

| Branch | Module folder | Manifest version | list-tag | kanban | Transforms |
|--------|---------------|------------------|----------|--------|------------|
| 14.0 | `helpdesk_community/` | `14.0.1.0.2` | `<tree>` | `kanban-box` | R-MANIFEST-001, R-VIEW-001, R-VIEW-002, R-ORM-002, R-TEST-001 |
| 15.0 | `helpdesk_community/` | `15.0.1.0.2` | `<tree>` | `kanban-box` | R-MANIFEST-001, R-VIEW-001, R-VIEW-002, R-ORM-002 |
| 16.0 | `helpdesk_community/` | `16.0.1.0.2` | `<tree>` | `kanban-box` | R-MANIFEST-001, R-VIEW-001, R-VIEW-002, R-ORM-002 |
| 17.0 | `helpdesk_community/` | `17.0.1.0.2` | `<tree>` | `kanban-box` | R-MANIFEST-001, R-VIEW-001, R-VIEW-002, R-ORM-002 |
| 18.0 | `helpdesk_community/` | `18.0.1.0.2` | `<list>` | `card` | R-MANIFEST-001 (identity) |
| 19.0 | `helpdesk_community/` | `19.0.1.0.2` | `<list>` | `card` | canonical (identity) |

## 3. Validation evidence

### 3.1 Build + package + manifest prefix (this release)
`build_market_release.ps1` → **6/6 VALIDATION PASSED**, `dist/market-release.json`
`validated:true`. icon.png 512×512 verified per artifact.

| Series | Artifact | sha256 |
|--------|----------|--------|
| 14.0 | `dist/14.0/helpdesk_community-14.0.1.0.2.zip` | `79d5e5753fee3bfc2a818fe015f7326f638d24bc9c8fdca54f6a658964a01402` |
| 15.0 | `dist/15.0/helpdesk_community-15.0.1.0.2.zip` | `a06c80c60e1a4b677e7f5c570bc9bc66ba78cb6ffea73860b591b1b33a34eaf1` |
| 16.0 | `dist/16.0/helpdesk_community-16.0.1.0.2.zip` | `32b0943566405a8f53345292afcd3f0536323dc1312125c72fad3324369085e2` |
| 17.0 | `dist/17.0/helpdesk_community-17.0.1.0.2.zip` | `a3179b208c2024cfb2d4743b285accd0861a0b08ecc6bd269b1234745bdb58ea` |
| 18.0 | `dist/18.0/helpdesk_community-18.0.1.0.2.zip` | `a5d382c81bd7afb6eed8263b64544ee7a58a31b7e73106d579c0f51122a5b81e` |
| 19.0 | `dist/19.0/helpdesk_community-19.0.1.0.2.zip` | `e14a4b3381194e67964eb7fa75a9e8c01604e493ff8c20f2ec2419fbfcddde85` |

### 3.2 Render smoke (ADR-002)
- Full matrix 14.0–19.0: **PASSED** (kanban/list/form render, 0 uncaught OwlError)
  after the FA-007 fix — the gate that previously caught the Odoo-16 form crash.
- Post-restructure re-confirmation on **16.0** (FA-007 boundary + ≤17 kanban
  rename path): **PASSED** (admin login, kanban 3 cards, list, form, 0 JS errors).

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

## 4. Compliance checklist

| Rule | Requirement | Status |
|------|-------------|--------|
| STORE-001 | Module in valid-name subfolder | READY |
| STORE-002 | branch == series == version prefix | READY (6/6) |
| STORE-003 | Each branch = compiled artifact, no hand-edit | READY |
| STORE-004 | English description / screenshots | PENDING (portal step) |
| STORE-005 | Real PNG icon (512×512) | READY |
| STORE-006 | No manifest error (would unpublish whole repo) | READY (6/6 validated) |
| STORE-007 | No embedded credentials | LOCAL DONE / **PAT rotation pending on GitHub** |

## 5. Open items before "Submit"

1. **Rotate the old PAT on GitHub** (revoke `ghp_6RdX…`, create new; add
   `workflow` scope if reused for CI). Security blocker (STORE-007).
2. Prepare Store portal metadata: English long description + screenshots (STORE-004).
3. Push branches to origin (this report precedes the batch push).

## 6. Verdict

Engineering gates: **6/6 READY**. Remaining items are portal/account actions
(PAT rotation, Store listing copy), not code.
