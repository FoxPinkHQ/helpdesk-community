# STORE Rules

> Distribution/publishing constraints for the Odoo Apps Store backend.
> Status legend: **Draft** (hypothesis) · **Verified** (source- or
> submission-proven) · **Stable** (enforced gate) · **Rejected**.
> Every Verified/Stable rule cites its source.

---

## STORE-001 — module lives in a valid-name subfolder, never at repo root
- **Status:** Verified (source) → treat as Stable gate.
- **Rule:** on every series branch, the module must be a subfolder named with a
  valid Odoo technical name (`helpdesk_community/__manifest__.py`). It must not
  sit at repo root, because the Store derives the module directory from the repo
  checkout and the repo is `helpdesk-community` — a hyphen is not a valid
  Odoo/Python module name.
- **Evidence:** Vendor Guidelines / "New Odoo Apps store" — "Setup your
  repository: one folder per module". Odoo module names must be valid Python
  identifiers (underscores).
- **Impact if violated:** scan error / invalid module name → reject.
- **Compiler action:** emit each branch with the module under
  `helpdesk_community/` (packaging already zips with this root; branches must
  match).

## STORE-002 — branch name == series AND manifest version prefix == series
- **Status:** Verified (source).
- **Rule:** register `repo#<series>`; the branch name must exactly equal the Odoo
  series (`16.0`), and the module `version` on that branch must start with the
  same series (`16.0.x.y.z`).
- **Evidence:** FAQ / Apps store slides — "branch name matches series
  (e.g. `#8.0`)"; Vendor Guidelines — version "should include the Odoo version".
- **Impact if violated:** version/branch mismatch → reject; combined with
  STORE-006 it can unpublish the whole repo.
- **Current state (helpdesk_community):** VIOLATED — branches 14.0–18.0 still
  carry `version = 19.0.1.0.0`. Must regenerate per series.

## STORE-003 — each series branch is the *compiled artifact*, not a golden copy
- **Status:** Verified (submission-independent, from our own build system).
- **Rule:** branch `S` content must equal the output of
  `build_version.ps1 -Version S` (all Compatibility-Layer transforms applied,
  including FA-007). Never hand-edit a branch; regenerate from golden.
- **Evidence:** render-smoke proved series-specific fixes are required
  (F-003 kanban `card`→`kanban-box` for ≤17; FA-007 duplicate `stage_id`
  statusbar crash on 16). A golden copy on a ≤17 branch renders broken.
- **Impact if violated:** the Store would publish a build that crashes on that
  series even though the canonical 19 is fine.
- **Current state:** VIOLATED — branches 14.0–18.0 still contain the duplicate
  `stage_id` (FA-007) and `card` kanban (F-003).

## STORE-004 — description and screenshots must be in English
- **Status:** Verified (source).
- **Rule:** the app description (manifest + `static/description/`) and all
  screenshots must be English regardless of the author's country/language.
- **Evidence:** Vendor Guidelines — "The app's description and screenshots must
  be in English, regardless of the originating country or language of the app."
- **Impact if violated:** reject / unpublish until fixed.
- **FoxPink note:** manifest `summary`/`description` are already English. Verify
  the captured screenshots show the **English** UI (project convention allows
  Vietnamese user-facing labels, which would violate this rule for the Store —
  capture Store screenshots with an English session).

## STORE-005 — assets: real PNG icon + allowed image formats
- **Status:** Verified (source).
- **Rule:** `static/description/icon.png` must be a genuine PNG (not a renamed
  file); description images may only be `png`, `gif`, or `jpeg`; the cover/main
  image comes from the manifest `images` key, and an image whose filename ends
  `_screenshot` is shown as the large preview.
- **Evidence:** FAQ — icon location/format; "only image file formats allowed …
  are png, gif, and jpeg"; `images` key + `_screenshot` behaviour.
- **Impact if violated:** icon/screenshots not displayed → listing looks broken.

## STORE-006 — a manifest error unpublishes the WHOLE repository (blast radius)
- **Status:** Verified (source).
- **Rule:** any manifest error on any branch can unpublish every module in the
  repository; keep all branches valid at all times.
- **Evidence:** Vendor Guidelines — "any error will unpublish all the modules
  from your repository." FAQ R-sanctions — temporary unpublish until fixed.
- **Impact if violated:** a single bad branch takes down all listings.
- **Compiler action:** the release step must validate *all* series branches
  before any push (fail-closed), mirroring `build_market_release.ps1`.

## STORE-007 — no embedded credentials in the repository / git config (hygiene)
- **Status:** Draft (best practice, not an Odoo scan rule).
- **Rule:** never commit or store a PAT in `.git/config` remote URLs or in repo
  files; use a credential manager. Rotate any exposed token.
- **Evidence:** general security policy; Odoo authorizes read access via the
  `online-odoo` user (private repos), not via embedded tokens.
- **Current state:** the local clone's remote URL embeds a `ghp_…` PAT — rotate
  and remove.

---

## Open questions (kept Draft rather than guessed)
- **[VERIFY]** Does one dashboard repo registration auto-scan all `*.0` series
  branches, or must each series be added separately?
- **[VERIFY]** Is per-version ZIP upload still offered as an alternative to
  repo-scan, and does it list under the correct Odoo version automatically?
- **[VERIFY]** Exact minimum screenshot dimensions the Store enforces (guides
  cite 1200×800+; not stated on official pages).
