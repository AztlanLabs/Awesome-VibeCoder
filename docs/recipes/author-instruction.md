# How to author a new instruction

A runbook for adding a new `instructions/<name>.instructions.md` to this repo.

---

## 1. Instructions are glob-scoped, not agent-scoped

Unlike agents and skills, instructions are matched to **files**, not roles — any agent (or Copilot directly) can pull one in when it touches a matching path. That's what the `applyTo` frontmatter field is for:

```yaml
---
description: '<one sentence: what conventions this file enforces>'
applyTo: '**/*.tsx, **/*.ts, **/*.jsx, **/*.js'
---
```

Only two frontmatter keys are used across the repo: `description` and `applyTo` — like skills, instructions need no host-specific "superset" layer and no `scripts/agent-frontmatter-adapter.py` run (that adapter exists only to translate agent frontmatter, per Rule 1 of [`docs/integrations/compatibility.md`](../integrations/compatibility.md)). Keep it that simple — see the same doc for how `applyTo` maps to each host (Copilot reads it natively; Cursor maps it to `globs:`; Claude Code/opencode load instructions on demand by reference from `AGENTS.md`, not via glob-matching).

## 2. Scope the glob precisely

- Prefer the narrowest glob that actually covers the convention's applicability — `**/*.tsx, **/*.ts` for a React/TypeScript rule, not `**`.
- Reserve `applyTo: "**"` for genuinely repo-wide concerns (see [`instructions/a11y.instructions.md`](../../instructions/a11y.instructions.md), [`instructions/security-and-owasp.instructions.md`](../../instructions/security-and-owasp.instructions.md)).
- If an instruction should be excluded from a specific agent mode (e.g. code review), add `excludeAgent` — see [`docs/integrations/github-copilot.md`](../integrations/github-copilot.md) Step 2.

## 3. Write body content as enforceable rules, not prose advice

Instruction files are the most terse asset class in the repo — no canonical section structure is enforced, but the strongest existing files (e.g. `instructions/security-and-owasp.instructions.md`) state each rule as a concrete MUST/SHOULD with a short rationale, not a paragraph of general advice. Prefer:

```markdown
- **MUST**: <concrete, checkable rule>. <why, in one clause>.
```

over:

```markdown
It's generally a good idea to think about ways this could be more secure...
```

## 4. Validate the frontmatter

```bash
python3 scripts/validate-assets.py
```

`validate-assets.py` checks every `instructions/*.instructions.md` file for valid YAML frontmatter and a present `applyTo` key.

## 5. Register it in the catalog

- `docs/README.instructions.md` — add a row to the "Representative Files" table if it's broadly useful, and confirm the intro line's file count.
- `docs/opencode.json` — add to the curated `instructions:` array only if it should be loaded by default for every session (most instructions are referenced on-demand instead — see `docs/integrations/opencode.md` Step 3).
- If the instruction is specific to one role, add a line to that role's agent body or skill file pointing at it (e.g. `sdlc-code-reviewer.agent.md` consumes `instructions/code-review-generic.instructions.md`).

```bash
ls instructions/*.instructions.md | wc -l
python3 scripts/validate-assets.py
```

## Copy-paste skeleton

```markdown
---
description: '<what conventions this file enforces>'
applyTo: '<glob pattern(s), comma-separated>'
---

# <Title>

You are an expert in <domain> with deep software engineering expertise.

## <Convention Category 1>

- **MUST**: <rule>. <rationale>.
- **SHOULD**: <rule>. <rationale>.

## <Convention Category 2>

- **MUST**: <rule>. <rationale>.
```
