# Known False Assumptions

> A graveyard of hypotheses that turned out wrong, kept so neither humans nor the
> Compiler repeat them. Every entry follows:
>
> `Assumption → Evidence → Result → Why wrong → Replacement`
>
> Rule of thumb: an assumption only leaves this file when it is replaced by a
> **Verified** rule (source- or Docker-proven).

---

## FA-001 — "group_expand differs at the 19→18 boundary"

- **Assumption:** the `group_expand` callback signature changes between 19.0 and
  18.0, so a transform must fire when lowering 19→18.
- **Evidence:** read `group_expand(...)` call sites directly in Odoo source for
  all six series (`odoo/models.py`, and `odoo/orm/models.py` on 19).
- **Result:** FALSE.
- **Why wrong:** 18.0 and 19.0 both call `group_expand(self, groups, domain)`
  (3 args). The real boundary is **18→17** — 17.0 and older call
  `group_expand(self, groups, domain, order)` (4 args). Change landed in 18.0
  (odoo/odoo#110737).
- **Replacement:** R-ORM-002 (fires ≤17.0 only, appends `order`).

## FA-002 — "the golden 19 group_expand was correct because 12 tests passed"

- **Assumption:** golden `_read_group_stage_ids(self, stages, domain, order)` was
  fine; the suite is green.
- **Evidence:** `test_12` called the method directly with 3 positional args
  (`self.Stage, [], 'sequence'`), never through the ORM kanban path.
- **Result:** FALSE.
- **Why wrong:** the ORM on 18/19 calls the callback with 3 args, so the 4-arg
  golden raised `TypeError` on any real grouped kanban read — a latent bug the
  test masked by calling the method with the wrong arity itself.
- **Replacement:** golden fixed to 3-arg; `test_13_group_expand_orm_path` now
  drives the real `read_group` path (portable 14–19). Verified on Docker 19.

## FA-003 — "bare group names resolve in view `groups=` because ir.rule refs do"

- **Assumption:** `groups="group_helpdesk_team_leader"` on a view button resolves
  within the current module, just like `eval="[(4, ref('group_...'))]"` in an
  ir.rule.
- **Evidence:** Docker 19 install logged `The group "group_helpdesk_team_leader"
  defined in view does not exist!` while the ir.rule refs loaded silently.
- **Result:** FALSE.
- **Why wrong:** ir.rule `ref()` resolves against the loading module context;
  the `ir.ui.view` `groups=` attribute resolves via `ir.model.data` and needs a
  fully-qualified `module.xmlid`. Bare names are dropped → visibility not applied.
- **Replacement:** F-001 fix — always emit `helpdesk_community.group_*`. Guarded
  by `test_14_security_groups_resolve`. (Candidate future lint rule: R-VIEW-007
  "view/menu groups= must be fully qualified".)

## FA-004 — "chatter needs a transform for older series"

- **Assumption:** the 19 golden uses `<chatter/>`, requiring expansion to the
  legacy div for ≤17.
- **Evidence:** inspected the golden arch — it already uses the legacy
  `<div class="oe_chatter">` form, which is accepted 14→19.
- **Result:** FALSE (for this module).
- **Why wrong:** the golden was authored on the lowest-common-denominator arch,
  so no transform is needed.
- **Replacement:** R-VIEW-003 = identity. Note kept: if a future golden adopts
  `<chatter/>`, add R-VIEW-003b (expand to legacy div for ≤17).

## FA-005 — "the `states`/`attrs` attributes were removed in 19"

- **Assumption:** `states` (and `attrs`) view attributes disappear at the 19
  boundary, so R-VIEW-005 documents a 19-only constraint.
- **Evidence:** `ir_ui_view.py` + `common.rng` read across images 16→19.
- **Result:** FALSE (wrong boundary).
- **Why wrong:** they were removed in **17.0**, not 19. 16.0 still *processes*
  `states` (`ir_ui_view.py:89`, converting it to `invisible` modifiers); 17.0+
  raise `ValidationError("Since 17.0, the 'attrs' and 'states' attributes are no
  longer used")`. The RNG `<group>` define drops `states`+`attrs` at 17.0. Being
  wrong by two series would have made the Compiler emit `states` for 17/18 targets
  → broken installs.
- **Replacement:** R-VIEW-005 re-verified with boundary **17.0**. Also surfaced
  the real transform gap **R-VIEW-008** (rewrite 17+ `invisible` domains back to
  legacy `attrs` for ≤16) — kept Draft (Unknown) rather than guessed.

## FA-006 — "install + tests passing means the module is correct on that series"  ★ process gap

- **Assumption:** a green `-i module --test-enable` run on a series proves the
  module works on that series. The 14-test suite passed 14/14 on all 6 series, so
  the golden was declared correct.
- **Evidence:** capturing store screenshots on the **canonical 19** live instance
  immediately hit three hard failures the test suite never saw:
  - **F-003** — kanban `t-name="kanban-box"` throws OwlError `Missing 'card'
    template` on 19 → the kanban view does not render at all (see R-VIEW-002).
  - **F-viewmode** — `view_mode="tree,form"` invalid on 19 (`tree` view type
    removed → `list`); 3 config actions failed to open.
  - **F-portal** — `base.group_portal` had a record rule but **no
    `ir.model.access.csv` ACL** → portal users got 403 Forbidden on their own
    tickets.
- **Result:** FALSE. Install + ORM tests are necessary but **not sufficient**.
- **Why wrong:** Odoo's test framework loads and validates the *registry and data*
  but **never renders a view in a browser**. View-layer regressions (kanban
  template name, `view_mode` view types, missing frontend ACLs, portal QWeb) are
  invisible to `TransactionCase`/`HttpCase`-free suites. "Green tests" measured
  the wrong surface.
- **Replacement:** the release gate now requires a **render-smoke** step in
  addition to install+tests — load each primary view (kanban/list/form/search),
  each menu action, and the customer portal in a real browser (Playwright) before
  a series is called green. The 19 screenshot capture doubles as the 19 render
  smoke; F-003's `kanban-box→card` rename was Docker-render-confirmed on 17 (and
  card-as-is on 18). Backfill render-smoke for 14–16 is tracked as a follow-up.

