# Odoo Apps Store — HTML Description Sanitization (Research)

> Source of truth: `odoo.tools.html_sanitize` (used by the app store to render
> `static/description/index.html`). This is an XSS/consistency filter, NOT a
> full HTML renderer.

## Why Odoo "does not understand" your styles

1. **Tag kill list** — removed entirely:
   `base, embed, frame, head, iframe, link, meta, noscript, object, script, style, title`
   → Your `<head>`, `<style>` block and Google-Fonts `<link>` are ALL deleted.
2. **Custom CSS classes die** — `class` attributes are kept, but the `<style>`
   that defines `.hero/.card/.grid/.badge/...` is gone, so those classes do nothing.
3. **Inline `style` kept ONLY for a whitelist of properties** (below). Anything
   else (`box-shadow`, `linear-gradient`, `transition`, `transform`,
   `grid-template-*`, `@media`, ...) is dropped.
4. **External resources**: `<link>` killed; relative image paths
   (`banner.png`) resolve under `static/description/` and work. External URLs in
   `href` are restricted — only youtube / microsoft-teams / `mailto:` / `skype:`
   allowed; arbitrary external links are invalidated by store review.

## Allowed inline-style property whitelist

```
font-size, font-family, font-weight, background-color, color, text-align,
line-height, letter-spacing, text-transform, text-decoration, opacity,
float, vertical-align, display,
padding (+ -top/-left/-bottom/-right),
margin (+ -top/-left/-bottom/-right),
white-space,
border, border-color, border-radius, border-style, border-width,
border-top/bottom/left/right (+ -style/-color/-width/-left-radius/-right-radius),
height, width, max-width, min-width, min-height,
border-collapse, border-spacing, caption-side, empty-cells, table-layout
```

Note: `background` (shorthand) and `box-shadow` are NOT whitelisted →
use `background-color` only; drop shadows.

## What survives for layout

- **Odoo `oe_*` classes** (defined by Odoo's web description CSS, guaranteed):
  `oe_container, oe_row, oe_spaced, oe_slogan, oe_picture, oe_screenshot,
  oe_demo, oe_span6 / oe_span4 / oe_span12, oe_mt* , oe_mb* , oe_dark,
  oe_separator`.
- **Bootstrap 4 utility classes** (store frontend is Bootstrap 4): `container,
  row, col-md-6, d-flex, justify-content-*, align-items-*, text-center,
  text-justify, mb-4, mt-4, p-3, bg-light, rounded, border, shadow-sm,
  text-primary, font-weight-bold, img-fluid, badge, table`.

## Correct pattern (long-term, maintainable)

- No `<html>/<head>/<style>/<link>/<title>`. Start at `<div class="oe_container">`
  or `<div class="container">`.
- Layout via `oe_row` + `oe_span6` OR Bootstrap `row` + `col-md-6`.
- Brand color via inline `style="color:#6D28D9;"` / `style="background-color:#F5F3FF;"`.
- Cards/boxes: `style="border:1px solid #EDE9FE; border-radius:10px; padding:18px; background-color:#FAFAF9;"`.
- Images: `<img class="img-fluid rounded" src="banner.png">` (relative path).
- Fonts: cannot embed web fonts; rely on system stack
  (`style="font-family:Arial, sans-serif;"` if desired — no external load).
- Must be English; no JS; no external links except youtube/msteams; `mailto:` ok.
- `display:flex` survives (property whitelisted) but `justify-content/align-items`
  are stripped → use Bootstrap `d-flex justify-content-between align-items-center`
  instead of raw flex.

## Validation

The store applies the sanitizer server-side; a local browser preview is NOT
representative. Quick mental check: delete every `<style>/<link>`, keep only
whitelisted inline props — that is the rendered result.
Reference: Odoo's own `addons/crm/static/description/index.html`.

## Deliverable

`STORE_DESCRIPTION_TEMPLATE.html` — Odoo-compliant body. Copy its content into
`helpdesk_community/static/description/index.html` when ready to update.
