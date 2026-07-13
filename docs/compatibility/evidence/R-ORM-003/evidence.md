# Evidence Pack — R-ORM-003 (aggregator → group_operator)

- **Pass:** TrackingPass (ORM)
- **Method:** primary source, grepped inside official `odoo:<series>` Docker images
  at `/usr/lib/python3/dist-packages/odoo` (2026-07-13).
- **Decision:** Draft → **Verified** · confidence **100%**

## Claim under test
Golden (19) declares field kwarg `aggregator=...`; targets ≤17 only understand
`group_operator=...`. Compiler must rename `aggregator` → `group_operator` for ≤17.

## Upstream citations
Counts in `odoo/fields.py` (14–18) / `odoo/orm/fields.py` (19):

| series | `aggregator` | `group_operator` | interpretation |
| ------ | -----------: | ---------------: | -------------- |
| 14.0 | 0 | 7 | only `group_operator` |
| 15.0 | 0 | 7 | only `group_operator` |
| 16.0 | 0 | 7 | only `group_operator` |
| 17.0 | 0 | 11 | only `group_operator` |
| 18.0 | 19 | 3 | `aggregator` primary; `group_operator` = deprecated alias |
| 19.0 | 13 (orm/fields.py) | 3 (orm/fields.py) | same as 18 |

Deprecation shim, identical in 18.0 (`fields.py:482`) and 19.0 (`orm/fields.py:487`):

```python
if 'group_operator' in attrs:
    warnings.warn("Since Odoo 18, 'group_operator' is deprecated, use 'aggregator' instead",
                  DeprecationWarning, ...)
    attrs['aggregator'] = attrs.pop('group_operator')
```

- ORM package restructured in 19.0: `odoo/fields.py` → `odoo/orm/fields.py`.
- `aggregator` absent from `odoo/` entirely on 17.0 (the two hits in 17 `models.py`
  are an unrelated local variable, not a field kwarg).

## Boundary
**18.0.** `aggregator` accepted 18.0+; `group_operator` still accepted as a
deprecated alias on 18/19 but is the *only* form on ≤17.

## Impact
- Compiler pass: TrackingPass.
- Transform (build 19→target): for series ≤17 rename kwarg `aggregator`→`group_operator`.
  For 18 keep `aggregator` (native). One mechanical, reversible rename.

## Regression risk
**Low.** Pure kwarg rename, symmetric deprecation path, documented by upstream
warning text itself.

## Exercised by golden?
**No** — helpdesk-community declares no `aggregator` field. Rule proven by source,
awaits a Docker run on a module that uses it before → Stable.
