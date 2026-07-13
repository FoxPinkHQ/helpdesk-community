# FoxPink Publishing Pipeline (publisher-wide)

> Companion to `PER_SERIES_REPOSITORY_RULES.md`. That file defines *what* the
> artifacts are; this file defines the *stages* every FoxPink module flows through,
> and which of them are **mandatory CI gates**. Designed to hold at 40-50 modules:
> every module takes the same path.

## Two layers

The **Compiler** turns canonical `19.0` into per-series artifacts (4 passes). The
**Pipeline** wraps the compiler with the discipline of *generate → prove
consistent → prove correct → release* (4 stages).

```
Pipeline
├── Build      →  Compiler:  CodePass → MetadataPass → ResearchPass → PackagePass
├── Audit      →  consistency invariants   (MANDATORY CI GATE)
├── Validate   →  correctness              (tests · render-smoke · packaging)
└── Publish    →  tag · GitHub Release · Apps Store
```

| Stage | Question it answers | Owns | Where it runs today |
| ----- | ------------------- | ---- | ------------------- |
| **Build** | "Are the artifacts generated from canonical?" | CodePass, MetadataPass, ResearchPass, PackagePass | local build toolchain (`build_version.ps1`, `metadata_pass.ps1`, `research_pass.ps1`) |
| **Audit** | "Are the artifacts *consistent* with the canonical source?" | R4/R5 (metadata), ResearchPass audit, canonical-knowledge identity, matrix uniqueness | **GitHub Actions** (`.github/workflows/pipeline.yml` → `ci/pipeline_audit.py`) — **required** |
| **Validate** | "Are the artifacts *correct*?" | unit tests, Playwright render-smoke (14-19), packaging validation | local Docker matrix + `build_market_release.ps1` (heavy; not on free CI yet) |
| **Publish** | "Ship it." | tag, GitHub Release body (`research_pass.ps1 -ReleaseBodyOut`), Apps Store submission | REST API + manual Apps Store step |

## Why Audit is separated from Validate

- **Audit = consistency** (fast, deterministic, no runtime): does branch `16.0`
  actually reflect `16.0` (README tokens, manifest, `THIS_BRANCH.md`), is canonical
  knowledge byte-identical, is `matrix.json` a single blob? This catches the whole
  class of *"edited `matrix.json` but forgot to regenerate"* / *"README drift on one
  branch"* bugs **before** anything expensive runs.
- **Validate = correctness** (slow, needs Odoo + a browser): install, tests, and a
  real render. Kept separate so a cheap consistency failure never wastes a Docker
  matrix run.

If **Audit** fails, the pipeline stops — no artifact is produced or published.

## The mandatory CI gate

`ci/pipeline_audit.py` (stdlib-only, cross-platform) runs on every push to a series
branch and on pull requests. It reads committed content directly from git refs and
enforces:

1. **MetadataPass (R4/R5)** — per branch: `tag/clone/build == branch`,
   `version/latest/manifest == <branch>.<tail>`, supported-range preserved, UTF-8 intact.
2. **ResearchPass** — per branch: `THIS_BRANCH.md` declares its own series and lists
   exactly the `Stable`+exercised transforms `matrix.json` assigns to it;
   `matrix.json` is byte-identical across all branches.
3. **CanonicalKnowledge** — the version-independent docs + CI files are byte-identical
   across all branches.

Run locally the same way CI does:

```
git fetch origin '+refs/heads/*:refs/remotes/origin/*'
python ci/pipeline_audit.py --ref-prefix origin/
```

## Roadmap

- Fold **Validate** (render-smoke) into CI once a self-hosted / container runner
  with the Odoo images is available.
- Per-series CHANGELOG stays **out of scope** until series grow independent
  hotfix histories (today every series is generated from canonical, so a single
  canonical CHANGELOG is sufficient).

## Enforcement (applied)

The audit is **not advisory** — it is a required status check via branch
protection. As of `19.0.1.0.4`:

- Branch protection with **required status check** `Audit gate (MetadataPass +
  ResearchPass + canonical knowledge)`, `strict=true`, `enforce_admins=true`,
  force-pushes/deletions disabled on: `19.0`, `18.0`, `16.0` (representative
  canonical + older series; extend to 14/15/17 as the module count grows).
- Any push/PR whose commit fails `ci/pipeline_audit.py` is **blocked** — no
  artifact is built or published from a drifted branch. Drift is caught at the
  gate, not after merge.
