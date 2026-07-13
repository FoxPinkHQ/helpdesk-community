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
| **Canonical-identical** | everything under `docs/`, `LICENSE`, `SPEC.md`, `BACKLOG.md`, `IMPLEMENTATION_PLAN.md`, `MARKET_RELEASE_CHECKLIST.md`, `.gitignore` | **byte-identical** on all branches (copied verbatim from canonical) |
| **Per-branch artifact** | `README.md`, the module folder (`<module>/…`) | **transformed** per series; each branch reflects *its own* series |

- `README.md` is an **artifact**, not documentation. On branch `X.0` it must
  reflect that series' branch, manifest, and release — exactly like the module
  code is transformed for that series.
- The module folder is transformed by the existing view/orm/manifest/test passes;
  `README.md` (and other metadata) is transformed by the **MetadataPass** (below).

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

## MetadataPass — README/metadata as a compiler pass

Today the builder runs, conceptually:

```
ModelPass → ViewPass → ORMPass → PackagingPass
```

We add **MetadataPass** so metadata stops being an exception and becomes just
another generated artifact:

```
ModelPass → ViewPass → ORMPass → MetadataPass → PackagingPass
```

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

## Operating procedure (until MetadataPass is fully in the builder)

1. Edit **only** canonical `19.0` (code + docs + canonical README).
2. Run the module passes to regenerate each series' module folder.
3. Run **MetadataPass** (`metadata_pass.ps1`) to project metadata per series.
4. Run the **R4 audit**; abort on any DRIFT.
5. Commit per branch, fast-forward push, then re-audit against **remote**.
6. Tag + release from canonical; attach the N validated artifacts.
