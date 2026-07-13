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
