# Odoo Apps Store — Submission Guide (SOP)

> FoxPink Standard Operating Procedure for publishing a module to
> **apps.odoo.com**. Written once, reused for every module. Ground truth is the
> official Odoo pages (cited inline); anything not proven from them is marked
> **[VERIFY]** rather than guessed (Unknown > Wrong).
>
> Sources (retrieved 2026-07):
> - Vendor Guidelines — https://apps.odoo.com/apps/vendor-guidelines
> - Submit your Apps — https://apps.odoo.com/apps/upload
> - Apps FAQ — https://apps.odoo.com/apps/faq
> - App Dashboard — https://apps.odoo.com/apps/dashboard
> - Module manifest ref — https://www.odoo.com/documentation/19.0/developer/reference/backend/module.html

---

## 0. The distribution model (read this first)

The Odoo Apps Store does **not** primarily consume a single ZIP. For community /
multi-version modules it **scans a Git repository, one branch per Odoo series**,
where **the branch name must exactly equal the series** (`14.0`, `15.0`, … ,
`19.0`). Odoo checks out `repo#<series>` and publishes the module(s) it finds on
that branch under that Odoo version. (FAQ: register the SSH clone URL followed by
`#<branch>`; "branch name matches series".)

This reconciles with FoxPink's **release-by-artifact** model as follows:

```
19.0 golden (canonical source)
        │  build_market_release.ps1  (build_version → package_module ×6)
        ▼
6 compiled artifacts  ──────────────►  6 series branches (14.0 … 19.0)
   dist/<series>/*.zip                    each branch = that artifact's source
   (GitHub Release + customer portal)     (this is what the Store scans)
```

- The **`dist/*.zip`** are for GitHub Releases, the customer portal, and evidence.
- The **series branches** are what the Store reads. Each series branch must
  contain the **compiled artifact for that series**, not a copy of the golden.
- A **ZIP upload** path also exists (apps.odoo.com/apps/upload) for a single
  version; treat it as a fallback, not the multi-version mechanism. **[VERIFY]**
  whether the current dashboard offers ZIP-per-version listing.

---

## 1. Pre-flight — repository layout (STORE-001)

- [ ] On **every** series branch the module lives in a subfolder whose name is
      the **valid Odoo technical name**: `helpdesk_community/__manifest__.py`.
      The repo is named `helpdesk-community` (hyphen) — a hyphen is **not** a
      valid Odoo/Python module name, so the module must **never** sit at repo
      root. See STORE-001.
- [ ] Exactly **one folder per module** at the branch root.
- [ ] No build junk in the branch (`__pycache__`, `.pyc`, tokens, `dist/`).

## 2. Pre-flight — branches match artifacts (STORE-002 / STORE-003)

