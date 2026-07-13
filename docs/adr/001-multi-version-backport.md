# ADR-001: Multi-Version Backport Strategy

**Date**: 2026-07-13
**Status**: Accepted
**Scope**: All FoxPink modules

## Context

Single-version (19-only) limits market reach. Odoo users on 14–18 are a large installed base. Multi-version support is a key differentiator on Odoo Apps Store.

## Decision

- **Source of truth**: Odoo 19 (all feature development happens here)
- **Backport pipeline**: 19 → 18 → 17 → 16 → 15 → 14 (sequential, not parallel)
- **Git branches**: `19.0` (primary dev), `18.0`, `17.0`, `16.0`, `15.0`, `14.0` (maintenance)
- **Release gate**: All 6 versions must pass before ANY version is published
- Each maintenance branch = 19.0 branch with version-specific compatibility patches on top

## Consequences

- Feature development only on 19. Backports are mechanical (API adapters, XML transforms).
- Bug fixes: fix on 19, then cherry-pick down the pipeline.
- Compiler must have a **Version Compatibility Layer** producing artifacts per target.
- **One commit → six artifacts**: CI pipeline builds 6 ZIPs per module.
- Backport 19→14 should take ≤1 week per module (KPI).
- Code variance across versions must be <5% (KPI).

## Definition of Done (revised)

| Version | Install | Tests | Package |
|---------|:-------:|:-----:|:-------:|
| 19      | ✅      | ✅    | ✅      |
| 18      | ✅      | ✅    | ✅      |
| 17      | ✅      | ✅    | ✅      |
| 16      | ✅      | ✅    | ✅      |
| 15      | ✅      | ✅    | ✅      |
| 14      | ✅      | ✅    | ✅      |

Release is created only when the full table is green.

## Alternatives Considered

- **Parallel development**: Rejected — 6x bug-fix surface.
- **Single branch with compat layer**: Rejected — too complex for Odoo XML/security differences.
