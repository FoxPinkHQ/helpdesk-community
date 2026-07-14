# FoxPink Brand Guidelines (logo / banner / social prompts)

> **Publisher-wide standard.** Part of the frozen `INFRA v1.0` baseline — it
> applies to *every* FoxPink module, so it lives in the shared publisher docs, not
> in any one module. Every module Odoogen produces carries the same visual + copy
> discipline so the catalogue looks coherent on Odoo Apps, GitHub and social.
>
> **Rule:** module content changes per module; the *style* never does. A new module
> reuses these templates and only fills in the module name / purpose / features.

## The module asset contract

Every module ships these marketing artifacts alongside the code:

```
<module>/
├── logo_prompt.md        # prompt to generate the module icon
├── banner_prompt.md      # prompt to generate the README/blog banner
├── social_post_prompt.md # prompt to generate marketplace + social copy
├── static/description/
│   ├── icon.png          # generated from logo_prompt.md  (32-512, transparent)
│   ├── banner.png        # generated from banner_prompt.md (16:9)
│   └── screenshot_*.png  # real post-install screenshots
└── README.md
```

The three `*_prompt.md` are **source**; the PNGs are **generated** from them. Keep
the prompts in the repo so a future design pass is reproducible.

## 1. Logo Prompt Template

Send to the design team or an image model.

```text
Design a clean, modern, minimal logo for an Odoo module.

Module name:
"<MODULE_NAME>"

Purpose:
"<ONE SENTENCE DESCRIPTION>"

Style:
- Modern SaaS / Enterprise software
- Flat vector
- Minimal geometric design
- No gradients
- Rounded corners
- Clean negative space
- Scalable from 32×32 to 512×512

Color palette:
- Primary: #2563EB (Blue)
- Secondary: #0F172A (Dark Navy)
- Accent: #F59E0B (Amber) only if needed

Visual direction:
- Create a simple abstract icon representing the module.
- Avoid literal illustrations.
- Avoid Odoo logo.
- Avoid company logos.
- Avoid text inside icon.

Deliverables:
- Square icon
- Transparent background
- Works on light and dark backgrounds
- Professional enterprise software appearance

Keywords:
Enterprise • ERP • Odoo • Productivity • Modern • Minimal • Vector
```

## 2. Banner Prompt Template

```text
Create a professional 16:9 English blog cover image introducing an Odoo module.

Style:
clean modern premium enterprise editorial design,
light cream or white background,
blue and navy accents,
minimal,
high-end SaaS marketing style.

Main title:
"<MODULE_NAME>"

Subtitle:
"<SHORT VALUE PROPOSITION>"

Feature tags:
"<FEATURE 1> • <FEATURE 2> • <FEATURE 3> • <FEATURE 4> • <FEATURE 5>"

Visual:
- Modern ERP dashboard
- Floating feature cards
- Workflow visualization
- Clean enterprise UI
- Abstract module icon
- Business process illustration
- Soft shadows
- Rounded cards

Workflow:
"<STEP 1>"
↓
"<STEP 2>"
↓
"<STEP 3>"

Small icons:
<LIST OF ICONS>

Requirements:
- English only
- Large readable typography
- Minimal text
- Premium SaaS marketing quality
- No official Odoo logo
- No company logos
- No watermark
- Suitable as GitHub README banner and blog cover
```

## 3. Social Post Prompt Template (added for the compiler platform)

Each module also ships marketplace + social copy so Odoogen emits the full
publishing kit, not just code.

```text
Write the launch copy for an Odoo module.

Module name:
"<MODULE_NAME>"

Purpose:
"<ONE SENTENCE DESCRIPTION>"

Key features:
<FEATURE 1>, <FEATURE 2>, <FEATURE 3>, <FEATURE 4>, <FEATURE 5>

Audience:
"<WHO USES IT>"

Produce, in English:
1. LinkedIn post (≤300 words, professional, 3 hashtags)
2. X (Twitter) post (≤280 chars, punchy, 2 hashtags)
3. Odoo Apps Store short description (≤280 chars)
4. Marketplace long description (≤120 words, benefit-led)
5. SEO meta description (≤160 chars)

Tone: confident, enterprise, no hype, no emoji.
No official Odoo logo claims; do not imply Odoo endorsement.
```

## How a new module uses this

1. Copy `logo_prompt.md` / `banner_prompt.md` / `social_post_prompt.md` from a
   previous module (or from this doc).
2. Fill `<MODULE_NAME>`, `<Purpose>`, features, workflow, audience.
3. Generate the PNGs and drop them in `static/description/`.
4. Capture real `screenshot_*.png` after install.
5. Done — visual + copy style is automatically on-brand.

This is a governance standard; changing the palette / typography here updates the
whole catalogue. Do not fork the style per module.