## FA-007 — "declaring the same field twice in a form is harmless (widget wins)"

- **Assumption:** listing `stage_id` both as `widget="statusbar"` in the `<header>`
  and again as a plain `<field name="stage_id"/>` in a `<group>` is a benign,
  common duplication — the statusbar in the header keeps working everywhere.
- **Evidence:** render-smoke backfill on 14–18. Kanban + list rendered on all,
  but the **form threw an OwlError on 16.0 only** (17/18/19 fine). Real cause
  extracted from the expanded client traceback:
  `TypeError: Cannot read properties of undefined (reading 'map')` at
  `StatusBarField.getVisibleMany2Ones`.
- **Result:** FALSE (16.0-specific hard render failure).
- **Why wrong:** Odoo 16 `relational_model.js#loadPreloadedData` derives the
  preload type as `activeField.widget || field.type`. When a field appears twice,
  the plain (widget-less) occurrence clears `widget` in the merged `activeFields`
  entry, so `type` resolves to `many2one` instead of `statusbar`. The statusbar
  preloader is registered under the key `"statusbar"`, so it never runs →
  `record.preloadedData["stage_id"]` stays `undefined` →
  `StatusBarField.getAllItems()` returns undefined → `.map` crashes the whole
  form. 17+ compute statusbar items differently and tolerate the duplicate; 16
  does not. Invisible to install + `TransactionCase` tests (never paints a view).
- **Replacement:** golden fix — never declare a field twice in one form; the
  header statusbar owns `stage_id`, so the redundant group field was removed.
  Render-smoke green on 14–19 after the fix. (Candidate future lint rule:
  R-VIEW-009 "a field with a widget must not be re-declared plain in the same
  form view".)
