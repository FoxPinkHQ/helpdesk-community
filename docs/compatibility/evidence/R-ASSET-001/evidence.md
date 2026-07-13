# Evidence Pack — R-ASSET-001 (manifest `assets` key)

- **Pass:** AssetPass
- **Method:** primary source, official `odoo:<series>` Docker images (2026-07-13).
- **Decision:** Draft → **Verified** · confidence **95%**

## Claim under test
The manifest `assets` dict (`{'web.assets_backend': [...]}`) is understood from
15.0 onward. For 14.0 the compiler must instead emit an XML bundle
`<template inherit_id="web.assets_backend">`.

## Upstream citations
The `assets` manifest key is backed by the `ir.asset` model
(`odoo/addons/base/models/ir_asset.py`):

| series | `ir_asset.py` present |
| ------ | :-------------------: |
| 14.0 | **MISSING** |
| 15.0 | FOUND |
| 16.0 | FOUND |

Without `ir.asset`, a 14.0 module's manifest `assets` dict has no loader — assets
must be declared the legacy way (XML template inheriting `web.assets_backend`).

## Boundary
**15.0.** `assets` manifest key works 15.0+; 14.0 requires the XML template bundle.

## Impact
- Compiler pass: AssetPass.
- Transform (build 19→14): convert manifest `assets` dict into an
  `<template inherit_id="web.assets_backend">` XML file; drop the manifest key.
- Only relevant to modules that ship frontend assets (OWL/JS/CSS).

## Regression risk
**Medium.** Ordering and load-sequence differences between manifest `assets` and
legacy XML bundles can subtly change asset order; needs a real OWL module +
Docker 14 render to reach Stable. Confidence held at 95% (model-file presence is
definitive for *availability*, but the transform output is not yet runtime-tested).

## Exercised by golden?
**No** — helpdesk-community ships no OWL/frontend assets. Confirm with module #2
(a module that has an `assets` manifest key) before → Stable.
