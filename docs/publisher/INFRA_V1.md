# FoxPink Publisher Infrastructure — v1.0 (FROZEN)

> **Status: FROZEN.** This is the baseline. Do **not** invest further in
> publisher infrastructure (compiler/passes/CI/release tooling) unless there is a
> concrete bug or a real, validated need (e.g. ~20-30 modules before a self-hosted
> runner + heavy CI is worth it). From here, all effort goes to **modules**.
>
> Business value now lives in module count + quality on Odoo Apps Store, not in
> making the pipeline 5% better.

## What is in the frozen v1.0 baseline

| Component | State | Where |
| --------- | ----- | ----- |
| **Brand kit** | publisher name `FoxPink`, LGPL-3, multi-version policy | `LICENSE`, `__manifest__.py`, `MARKET_RELEASE_CHECKLIST.md` |
| **Repository rules** | canonical-first, per-series artifacts, 5-token README | `docs/publisher/PER_SERIES_REPOSITORY_RULES.md` |
| **Compiler (CodePass)** | per-series module transforms | build toolchain (`build_version.ps1`) |
| **Compatibility Layer** | rule registry + matrix | `docs/compatibility/RULES.md`, `MATRIX.md`, `matrix.json` |
| **MetadataPass** | README/manifest/version projection + R4/R5 audit | `metadata_pass.ps1` |
| **ResearchPass** | per-branch version knowledge + release notes | `research_pass.ps1` |
| **PackagePass** | per-series ZIP + validation + SHA | `build_market_release.ps1` |
| **Audit CI (Fast Gate)** | mandatory consistency gate | `.github/workflows/pipeline.yml` + `ci/pipeline_audit.py` |
| **Release workflow** | tag + GitHub Release + per-series body | REST API + `research_pass.ps1 -ReleaseBodyOut` |
| **Submission workflow** | manual Apps Store step | `docs/STORE_SUBMISSION_GUIDE.md` |

## Pipeline shape (frozen)

```
Pipeline
├── Build      → CodePass → MetadataPass → ResearchPass → PackagePass
├── Audit ✅ CI (Fast Gate — fails closed, branch-protected on 19/18/16)
├── Validate   (Heavy Gate — manual, at release: unit + render-smoke + UAT + packaging + SHA)
└── Publish    (tag → GitHub Release → Apps Store manual step)
```

## Deferred (do NOT build yet)

- Render-smoke / Playwright inside GitHub Actions (too heavy per-push; revisit at
  scale with a self-hosted runner + Docker image cache + parallel matrix).
- Per-series CHANGELOG (no independent hotfix histories yet; canonical CHANGELOG
  suffices while every series is generated from canonical).
- Additional module-count-driven infra (shared release runner, module registry).

## Re-freeze trigger

Re-open infrastructure work only when: (a) a drift/bug breaks a real release, or
(b) module count justifies the Heavy-Gate CI investment. Otherwise: ship modules.
