# Per-Series Repository & Artifact Rules (publisher-wide)

> **Scope:** every FoxPink module repository, not just `helpdesk_community`.
> **What this is:** the rules that govern how a single canonical source becomes
> N per-series branches/artifacts. **What this is NOT:** submission/marketplace
> workflow — that lives in `docs/STORE_SUBMISSION_GUIDE.md`. These rules stay true
> even if the marketplace changes (Odoo Apps → GitLab → private registry).
>
> Governing idea:
>
> > **Not only code is an artifact. Everything a user or marketplace sees —
> > manifest, README, CHANGELOG, release notes, metadata — is an artifact
> > generated from the canonical source.**

---

## R1 — Canonical-first (single source of truth)

- All authoring happens on the **canonical branch only**: `19.0`.
- The series branches `18.0, 17.0, 16.0, 15.0, 14.0` are **never hand-edited**.
  They are *regenerated* from canonical by the builder. A manual commit on a
  series branch is a process violation (fix it on canonical, regenerate).
- Rationale: hand-editing N branches guarantees drift. One source, N outputs.

## R2 — Two file classes: `docs/` is identical, `README.md` is per-branch

| Class | Files | Cross-branch rule |
| ----- | ----- | ----------------- |
| **Canonical-identical** | most of `docs/` (`adr/`, `compiler/`, `architecture/`, `engineering/`, `compatibility/RULES.md`, `compatibility/MATRIX.md`, `compatibility/matrix.json`, …), `LICENSE`, `SPEC.md`, `BACKLOG.md`, `IMPLEMENTATION_PLAN.md`, `MARKET_RELEASE_CHECKLIST.md`, `.gitignore` | **byte-identical** on all branches (copied verbatim from canonical) |
| **Per-branch artifact** | `README.md`, `docs/compatibility/THIS_BRANCH.md`, the module folder (`<module>/…`) | **transformed** per series; each branch reflects *its own* series |

- `README.md` is an **artifact**, not documentation. On branch `X.0` it must
  reflect that series' branch, manifest, and release — exactly like the module
  code is transformed for that series.
- The module folder is transformed by the code passes; `README.md`/manifest/
  CHANGELOG are transformed by **MetadataPass**; per-branch *knowledge* is
  transformed by **ResearchPass** (both below).

### R2.1 — Knowledge is also two classes: canonical vs version

Not only code splits into identical/per-branch — **knowledge does too**. Failing
to split it means a series branch documents changes that only exist on another
series (e.g. `16.0` describing a `19.0`-only rule), which misleads readers and
contributors.

| Knowledge class | Files | Rule |
| --------------- | ----- | ---- |
| **Canonical knowledge** (version-independent) | `docs/adr/`, `docs/compiler/`, `docs/architecture/`, `docs/engineering/`, `docs/compatibility/RULES.md`, `docs/compatibility/MATRIX.md`, `docs/compatibility/matrix.json` (the full registry) | byte-identical on every branch |
| **Version knowledge** (per-branch state) | `docs/compatibility/THIS_BRANCH.md` (rendered), per-series release notes | reflects **that** series' applicable rules/transforms only |

- The **single source of truth** for version knowledge is the machine-readable
  `docs/compatibility/matrix.json` (canonical, on `19.0`). Humans edit the matrix;
  **ResearchPass** renders each branch's `THIS_BRANCH.md` and release note from it.
- A rule's per-series status (`Stable`/`Verified`/`Draft`, `applies_to`, `kind`)
  can change over time (e.g. a rule gets Docker-verified on `16.0`). You update it
  **once** in `matrix.json` on canonical, then regenerate — every branch's
  `THIS_BRANCH.md` becomes correct without hand-editing N branches.

## R3 — README: exactly FIVE tokens may change per series

Given a target series `S` (e.g. `16.0`) and version tail `V` (e.g. `1.0.4`), only
these tokens differ from canonical; **every other byte is identical** to the
canonical `README.md`:

| # | Token | Canonical (19.0) | On branch S |
| - | ----- | ---------------- | ----------- |
| 1 | Series tagline | `for **Odoo 19.0** ` | `for **Odoo S** ` |
| 2 | Version | `**Version:** 19.0.<V> ` | `**Version:** S.<V> ` |
| 3 | Clone branch | `git clone -b 19.0 ` | `git clone -b S ` |
| 4 | This build | `**This build:** Odoo 19.0 (` | `**This build:** Odoo S (` |
| 5 | Latest release | `Latest: **19.0.<V>**` | `Latest: **S.<V>**` |

**Hard constraint:** the supported-range/list text (`Odoo 14.0 – 19.0`,
`14.0, 15.0, 16.0, 17.0, 18.0, 19.0`) and any `docs/adr/…` / Releases URLs are
**not** tokens and must never be rewritten by series substitution. Substitution is
by **exact string**, never a blanket `19.0 → S` replace.

## R4 — Mandatory post-generation audit (fail-closed)

After regeneration, before push, the builder MUST verify for **every** branch that
these four agree:

```
branch name   ==   README series (tokens 1/3/4)   ==   manifest 'version' prefix   ==   README Version/Latest (tokens 2/5)
```

and that non-token content is byte-identical to canonical (only the module folder
and the 5 README tokens may differ). Any mismatch = **DRIFT**, abort the release.
The audit is also run against the **remote** after push (remote = source of truth).

## R5 — Encoding integrity

- README contains UTF-8 (`·` U+00B7, `→` U+2192, `✅`/`❌`). Substitution MUST
  preserve UTF-8 (no replacement chars `U+FFFD`, no lone `0xB7`).
