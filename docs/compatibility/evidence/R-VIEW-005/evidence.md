# Evidence Pack — R-VIEW-005 (`states` / `attrs` attribute)

- **Pass:** ViewPass
- **Method:** primary source, grepped inside official `odoo:<series>` Docker images
  (2026-07-13): `odoo/addons/base/models/ir_ui_view.py` + `odoo/addons/base/rng/common.rng`.
- **Decision:** Draft → **Verified** · confidence **100%**
- **Correction:** original claim "removed in 19" is **WRONG** → recorded as FA-005.

## Claim under test
Original: "`states` attribute removed in **19**; golden must not emit it."

## Upstream citations
`ir_ui_view.py` — how `states` is treated:

- **16.0** (`ir_ui_view.py:89-96`): `states` is *processed* — popped from the node
  and converted into `invisible` modifiers:
  ```python
  states = node.attrib.pop('states', None)
  if states:
      states = states.split(',')
      ... modifiers['invisible'].append(('state', 'not in', states))
  ```
- **17.0 / 18.0 / 19.0** (`ir_ui_view.py`): hard validation error —
  ```python
  if combined_arch.xpath('//*[@attrs]') or combined_arch.xpath('//*[@states]'):
      err = ValidationError(_('Since 17.0, the "attrs" and "states" attributes are no longer used. ...'))
  ```

`common.rng` `<group>` element define (mirror confirmation):

| series | `attrs` | `states` |
| ------ | :-----: | :------: |
| 16.0 | ✓ (L317) | ✓ (L321) |
| 17.0 | ✗ | ✗ |
| 18.0 | ✗ | ✗ |
| 19.0 | ✗ | ✗ |

## Boundary
**17.0.** `attrs` and `states` are accepted (and transformed) up to 16.0 and
**rejected with ValidationError from 17.0 onward** — not 19.0.

## Impact
- Compiler pass: ViewPass.
- Golden (19) already omits `states`/`attrs`, so no transform is needed when
  building down. This is a **golden-authoring constraint / lint**, not a build
  transform for this module.
- **Surfaces a real gap → R-VIEW-008:** the 17.0 change also removed the old
  `attrs="{'invisible': domain}"` mechanism in favour of `invisible="<domain>"`.
  A module that uses *dynamic* modifiers on the golden would need those rewritten
  back to `attrs` for ≤16. See R-VIEW-008 (Draft).

## Regression risk
**Low** for this rule as a lint. **Unknown/Medium** for the associated R-VIEW-008
transform (not yet mapped) — flagged as Unknown rather than assumed handled.

## Exercised by golden?
Golden helpdesk-community uses **0** dynamic `invisible/attrs/readonly/required`
conditions (only one static `required="True"` on a portal HTML input). So neither
this lint nor R-VIEW-008 is exercised by module #1.
