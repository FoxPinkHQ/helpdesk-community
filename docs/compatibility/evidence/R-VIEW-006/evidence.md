# Evidence Pack — R-VIEW-006 (`<group expand>` in search)

- **Pass:** ViewPass
- **Method:** primary source, official `odoo:<series>` Docker images (2026-07-13):
  `odoo/addons/base/rng/common.rng` (`<group>` define) + `search_view.rng`.
- **Decision:** Draft → **Verified** · confidence **100%**

## Claim under test
"Search `<group expand="...">` removed in **19**; golden must not emit it."

## Upstream citations
`search_view.rng` references the shared `<group>` define
(`<rng:ref name="group"/>`) in `common.rng`, so a `<group>` inside `<search>`
validates against that define. The `expand` attribute on the `<group>` define:

| series | `expand` on `<group>` | source line |
| ------ | :-------------------: | ----------- |
| 16.0 | ✓ | common.rng L320 |
| 17.0 | ✓ | common.rng L301 |
| 18.0 | ✓ | common.rng L301 |
| 19.0 | ✗ (removed) | absent from group define (L295+) |

(The `expand` attribute still exists on the `<field>` define in 19 — that is a
different element and out of scope for this rule.)

## Boundary
**19.0.** `expand` on `<group>` is accepted 16.0–18.0 and **absent from the 19.0
RNG group schema** → a `<group expand>` fails view validation on 19.

## Impact
- Compiler pass: ViewPass.
- Golden (19) must not emit `expand` on `<group>` (would fail install). Building
  down to 14–18, those series accept a group without `expand` → **no transform**.
  Golden-authoring constraint / lint.

## Regression risk
**Low.** Schema-level, one boolean presence check.

## Exercised by golden?
Golden helpdesk-community has no `<group expand>` in its search view → constraint
already satisfied; not a build blocker for module #1.