For each series `S` in {14.0 … 19.0}:
- [ ] Branch `S` exists and its `helpdesk_community/__manifest__.py` `version`
      starts with `S.` (e.g. branch `16.0` → `16.0.1.0.2`). A mismatched prefix
      is an automatic reject and **can unpublish the whole repo** (Vendor
      Guidelines: "any error will unpublish all the modules from your
      repository"). See STORE-006.
- [ ] Branch `S` content == the artifact validated by render-smoke + tests for
      `S` (same Compatibility-Layer transforms, including FA-007). Regenerate via
      `build_version.ps1 -Version S`, never hand-edit a branch. See STORE-003.
- [ ] `dist/market-release.json` `validated: true` and its per-series sha256
      corresponds to what you pushed.

## 3. Pre-flight — manifest (mandatory keys, Vendor Guidelines)

- [ ] `name` — explicit, **≤ 25 chars**, no adjectives, no company name.
      (`Helpdesk Community` = 18 ✓)
- [ ] `version` — `\<series\>.major.minor.bugfix` (e.g. `19.0.1.0.2`), bumped on
      every release.
- [ ] `license` — recognised id. Open-source recommended `LGPL-3`; paid `OPL-1`.
      **AGPL/LGPL cannot be sold at price > 0.**
- [ ] `summary` — one-liner shown in search results, **English**.
- [ ] `description` — **English** (STORE-004). Derived from manifest +
      `static/description/`.
- [ ] `author`, `website`, `support` (email for claims/support — visible only to
      buyers), `depends` (every dependency listed; a missing dep fails the scan).
- [ ] `installable: True`, `auto_install: False` (unless truly needed),
      `application` set intentionally.
- [ ] Paid only: `price` (min 9 EUR) + `currency` (EUR|USD). Free = omit `price`.
- [ ] Module installs by copying to `addons/` + satisfying deps — **no** custom
      install steps, **no** code download / obfuscation (FAQ R2).
- [ ] No hardcoded company data (`self.env.company`, not `company_id = 1`).

## 4. Pre-flight — store assets (STORE-004 / STORE-005)

- [ ] `static/description/icon.png` — **actual PNG** (renaming `.ico`→`.png`
      fails), ≥ 128×128.
- [ ] `static/description/index.html` — rich-text description, **English**,
      images referenced relative to the description folder; only `png/gif/jpeg`
      allowed.
- [ ] `images` manifest key points at existing files. For a large cover
      screenshot, include an image whose filename ends `_screenshot` (the first
      such image becomes the big preview). **[VERIFY]** current banner vs
      `_screenshot` behaviour.
- [ ] Screenshots are of the **English** UI (STORE-004). If the demo/UI was
      captured in Vietnamese, re-capture in English before submitting.
- [ ] `LICENSE` file at module root (full license text).
- [ ] Optional: `doc/index.rst` (auto-loaded documentation, valid pure RST).

## 5. Pre-flight — DoD gate (from MARKET_RELEASE_CHECKLIST.md)

- [ ] Install 14–19 green · Tests 14–19 green · Render-smoke 14–19 green.
- [ ] 6 artifacts validated, 6 manifest prefixes correct, `market-release.json`.

## 6. Authorize the repository (only if private — FAQ)

- Public repo → no authorization needed.
- Private GitHub → grant read to the GitHub user **`online-odoo`** (NOT
  `odoo-online`) **on this repo specifically** (not the whole org), and register
  the **SSH** clone URL.
- GitLab → authorize `apps@odoo.com` (`OdooApps`). Bitbucket/other → their public
  SSH key.

> Security: never embed a PAT in the git remote URL / `.git/config`. If one was
> committed or stored, **rotate it** and use a credential manager. See
> store-rules note.

## 7. Register & submit (App Dashboard)

1. Sign in at https://apps.odoo.com with the FoxPink publisher account
   (`aduy000@gmail.com`).
2. **My Apps Dashboard** → add repository. Enter the clone URL with the branch
   suffix, e.g. `…/helpdesk-community#19.0` (repeat / rely on scan for each
   series branch — **[VERIFY]** whether one registration scans all `*.0`
   branches or each series is added separately).
3. Click **Scan** (first time) so Odoo reads the repo.
4. Repositories are created as **draft** → click **Validate**.
5. Fill listing metadata: category, supported versions, pricing (Free), banner,
   screenshots, description (already from `static/description/`).
6. Submit.

## 8. After submission

- Review window: **5–10 business days** (may be shorter for free apps; Odoo
  states not every module is manually reviewed but acts on reports).
- Record the outcome in `docs/STORE_REVIEW_NOTES.md` (one entry per submission).
- If **rejected**: do not just patch. Capture the reason as a new/updated rule in
  `docs/compatibility/store-rules/` (Store becomes another compiler backend),
  fix, bump version, push the affected branch(es), re-submit.
- If **approved**: archive the full trail (commit → push → scan → validate →
  publish) as pipeline knowledge, then tag the Engineering release and mark the
  first FoxPink **Market Release**.

## 9. Common rejection causes (grounded)

- Missing/!recognised `license`; inconsistent `version` (manifest must match the
  directory + README + branch series).
- Hardcoded company info; PEP8 / security-warning code quality.
- Non-English description or screenshots.
- Icon not a real PNG or wrong location.
- Custom install procedure; code that downloads/launches other code (R2).
- Undocumented/hidden features vs description (R3); data collection w/o consent
  (R4); no support for paying customers (R6).
- Manifest error → **unpublishes every module in the repo** (blast radius).
