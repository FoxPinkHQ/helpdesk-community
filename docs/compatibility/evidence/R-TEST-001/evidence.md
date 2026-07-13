# Evidence Pack — R-TEST-001 (`TransactionCase` class-level env)

- **Pass:** TestPass
- **Method:** primary source (`odoo/tests/common.py`) + Docker 14 failure→fix.
- **Decision:** discovered during Docker validation → **Stable** · confidence **100%**

## Claim under test
A test class that uses `setUpClass` + `cls.env` on `common.TransactionCase` works
on 15–19 but **fails on 14.0** with
`AttributeError: type object '...' has no attribute 'env'`. For 14.0 it must
subclass `common.SavepointCase` instead.

## Upstream citations
`odoo/tests/common.py` class hierarchy:

| series | `TransactionCase` has `setUpClass`+`cls.env` | class that provides `cls.env` |
| ------ | :-----------------------------------------: | ----------------------------- |
| 14.0 | **NO** (only `setUp`+`self.env`, L693/704) | `SingleTransactionCase` (L720/727/736) → `SavepointCase` (L745) |
| 15.0 | **YES** (`setUpClass` L823, `cls.env` L832) | `SavepointCase` (L869) = deprecated alias merged into `TransactionCase` |

14.0 class boundaries (`grep '^class'`): `TransactionCase` 687, `SingleTransactionCase`
720, `SavepointCase(SingleTransactionCase)` 745. So on 14 the class-level env lives
on `SingleTransactionCase`/`SavepointCase`, not `TransactionCase`.
15.0: `SavepointCase` body carries the warning *"Deprecated class SavepointCase has
been merged into TransactionCase"*.

## Boundary
**15.0.** `TransactionCase` gained class-level `setUpClass`/`cls.env` in 15.0. ≤14
requires `SavepointCase`.

## Impact
- Compiler pass: TestPass.
- Transform (build 19→14): `common.TransactionCase` → `common.SavepointCase`
  (only when the class defines `setUpClass` and uses `cls.env`). Behaviour is
  equivalent (per-test savepoint rollback to the class fixture).

## Regression risk
**Low.** Symmetric class rename; `SavepointCase` on 14 provides the identical
class-fixture semantics that `TransactionCase` provides on 15+.

## Docker proof
- 14.0 **before** rule: `setUpClass ... has no attribute 'env'` → 1 error.
- 14.0 **after** rule: `0 failed, 0 error(s) of 14 tests`. (2026-07-13, `odoo:14.0`)
