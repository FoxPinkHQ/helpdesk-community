# Market Release Checklist

> The single gate a FoxPink module must clear before it is submitted to the
> **Odoo Apps Store**. Copy this file into every new module repo and tick each
> box. A box may only be ticked when it is **proven** (Docker run, artifact,
> screenshot, or a live URL) — never on intent.
>
> Ordering follows the DoD: **Install → Tests → Render Smoke → Package → Assets
> → Submission**. CI (GitHub Actions) is deliberately **not** a Market blocker
> (ADR-001: Engineering vs Market tracks) — it is Phase 2D, after submission.

---

## Module: `helpdesk_community`

- **Version:** 19.0.1.0.2
- **Canonical series:** 19.0 (ADR-001)
- **Supported series:** 14.0, 15.0, 16.0, 17.0, 18.0, 19.0
- **Publisher:** FoxPink
- **Support email:** aduy000@gmail.com
- **Repo:** https://github.com/FoxPinkHQ/helpdesk-community
- **HEAD at release candidate:** `aac5aa9`

### 1. Install (Docker `odoo:<v>` + `-i module`)
- [x] Install 14.0
- [x] Install 15.0
- [x] Install 16.0
- [x] Install 17.0
- [x] Install 18.0
- [x] Install 19.0

### 2. Tests (`--test-enable`, 14/14)
- [x] Tests green 14.0
- [x] Tests green 15.0
- [x] Tests green 16.0
- [x] Tests green 17.0
- [x] Tests green 18.0
- [x] Tests green 19.0

### 3. Render Smoke (Playwright paint check — kanban/list/form/menus/portal, 0 OwlError)
- [x] Render smoke 14.0
- [x] Render smoke 15.0
- [x] Render smoke 16.0  *(FA-007 fixed: duplicate `stage_id` statusbar crash)*
- [x] Render smoke 17.0
- [x] Render smoke 18.0
- [x] Render smoke 19.0  *(doubles as the live screenshot capture)*

### 4. Compatibility Layer
- [x] Transforms verified on 14–19 (RULES.md, all exercised rules Stable)
- [x] Version matrix documented (docs/compatibility/MATRIX.md)
- [x] Known false assumptions recorded (FA-001 … FA-007)

### 5. Package
- [x] `package_module.ps1` VALIDATION PASSED (manifest keys, license, data files, icon size, junk sweep)
- [x] ZIP artifact built with forward-slash entries — `dist/helpdesk_community-19.0.1.0.2.zip`

### 6. Store Assets
- [x] `icon.png` 512×512
- [x] `banner.png` 1280×640
- [x] Screenshots (9× @2x, 2880×1800) in `static/description/`
- [x] `static/description/index.html` (story flow + 6-version matrix)
- [x] Description (summary + long description in manifest & index.html)
- [x] Changelog present *(see CHANGELOG below / manifest version)*
- [x] License declared — LGPL-3
- [x] Version Matrix visible in listing
- [x] Support email present

### 7. Submission
- [ ] Uploaded to Odoo Apps Store (publisher account)
- [ ] Listing metadata filled (category, price=Free/community, versions)
- [ ] Submission completed / awaiting review
- [ ] Review outcome recorded (`STORE_REVIEW_NOTES.md`)

---

## Post-submission (Phase 2D — does not affect first users)
- [ ] New PAT with `workflow` scope
- [ ] Push `.github/workflows/ci.yml`
- [ ] CI green badge on README
- [ ] Auto test matrix 14–19 wired
- [ ] Engineering tag `19.0.1.0.2` (git tag + GitHub Release)
- [ ] Mark first **FoxPink Market Release** once Store-approved

---

## How to reuse (module #2+)
1. Copy this file to the new module repo.
2. Reset every `[x]` to `[ ]` and fill the Module header.
3. Drive the boxes top-down; each series' Install/Tests/Render are produced by
   `build_version.ps1` + `render_smoke.ps1`.
4. Never tick a box you cannot point to evidence for.
