# How to author a new agent

A runbook for adding a new `agents/<name>.agent.md` to this repo. See [`docs/integrations/compatibility.md`](../integrations/compatibility.md) for the full cross-host analysis this recipe is extracted from.

---

## 1. Pick a bucket

Every role maps onto exactly one of three write-surface buckets — this decides its default tool/permission preset across hosts:

| Bucket | Who | Edit surface |
| --- | --- | --- |
| `implementation` | Developer, Backend/Frontend/Full Stack Engineer, DB Developer, Cybersecurity Developer, QA Tester, DevOps Engineer | full repo edit |
| `research` | Software Architect, UX/UI Designer, Accessibility Specialist, DB Architect, API Designer, Cybersecurity Architect, Product Manager, Responsible AI, Scrum Master | `.sdlc/**` + `docs/**` only |
| `review` | Code Reviewer, Repository Path Auditor, Agent Governance Reviewer | read-only, `edit: deny` |

List the exact tool/permission presets for each bucket:

```bash
python3 scripts/agent-frontmatter-adapter.py --list-buckets
```

## 2. Author the source in superset frontmatter (Rule 1)

Keep the repo's Copilot-style `tools:` field — it's the portable superset every host either reads or silently drops:

```markdown
---
name: 'SDLC: <Role Name>'
description: '<one sentence: domain, key nouns, "works standalone or as part of an SDLC team">'
tools: [vscode, execute, read, agent, edit, search, web, browser, ms-python.python/getPythonEnvironmentInfo, ms-python.python/getPythonExecutableCommand, ms-python.python/installPythonPackage, ms-python.python/configurePythonEnvironment, todo]
---
```

For a `review`-bucket agent, drop `edit`/`execute`-style tools that would imply write access — see an existing example in [`agents/sdlc-code-reviewer.agent.md`](../../agents/sdlc-code-reviewer.agent.md).

## 3. Write the canonical 7-section body

Follow the structure already used by every `sdlc-*.agent.md` file:

1. **Role intro** — one paragraph, who this agent is and what it owns.
2. **Always load** — the mandatory skills (always `skills/sdlc-shared-memory/SKILL.md` plus the role's matching skill).
3. **Core Workflow** — numbered startup → task → build/test → handoff sequence.
4. **Patterns, Rules & Structures** — named industry patterns and process rules (the "how/which").
5. **Indicators of Done (`<role>`)** — a measurable target table (build green, tests cited, contract state).
6. **Definition of Done** (implementation roles only) — the narrative gate requiring a real build/test run cited in `progress.md`.
7. **Boundaries (Do / Do Not)** — explicit scope fences.

Reuse an existing agent in the target bucket as your starting skeleton rather than writing from scratch — e.g. [`agents/sdlc-api-designer.agent.md`](../../agents/sdlc-api-designer.agent.md) (research), [`agents/sdlc-backend-engineer.agent.md`](../../agents/sdlc-backend-engineer.agent.md) (implementation), [`agents/sdlc-code-reviewer.agent.md`](../../agents/sdlc-code-reviewer.agent.md) (review).

## 4. Run the adapter

Never hand-translate per host. Regenerate the per-host files (or just validate with `--stdout`):

```bash
python3 scripts/agent-frontmatter-adapter.py --src agents/<name>.agent.md --stdout
```

Zero failures is the bar — this is exactly what CI (`.github/workflows/validate.yml`) checks for every agent on every PR.

## 5. Register it everywhere the catalog is counted

Adding an agent changes the count in five places — update all of them in the same commit:

- `AGENTS.md` §5 (role catalog table — add a row)
- `docs/README.agents.md` (catalog table + count in the intro line)
- `docs/opencode.json` (`agent:` block entry)
- `docs/README.sdlc-system.md` (role catalog table, if it's an `sdlc-*` role)
- `README.md` (role count line, if the project states a total)

Run the cross-cutting checklist from [`docs/implementation-plan.md`](../implementation-plan.md) to confirm every count reconciles:

```bash
ls agents/*.agent.md | wc -l
python3 scripts/validate-assets.py
```

## Copy-paste skeleton

```markdown
---
name: 'SDLC: <Role Name>'
description: '<domain summary>'
tools: [vscode, execute, read, agent, edit, search, web, browser, todo]
---

# SDLC <Role Name>

You are <persona>. <what you own, what you don't>.

## Always Load

- **Always load**: `skills/sdlc-<role>/SKILL.md`
- **Always load**: `skills/sdlc-shared-memory/SKILL.md`

## Core Workflow

1. Read `.sdlc/architecture.md` and the relevant `.sdlc/contracts/*.md` on startup.
2. <role-specific step>.
3. Build/run/test using `runTasks`/`runTests`; cite command + result in `.sdlc/progress.md`.
4. Create handoffs to downstream roles.

## Patterns, Rules & Structures

- <named pattern 1>.

## Indicators of Done (<Role Name>)

| Indicator | Target |
| --- | --- |
| <indicator> | <target> |

## Boundaries

### Do

- <in-scope action>.

### Do Not

- <out-of-scope action>.
```
