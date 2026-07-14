# Odoogen Error Code Registry

Every diagnostic emitted by the Odoogen quality pipeline carries a stable code
of the form `E<layer><nnn>`. Codes are a contract: an IDE, the MCP server, or a
CI log can print `See: E2002` and the reader resolves it here. Never break a
code once published.

## Namespace (do not cross)

| Prefix | Layer                | Responsibility                         | Where it lives |
|--------|----------------------|----------------------------------------|----------------|
| `E1xxx`| Semantic Validator   | business correctness (Intent level)    | pre-IR         |
| `E2xxx`| Compiler Validator   | structural consistency of artifacts    | Build / CodePass (Invariants 10–13) |
| `E3xxx`| Publisher Validator  | distribution correctness (Store desc, assets, packaging) | Publisher suite |
| `E4xxx`| Runtime / Harness    | runtime correctness (install, render)  | Install Harness |

New checks pick the next free number inside their own layer. A code must never
be reused outside its namespace.

## Governing principle — bug → invariant promotion

> Every production bug, once its root cause is understood, MUST be evaluated for
> promotion to a Compiler Invariant. A bug is only "closed" when the invariant
> that prevents its class is present in the quality gate.

This turns each expensive production incident into a permanent increase in
compiler quality, instead of a one-off local patch. The lifecycle:

```
production bug -> investigate -> root cause -> fix module
     -> generalize -> Invariant -> Compiler Gate
```

`E2001`–`E2003` are the first fruits of this principle (born from the Helpdesk
"menu invisible" incident, 2026-07-14).

## Environment invariant — Python interpreter

Tooling MUST NOT rely on `python` resolving from `PATH`:
- On CI the runner provides Python 3.12.
- On developer machines `python` may resolve to **Python 2.7** (observed
  2.7.9), which cannot run type-annotated / f-string code.

Invoke Python 3 explicitly: `py -3`, `sys.executable`, or a detected interpreter
path. The canonical interpreter is **3.12**. All pipeline scripts are
py2/py3-compatible as a safety net, but they must be launched with 3.x.

## Error schema

Each `E<code>.md` carries exactly these sections (the single source of truth):

```
## Meaning
## Why
## Example
## How to fix
## Severity      (Error | Warning)
## Invariant     (e.g. "13 -- Menu Visibility (ADR-013)" or "None")
```

`Severity` drives CI gating (Error blocks publish; Warning flags for review).
`Invariant` closes the trace `Bug -> E-code -> Invariant -> ADR`, so every
production incident links back to the rule that now prevents its class.

## API — one source, many consumers

`docs/errors/*.md` is the canonical knowledge base. **No other copy exists.**
`publisher/odoo_store/error_registry.py` is the only reader; CLI, IDE
extension, MCP tool and the docs site all call `get_error_info(code)` and
receive the same structured object:

```json
{
  "error_code":   "E2002",
  "message":      "Menu `groups` has no readable ACL",
  "meaning":      "...",
  "why":          "...",
  "example":      "...",
  "fix":          "...",
  "severity":     "Error",
  "invariant":    "13 -- Menu Visibility (ADR-013)",
  "documentation":"E2002"
}
```

Contract for every surface:
- **CLI** renders the text form (`python error_registry.py E2002`).
- **VS Code / Cursor extension** opens the Markdown / shows the parsed object.
- **Claude Code / agents** read `documentation` and may fetch the Markdown.
- **MCP tool** `get_error_info` returns the JSON object above verbatim — never
  free text alone. The compiler should emit `{"error_code", "message",
  "documentation"}`; the consumer expands via this registry.

> MCP exposure note: the Odoogen MCP server is a **frozen v1.0.0 public
> contract** (ADR-011). Adding `get_error_info` as a first-class MCP tool
> requires ADR -> RFC -> v2. Until then, the registry is consumed locally by
> CLI/IDE/agents and the compiler embeds the `{"error_code","message",
> "documentation"}` object; the frozen MCP continues to return codes as today.

## Index

- [E2001](E2001.md) — Menu → model has no readable ACL (invisible to all)
- [E2002](E2002.md) — Menu `groups` has no readable ACL (audience locked out)
- [E2003](E2003.md) — Menu action unresolvable to a res_model
