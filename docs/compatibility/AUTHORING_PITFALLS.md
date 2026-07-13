# Odoo Authoring Pitfalls (publisher-wide)

> A reusable "do-not-repeat" catalogue for **every FoxPink module**, distinct from
> `KNOWN_FALSE_ASSUMPTIONS.md` (which records wrong *compatibility* hypotheses).
> These are **module-authoring defects** that paint fine but fail on a real user
> action — the class ADR-003's **Behavior** tier exists to catch.
>
> Each entry: `Symptom → Root cause → Fix → Prevention (checklist / lint / default)`.
> When a pitfall becomes mechanically enforced (Planner default or
> `validate_odoo_syntax` rule) it is tagged **[mechanized]**; until then it is a
> **[review]** checklist item.

---

## AP-001 — `widget="color"` on an Integer field crashes on save

- **Symptom:** view paints; picking a color and **saving** raises
  `ValueError: invalid literal for int() with base 10: '#e90707'` (RPC_ERROR).
- **Root cause:** `widget="color"` is a **hex string** picker; Odoo's color
  convention (`color` field, kanban color index) is an **Integer**. The widget
  posts `#rrggbb`, the ORM writes to an Integer column → crash.
- **Fix:** use `widget="color_picker"` for Integer color-index fields. Reserve
  `widget="color"` for Char fields that genuinely store a hex string.
- **Prevention [review]:** any `color`/palette field → confirm field type vs widget.
  Candidate lint: *Integer field + `widget="color"` → error; suggest `color_picker`.*
- **Origin:** helpdesk_community Bug A (1.0.4). Behavior-verified 19.0 + shell 16.0.

## AP-002 — required field with no default freezes the form

- **Symptom:** a brand-new record's form is permanently **dirty**; Save appears to
  do nothing (silently blocked by inline required-validation) and stat/header
  buttons become no-ops because the record can't persist.
- **Root cause:** a field is `required=True` (often a `_default`-less `stage_id` /
  status / stage-like m2o) with **no client-side default**, so the form opens
  invalid and can never reach a clean state from the UI.
- **Fix:** give every `required=True` field a `default` that resolves at
  `default_get` time (e.g. a `_default_stage_id` returning the start/first stage),
  mirroring any server-side `create()` default so UI and RPC agree.
- **Prevention [review]:** for each `required=True` non-related field, assert a
  `default` exists (or the field is always set by an onchange/parent). Candidate
  lint: *required field with no `default=` and no `related=` → warning.*
- **Origin:** helpdesk_community Bug D (1.0.4). Behavior-verified 19.0 + shell 16.0.

## AP-003 — custom stat/action buttons that don't mutate state

- **Symptom:** clicking a header/stat button (e.g. *Assign to me*) does nothing
  observable.
- **Root cause (two flavors):** (a) the Python handler doesn't actually `write`
  the field it claims to; or (b) it's masked by AP-002 — the record can't save so
  the side-effect never persists.
- **Fix:** handler performs an explicit `self.write({...})` / assignment and
  returns cleanly; **and** ensure the form can save (see AP-002).
- **Prevention [review]:** every custom button needs a Behavior UAT click that
  asserts the resulting field value — not just that the button paints.
- **Origin:** helpdesk_community Bug B (1.0.4).

## AP-004 — portal / website POST form without `csrf_token`

- **Symptom:** the portal page renders (HTTP 200) but **submitting** the form
  returns **400 Bad Request**; users cannot create/update from the frontend.
- **Root cause:** a `type="http"` controller route is CSRF-protected by default;
  a `<form method="post">` that omits the CSRF token is rejected.
- **Fix:** add `<input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>`
  to every frontend POST form (or set `csrf=False` on the route only when a token
  genuinely can't be supplied — rare, and a security trade-off).
- **Prevention [review]:** every website/portal `<form method="post">` must carry
  a `csrf_token`. Candidate lint: *portal form POST without csrf_token → error.*
- **Origin:** helpdesk_community Bug C (1.0.4). Behavior-verified 19.0.

## AP-005 — search filters/groups without a `string` show technical names

- **Symptom:** the search panel shows raw internal names (`my_tickets`,
  `unassigned`) instead of human labels.
- **Root cause:** a `<filter>` / `<separator>` / group-by has a `name=` but no
  `string=`, so Odoo falls back to the technical `name`.
- **Fix:** give every user-visible `<filter>` an explicit `string=` (localizable).
- **Prevention [review]:** grep views for `<filter` lacking `string=`. Candidate
  lint: *`<filter name=...>` with a domain/context but no `string` → warning.*
- **Origin:** helpdesk_community Bug E (1.0.4).

## AP-006 — mixed mail-template templating idioms

- **Symptom:** mail templates render literally / incorrectly (placeholders not
  interpolated), or fail on older series.
- **Root cause:** mixing `{{ }}` (inline_template, 15.0+ for char fields) with
  legacy `${ }` (jinja, ≤14) in the same template; jinja was replaced by
  qweb/inline_template in **15.0** (`odoo/tools/jinja.py` removed).
- **Fix:** author templates in the **canonical (modern) idiom** — `{{ }}` for
  inline char fields, QWeb `t-out`/`t-if`/`t-attf-*` for the HTML body — and let
  the Compatibility Layer (R-MAIL-001) emit the `${ }` + `% if %` jinja variant
  for **14.0** only.
- **Prevention [review]:** never hand-mix `{{ }}` and `${ }`; author modern, rely
  on R-MAIL-001 for ≤14. Render-smoke each series (14 exercises the jinja path).
- **Origin:** helpdesk_community mail templates (1.0.4). Docker-smoke-verified 14.0.

---

## How these feed the pipeline

- **[review]** items belong on the pre-commit authoring checklist and in module
  code review (ADR-003 Behavior tier).
- Where a pitfall is mechanizable it should graduate to a Planner default (emit the
  right widget/default/csrf automatically) or a `validate_odoo_syntax` lint rule,
  turning **[review] → [mechanized]** so future modules cannot re-introduce it.
