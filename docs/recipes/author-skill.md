# How to author a new skill

A runbook for adding a new `skills/<name>/SKILL.md` to this repo.

---

## 1. Skills are the universal common denominator (Rule 3)

Unlike agents, skills need **no** per-host translation and no adapter run — every host (Claude Code, opencode, GitHub Copilot, Cursor) can scan `**/SKILL.md` and read the same two frontmatter keys. Skills are already the "superset" for their asset class: there is no host-specific extra layer the way agent frontmatter has one (Rule 1 in [`docs/integrations/compatibility.md`](../integrations/compatibility.md)). That portability is only true if you never add host-only keys:

```yaml
---
name: <kebab-case-skill-name>
description: '<one sentence: what the skill covers, and — critically — which agent(s) consume it>'
---
```

**Never** add `tools`, `mode`, `permission`, `globs`, or any other host-only key to a `SKILL.md`. See the frontmatter compatibility matrix in [`docs/integrations/compatibility.md`](../integrations/compatibility.md) §1 for the full list of what's host-specific vs. universal.

## 2. Structure the body around "When to Use" → "Patterns" → "Indicators of Done"

Every skill in this repo follows the same shape so an agent can scan it predictably:

1. **Title + one-paragraph mission statement** — what "done" means for this domain, stated as a contract (not just a description).
2. **When to Use** — the triggers that should make an agent load this skill.
3. **Prerequisites** (if applicable) — what must already exist before this skill's workflow runs.
4. **Numbered pattern sections** (`## 1. <Pattern>`, `## 2. <Pattern>`, …) — each with a "Rules" subsection stating hard constraints, not just advice.
5. **Anti-Patterns** — the failure modes this skill exists to prevent.
6. **Indicators of Done** — a measurable target table.
7. **Boundaries** — `### Do` / `### Do Not Do` bullet lists.

Use [`skills/api-contract-first/SKILL.md`](../../skills/api-contract-first/SKILL.md) or [`skills/observability-three-pillars/SKILL.md`](../../skills/observability-three-pillars/SKILL.md) as reference implementations of this shape.

## 3. Name it for consumption, not just topic

The `description` field should name **which agent(s) consume it** — this is what lets an agent's "Always load" line and the catalog docs stay honest about ownership. Example:

```yaml
description: 'Golden outputs, model-graded evals, scorer matrix, CI integration — the canonical prompt evaluation and regression-testing skill consumed by Prompt File Author and QA Tester.'
```

## 4. Validate the frontmatter

```bash
python3 - <<'EOF'
import yaml, re
text = open("skills/<name>/SKILL.md").read()
fm = re.match(r"^---\s*\n(.*?\n)---\s*\n", text, re.S).group(1)
data = yaml.safe_load(fm)
assert set(data.keys()) == {"name", "description"}, f"extra keys: {set(data.keys()) - {'name','description'}}"
print("OK")
EOF
```

This is exactly what `scripts/validate-assets.py` checks in CI.

## 5. Wire it into the agent(s) that consume it

Add an "Always load" line (or a conditional load line, if the skill isn't always needed) to the consuming agent's `## Always Load` / `## Mandatory Skill Invocation Protocol` section — see how `agents/PromptFileAuthor.agent.md` conditionally loads `skills/prompt-eval-and-regression/SKILL.md`.

## 6. Register it in the catalogs

- `docs/README.skills.md` (skills table + count in the intro line)
- `AGENTS.md` §5 (the consuming role's "Load" column)
- `docs/opencode.json` — usually nothing to do; `skills.paths` globs `./skills` automatically (zero-copy).

```bash
ls skills/*/SKILL.md | wc -l
python3 scripts/validate-assets.py
```

## Copy-paste skeleton

```markdown
---
name: <kebab-case-name>
description: '<what it covers> — the canonical <domain> skill consumed by <Agent A> and <Agent B>.'
---

# <Title>

<One-paragraph mission statement — what "done" means for this domain>

---

## When to Use

- <trigger 1>.
- <trigger 2>.

## Prerequisites

- <precondition, if any>.

---

## 1. <Pattern Name>

<description>

### Rules

- <hard constraint>.

---

## Anti-Patterns

- <failure mode this skill prevents>.

## Indicators of Done

| Indicator | Target |
|-----------|--------|
| <indicator> | <target> |

## Boundaries

### Do

- <always-do rule>.

### Do Not Do

- <never-do rule>.
```