- On Windows/PowerShell, read/write with explicit UTF-8; verify byte sequences
  (`C2 B7` for `·`) post-write. A corrupted glyph is a failed build.

---

## The compiler pipeline — everything the user sees is a generated artifact

The full builder is four kinds of pass. Code, metadata **and knowledge** are all
outputs of the canonical source; nothing about a series branch is hand-written.

```
                 Compiler (canonical 19.0 -> series S)
                 ┌───────────────────────────────────────────────┐
  canonical ───▶ │  CodePass  →  MetadataPass  →  ResearchPass  →  PackagePass │ ───▶ artifact(S)
                 └───────────────────────────────────────────────┘
```

| Pass | Owns | Output class |
| ---- | ---- | ------------ |
| **CodePass** | Model/View/ORM/Report/Security/Test transforms (the module folder) | per-branch code |
| **MetadataPass** | `__manifest__.py` version, `README.md`, `CHANGELOG.md`, listing metadata | per-branch metadata |
| **ResearchPass** | `docs/compatibility/THIS_BRANCH.md`, per-series release notes (from `matrix.json`) | per-branch knowledge |
| **PackagePass** | zip the validated tree into the release artifact | artifact |

> **Endpoint of the pipeline:** not only is *code* correct per version — the
> *knowledge shipped with each artifact* is correct for that artifact too. Branch
> `16.0` never contains documentation about a change that only exists on `19.0`.

## MetadataPass — README/metadata as a compiler pass

### MetadataPass responsibilities (per target series)

| Artifact | Transform |
| -------- | --------- |
| `__manifest__.py` `version` | prefix to `S.<V>` (already R-MANIFEST-001; folded here) |
| `README.md` | 5-token substitution (R3), byte-identical otherwise (R5) |
| `CHANGELOG.md` | series-aware "Latest" / version header projection (canonical body preserved) |
| release notes | rendered from the canonical CHANGELOG entry for `<V>` |
| listing metadata | `static/description/index.html` version matrix, badges |

### Contract

- **Input:** canonical source (`19.0`) + target series list + version tail.
- **Output:** per-series tree = canonical tree with (a) transformed module folder
  and (b) MetadataPass-transformed metadata; nothing else differs.
- **Invariant:** re-running MetadataPass is idempotent and passes the R4 audit.
- **Ownership:** MetadataPass is *Compiler responsibility*. Humans edit canonical;
  the pass produces every series. No human touches a series branch.

### Reference implementation

`metadata_pass.ps1` (in the module's build toolchain, alongside `build_version.ps1`)
implements the README half of MetadataPass today: canonical README → 5-token
substitution → R4/R5 audit → per-branch commit. It is the seed that later absorbs
CHANGELOG/release-notes/listing projection.

---

## ResearchPass — version knowledge as a compiler pass

Compatibility knowledge has a lifecycle of its own (a rule moves
`Draft → Verified → Stable`, and its `applies_to` set can change as more series
are Docker-verified). Propagating knowledge *blindly* from `19.0` would eventually
make a series branch lie about itself. ResearchPass renders per-branch knowledge
from a single canonical, machine-readable matrix.

### Input / output

- **Input:** `docs/compatibility/matrix.json` — canonical, on `19.0`. Each rule
  carries `pass`, `lifecycle`, `confidence`, `kind` (`transform`/`identity`/`lint`),
  `exercised` (by this module), `applies_to` (series the transform fires on),
  `boundary`, `summary`.
- **Output (per branch S):**
  - `docs/compatibility/THIS_BRANCH.md` — *what applies to `S` specifically*:
    back-transforms applied to build `S`, rules native on `S`, always-on golden
    lints, and rules documented-but-not-exercised (with "would fire on `S`?").
  - a per-series **release note** fragment (transforms applied vs golden `19.0`).
- `matrix.json`, `RULES.md`, `MATRIX.md` remain **canonical-identical** (the full
  registry); only `THIS_BRANCH.md` and release notes are version-specific.

### Contract

- **Single source of truth:** update rule state **once** in `matrix.json` on
  canonical; regenerate — every branch's `THIS_BRANCH.md` is corrected. Never
  hand-edit a series branch's knowledge.
- **Invariant:** idempotent; the ResearchPass audit checks (a) `matrix.json` is
  byte-identical across all branches, and (b) each `THIS_BRANCH.md` declares its
  own series and lists exactly the transforms `matrix.json` assigns to it.
- **Auto-apply gate is honoured:** only `Stable` rules count as "applied";
  `Verified`/`Draft` appear under *documented, not used* — never as an applied
  transform (Unknown > Wrong).

### Reference implementation

`research_pass.ps1` (build toolchain) renders `THIS_BRANCH.md` per branch and the
aggregated release body from `matrix.json`, then runs the ResearchPass audit.

---

## Operating procedure (until the passes are fully in the builder)

1. Edit **only** canonical `19.0` (code + docs + canonical README + `matrix.json`).
2. Run the code passes to regenerate each series' module folder.
3. Run **MetadataPass** (`metadata_pass.ps1`) to project metadata per series.
4. Run **ResearchPass** (`research_pass.ps1`) to project version knowledge per series.
5. Run the **R4 + ResearchPass audits**; abort on any DRIFT.
6. Commit per branch, fast-forward push, then re-audit against **remote**.
7. Tag + release from canonical; attach the N validated artifacts; set the release
   body from `research_pass.ps1 -ReleaseBodyOut` (per-series transforms).
