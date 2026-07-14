# Publisher Acceptance Test (Odoo Apps Store target)

Every module published to the Odoo Apps Store must pass this 3-stage gate
before it is considered **Publisher Platform v1.0 complete** and reusable for
any Odoo module Odoogen generates.

```
Validator PASS        (automated — publisher/odoo_store/validator.py)
        ↓
Preview PASS          (manual — Odoo Apps Store description preview)
        ↓
Store PASS            (manual — after submission / review)
```

## Stage 1 — Validator PASS (automated)

`python publisher/odoo_store/validator.py helpdesk_community/static/description/index.html`
must return `PASS`: no kill tags, only whitelisted inline styles, no external
web-fonts, only relative image paths.

Plus `python publisher/odoo_store/acceptance.py <index.html>` (asset pre-flight):
every referenced image and `icon.png` must exist on disk.

## Stage 2 — Preview PASS (manual, on apps.odoo.com)

The module author logs into the Odoo Apps publisher, opens the description
preview and confirms:

- [ ] Banner displays correctly (no broken image, correct aspect).
- [ ] Icon displays correctly.
- [ ] No HTML appears stripped (no raw tags, no missing sections).
- [ ] Layout is not broken (cards/columns render as intended).

## Stage 3 — Store PASS (manual, after submission)

- [ ] Mobile preview looks fine (store frontend is responsive/Bootstrap 4).
- [ ] No warning from Odoo Apps review about the description.

## When is Publisher Platform v1.0 complete?

All 6 checks green → the description is proven correct on the real store
renderer, and the Publisher Platform (template + rules + validator + acceptance)
is promoted to **v1.0** and reusable for every future module.

Until Stage 2/3 are confirmed by a real Store preview, the platform is `9.8/10`
(per RC5 review): the automated quality gate is in place, the manual
confirmation is the only remaining gap.
