# ADR-002: Browser Rendering Validation (Render Smoke)

**Date**: 2026-07-13
**Status**: Accepted
**Scope**: All FoxPink modules (publisher-wide)
**Supersedes**: nothing · **Amends**: ADR-001 Definition of Done (adds a gate)

## Context

During Phase 2A (Market Packaging) of `helpdesk-community`, the module had already
passed the ADR-001 gate on all six series: **Install ✅ + Tests ✅ on Docker 14–19,
14/14 tests, 0 error.** By every signal we had, the golden was "green".

The moment we opened the module in a real browser (to capture Odoo Apps Store
screenshots on the canonical Odoo 19 instance), it broke in three independent ways
that **every automated check had missed**:

| ID | Failure (browser only) | Why tests missed it |
| -- | ---------------------- | ------------------- |
| **F-003** | Kanban `t-name="kanban-box"` throws OwlError `Missing 'card' template` on 19 → kanban does not render at all | OWL template resolution happens **client-side**; tests load the arch but never paint it |
| **F-viewmode** | `view_mode="tree,form"` invalid on 19 (`tree` view type removed → `list`); 3 config actions fail to open | action `view_mode` is validated at *open* time in the web client, not at install |
| **F-portal** | `base.group_portal` had a record rule but **no `ir.model.access.csv` ACL** → portal 403 Forbidden | no test logs in as a portal user and requests the portal route |

Recorded as **FA-006** in `docs/compatibility/KNOWN_FALSE_ASSUMPTIONS.md`.

### The false assumption

> "Install + Tests + Docker green ⟹ the module works on that series."

This is **false**. Odoo's `TransactionCase`/`SavepointCase` suites validate the
*registry and data* (models, fields, ORM behaviour, security in Python). They do
**not** render a view in a browser. An entire class of defects lives only in the
rendered UI and is therefore invisible to install + unit/integration tests.

## Decision

**Browser rendering is a first-class, independent quality gate** — "Render Smoke" —
inserted into the Definition of Done between `Tests` and `Package`:

```
Compile → Install → Tests → Render Smoke → Package → Store Validation
```

### What Render Smoke covers (that unit tests cannot)

- **OWL / QWeb client templates** — kanban card templates, custom OWL components,
  widget mounting (the F-003 class).
- **Action view-type validity** — `view_mode` tokens and view types actually
  supported by the target series' web client (the F-viewmode class).
- **Frontend / portal access** — `ir.model.access.csv` + record rules exercised by
  a real portal login on the actual route (the F-portal class).
- **Server-rendered QWeb** — portal/website templates (`t-out`, `t-field`, widgets)
  that only execute on an HTTP render.
- **Console / uncaught JS errors** — surfaced via the browser, never by Python tests.

### Tooling

- **Playwright + Chromium** is the standard Render Smoke driver (already used for
  Odoo 19 screenshot capture; the capture doubles as the 19 render smoke).
- Each smoke run **listens for `pageerror` (uncaught JS/OwlError) and the Odoo error
  dialog**, and asserts the expected view root element is present.

### Minimum Render Smoke checklist (per series)

For every supported Odoo series, in a browser against a live instance with the
module installed **with demo data**:

1. **Backend login** (admin) succeeds.
2. **Kanban** view of the primary model opens with **0 pageerror / 0 error dialog**.
3. **List** view opens.
4. **Form** view of one record opens.
5. **Search / filters** panel opens.
6. Each **menu action** opens without error.
7. **Portal**: a `group_portal` user opens the module's portal route(s) — HTTP 200,
   no 403, no 500, expected content present.

Render Smoke is **not** a full regression — it is a fast "does the UI paint?" pass.
Functional depth stays with the test suite.

### When Render Smoke MUST run

- On the **canonical 19** golden before any Engineering Release.
- On **every series 14–19** before a **Market Release** (all rows green in the
  ADR-001 DoD table).
- Whenever a change touches: views/OWL/QWeb, `view_mode`/actions, security ACLs or
  record rules, portal/website templates, or asset bundles.

## Consequences

- **DoD gains a gate.** ADR-001's table now has a `Render Smoke` column; a series is
  not "done" until it is green. Engineering Release requires 19 render-green;
  Market Release requires 14–19 render-green.
- **New compatibility rules can be born from render, not just source/tests.** F-003
  produced the corrected **R-VIEW-002** (kanban `card` boundary `<18`, hard error).
- **Compiler consequence.** Render-only failure modes (client template names,
  view-type tokens per series) become part of the Compatibility Layer's remit; the
  compiler must emit series-valid UI, and Render Smoke is how that is proven.
- **Cost.** Each series needs a runnable web instance + a short Playwright pass.
  Amortised publisher-wide across 40–50 modules via a shared smoke harness.
- **CI.** The CI pipeline (Phase 2C) will run Render Smoke per series alongside
  install + tests before producing the six Market ZIPs.

## Alternatives Considered

- **HTTP-status-only smoke (curl the routes).** Rejected — catches 403/500 (portal)
  but **not** client-side OwlError/kanban failures (F-003), which return HTTP 200.
- **`HttpCase` tours in the Python suite.** Partial — runs a browser, but tours are
  brittle, slow to author per module, and still miss views not covered by the tour.
  Kept as an *option* for deep flows; Render Smoke remains the mandatory baseline.
- **Trust deprecation warnings.** Rejected — F-003 logged a *deprecation warning* on
  18 (harmless) but a *hard error* on 19. Warnings do not indicate the boundary.
