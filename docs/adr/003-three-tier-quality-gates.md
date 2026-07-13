# ADR-003: Three-Tier Quality Gates (Build / Render / Behavior)

**Date**: 2026-07-13
**Status**: Accepted
**Scope**: All FoxPink modules (publisher-wide)
**Supersedes**: nothing · **Amends**: ADR-001 (DoD) and ADR-002 (adds a third tier + assigns per-tier ownership across the version matrix)

## Context

ADR-001 made **Install + Tests** a gate; ADR-002 added **Render Smoke** after
catching a class of browser-only defects (F-003 kanban OwlError, F-viewmode,
F-portal). During the 1.0.4 cycle a *fourth* class surfaced — defects that only
appear when a **real user performs an action**, invisible even to Render Smoke:

| ID | Defect | Why Render missed it |
| -- | ------ | -------------------- |
| **Bug A** | `helpdesk.category` `color` is Integer but the view used `widget="color"`, which posts a hex string → `ValueError: invalid literal for int()` on **save** | render paints the field fine; the crash is on the *write* RPC |
| **Bug B** | *Assign to me* stat button did not set `user_id` | button paints; only a *click* proves the handler |
| **Bug C** | portal ticket-create form POSTed with no `csrf_token` → **400** | the page renders (HTTP 200); the failure is on *submit* |
| **Bug D** | `stage_id` required with no client default → new-ticket form stuck **dirty**, Save silently blocked, stat buttons inert | form paints; only *filling + saving* exposes it |
| **Bug E** | search filters showed raw technical names (`my_tickets`) | the filter paints; label is only wrong to a *reading user* |

### The (next) false assumption

> "Install + Tests + Render green ⟹ the module works for a user."

Also **false**. Render proves the UI *paints*; it does not prove that
**create / write / click / submit** succeed. That is a distinct tier: **Behavior**.

## Decision

Adopt **three explicit, independent quality tiers**, each answering a different
question, and **assign ownership per tier across the version matrix**:

| Tier | Question it answers | Proven by | Owner |
| ---- | ------------------- | --------- | ----- |
| **Build** | Does it compile, test, and package? | Docker install `-i`, `--test-enable`, `build_market_release.ps1` | Compiler + Compatibility Layer |
| **Render** | Does the UI paint with no crash? | Playwright paint check (`render_smoke.ps1`), 0 OwlError/JS | Compatibility Layer |
| **Behavior** | Does a real user action succeed? | Playwright action UAT (CRUD, click, submit) + overflow proof; portable model-level assertions via `odoo shell` | Canonical branch |

### Coverage policy across the matrix (the key rule)

```
14.0 – 19.0 (all supported series):
    Build   ✅  (every series, every release)
    Render  ✅  (every series, every release)

Canonical (19.0) only:
    Behavior ✅  (full action UAT + overflow, every release)
```

**Rationale.** The **Compatibility Layer** owns *Render* — its whole job is to
emit series-valid UI (widgets that exist, view tags/tokens valid, templates that
parse) for 14–19, and Render Smoke is how that is proven per series. The
**Canonical branch** owns *Behavior* — business logic is authored once on 19.0
and is identical Python/data across series (the transforms are structural, not
behavioral), so exhaustive action-level UAT on 19.0 plus **portable model-level
assertions** (`odoo shell`, e.g. Bug A color-int write and Bug D default stage,
verified on 16.0 in 1.0.4) give sufficient evidence without re-authoring
selectors for every legacy web client.

### What Behavior UAT covers (that Render cannot)

- **Write/save RPCs** — the Bug A class (paints fine, crashes on write).
- **Handler side-effects** — button clicks that must mutate state (Bug B).
- **Form dirty/validation state** — required fields with no default (Bug D).
- **CSRF / HTTP POST flows** — portal & website form submits (Bug C).
- **User-facing copy** — filter/menu/field labels a human reads (Bug E).
- **Overflow / layout under interaction** — `scrollWidth == innerWidth` across
  screen sizes, popups, and models (18/19 chatter class, FA-008).

### When each tier MUST run

- **Build + Render**: every series 14–19, before **every** Engineering *and*
  Market Release (ADR-001 DoD table, all rows green).
- **Behavior**: on canonical 19.0 before **every** Engineering Release; plus the
  portable model-level assertions on at least one legacy series per Market Release.

## Consequences

- **DoD gains a third column.** The ADR-001 table is now Build / Render /
  Behavior. A series is "done" for Build+Render; the release is "done" only when
  canonical Behavior is also green.
- **Bugs A–E are recorded as authoring pitfalls** (see
  `docs/compatibility/AUTHORING_PITFALLS.md`) so future modules never re-introduce
  them; where mechanizable they become lint rules / Planner defaults.
- **Cost is bounded.** Full action UAT stays 19-only; legacy series pay only the
  cheap Render + shell-assertion cost. This is the deliberate reliability/speed
  balance ("act on hypothesis; update on evidence").
- **Phase 2 asset.** A cross-version Playwright abstraction (per-series adapters)
  would let Behavior UAT run on 14–18 too; deferred until several modules justify
  the shared *FoxPink Test Runtime* investment.

## Alternatives Considered

- **Behavior UAT on all 14–19 now.** Rejected for 1.0.x — legacy web clients
  (14–17) need bespoke selectors; marginal value is low because business logic is
  canonical and transforms are structural, already proven by Build+Render+shell.
- **Fold Behavior into Render Smoke.** Rejected — conflates "paints" with "works";
  ADR-002's own examples (Bug A/C paint at HTTP 200 yet fail on action) show they
  are distinct failure classes needing distinct gates.
- **Trust the test suite for Behavior.** Partial — `TransactionCase` proves ORM
  behavior (and does, for Bug A/D at model level) but never the web-client action
  path (Bug B/C/E). Kept as the model-level half of Behavior; UAT covers the UI half.
