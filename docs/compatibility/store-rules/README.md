# Store Rules — the Odoo Apps Store as a compiler backend

The Compatibility Layer teaches the compiler how to target six Odoo *runtimes*.
The **Store Rules** teach it how to target one more backend: the **Odoo Apps
Store** itself. A module that installs and renders on 14–19 can still be rejected
because it violates a *distribution* constraint (repo layout, branch naming,
description language, asset format). Those constraints are captured here as
`STORE-xxx` rules so neither humans nor the compiler rediscover them per module.

## Rule lifecycle (same invariant as compat rules: Unknown > Wrong)

`Draft → Verified → Stable`, plus `Rejected`. A rule reaches **Verified** only
when it is proven from an official Odoo source (Vendor Guidelines / FAQ / Upload
page / manifest reference) or from a real submission outcome recorded in
`STORE_REVIEW_NOTES.md`. Only **Stable** rules are treated as hard gates in
`STORE_SUBMISSION_GUIDE.md`.

## Sources of truth

- https://apps.odoo.com/apps/vendor-guidelines
- https://apps.odoo.com/apps/upload
- https://apps.odoo.com/apps/faq
- https://www.odoo.com/documentation/19.0/developer/reference/backend/module.html

See `RULES.md` for the current rule set.
