# Linking Awesome-VibeCoder into Cursor

> Goal: surface this repo's agents, skills, instructions, workflows, and MCP servers in Cursor, and run the SDLC pipeline against the `.sdlc/` shared state.

Cursor has no first-class "agent" or "skill" plugin format. It exposes **project rules** (`.cursor/rules/*.mdc`) and **MCP servers** (`.cursor/mcp.json`). This guide maps each Awesome-VibeCoder asset onto those mechanisms and shows how to drive the SDLC team by referencing the orchestrator agent.

> Cursor also reads a root `AGENTS.md` (the cross-tool convention) so its built-in composer gains the same context.

---

## What you are linking

| Asset | Repository path | Cursor target |
| --- | --- | --- |
| Rules index | new root `AGENTS.md` | Cursor agent reads it |
| Path-specific rules | `instructions/*.instructions.md` (have `applyTo`) | `.cursor/rules/<name>.mdc` (globs map to `globs:`) |
| Role agents | `agents/sdlc-*.agent.md` | `.cursor/rules/<role>.mdc` (auto-injected on demand) |
| Skills | `skills/<name>/SKILL.md` | each skill becomes a `.mdc` rule with `alwaysApply: false` |
| Workflows | `workflows/*.workflow.md` | referenced from the orchestrator rule |
| Shared state | `.sdlc/` (created at runtime) | nothing to wire |
| MCP | `.cursor/mcp.json` | tool surface |

---

## Prerequisites

- Cursor installed; signed in.
- This repository cloned, e.g. `~/src/Awesome-VibeCoder`.
- A **target project** opened in Cursor.

---

## Step 1 — Root `AGENTS.md`

Create a root `AGENTS.md` in the target project:

```markdown
# Agents guide

Awesome-VibeCoder agent personas live in `~/src/Awesome-VibeCoder/agents/`. Each file is a complete role operating manual. When asked to act as an SDLC role, load the matching agent file (`agents/<role>.agent.md`) and follow it.

Coding/style/instructions live in `~/src/Awesome-VibeCoder/instructions/`; workflows in `~/src/Awesome-VibeCoder/workflows/`. Coordinate via the `.sdlc/` shared state at the project root. Write source code to the project's real source tree; record build/test command + result in `.sdlc/progress.md`.
```

Cursor's composer reads `AGENTS.md` from the workspace root for context.

---

## Step 2 — `.cursor/rules/` for path-specific instructions

Cursor rule files use frontmatter `description`, `globs`, `alwaysApply`. The repo's instruction files already declare an `applyTo` glob; copy them and convert:

```bash
mkdir -p .cursor/rules
for f in ~/src/Awesome-VibeCoder/instructions/nextjs.instructions.md \
         ~/src/Awesome-VibeCoder/instructions/tailwind-v4-vite.instructions.md \
         ~/src/Awesome-VibeCoder/instructions/security-and-owasp.instructions.md; do
  base=$(basename "$f" .instructions.md)
  cp "$f" ".cursor/rules/${base}.mdc"
done
```

Then edit each `.mdc` so the frontmatter uses Cursor's fields:

```markdown
---
description: Next.js App Router conventions and best practices
globs: ["**/*.tsx", "**/*.ts", "app/**/*.tsx", "next.config.*"]
alwaysApply: false
---
```

> `applyTo` accepts comma-separated globs; `globs:` is a YAML list. If a repo file has `applyTo: "**/*.tsx, **/*.ts"`, split into two entries.

`alwaysApply: false` means the rule is **injected on demand** when the editor file matches `globs` (recommended to keep context lean).

---

## Step 3 — Role agents as `.mdc` rules

For each role you want first-class, create `.cursor/rules/<role>.mdc` whose body pastes the repo agent's body. Example:

```markdown
---
description: SDLC Backend Engineer — APIs, service layers, data access, idempotency, observability. Trigger when implementing or reviewing backend code.
globs: ["src/api/**", "src/services/**", "src/server/**"]
alwaysApply: false
---

<paste the body of ~/src/Awesome-VibeCoder/agents/sdlc-backend-engineer.agent.md here>
```

Because the repo agent bodies are long, the cleaner alternative is to **reference** the file rather than paste:

```markdown
---
description: SDLC Backend Engineer — APIs, service layers, idempotency, observability.
globs: ["src/api/**", "src/services/**", "src/server/**"]
alwaysApply: false
---

Read ~/src/Awesome-VibeCoder/agents/sdlc-backend-engineer.agent.md and follow it as your operating manual. Always load skills/sdlc-shared-memory and skills/sdlc-backend-engineer. Write code to the real source tree; record build/test command + result in .sdlc/progress.md.
```

Pick the paste form only if you want the rule to work offline / in agent mode without file reads.

---

## Step 4 — Skills as `.mdc` rules

Each `skills/<name>/SKILL.md` becomes a rule with `alwaysApply: false`:

```markdown
---
description: web-performance-budget — define and enforce Core Web Vitals and asset budgets. Trigger when working on performance or build config.
globs: ["**/perf-budgets*", "**/lighthouserc*", "**/vite.config.*", "**/webpack.config.*"]
alwaysApply: false
---

Read ~/src/Awesome-VibeCoder/skills/web-performance-budget/SKILL.md and apply its patterns, rules, and indicators of done.
```

Reuse the skill's frontmatter `description` verbatim where the repo already states triggers ("Use when…").

---

## Step 5 — Workflows via reference rule

Create `.cursor/rules/sdlc-workflow.mdc`:

```markdown
---
description: SDLC multi-agent pipeline using .sdlc/ shared state
alwaysApply: false
---

When asked to "run the SDLC pipeline":
1. Read ~/src/Awesome-VibeCoder/agents/sdlc-orchestrator.agent.md and follow it.
2. For phase order, load ~/src/Awesome-VibeCoder/workflows/sdlc-sequential.workflow.md.
3. Gate each phase on a real command + result cited in .sdlc/progress.md (build/test/lint/tf validate).
```

---

## Step 6 — MCP servers

Cursor supports MCP at `.cursor/mcp.json` (project) and `~/.cursor/mcp.json` (user). Example:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest", "--caps=vision"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    }
  }
}
```

After editing, reload the Cursor window (`Cmd/Ctrl+Shift+P` → "Reload Window"). Verify MCP servers in Cursor Settings → MCP.

---

## Step 7 — Run a canonical SDLC session

1. Open the target project in Cursor.
2. In the composer / chat, type:

   ```text
   Act as the SDLC Orchestrator: scaffold .sdlc/ for this project (read ~/src/Awesome-VibeCoder/agents/sdlc-orchestrator.agent.md), then decompose the goal "<your goal>" into role-assigned tasks in .sdlc/tasks/.
   ```

3. Verify `.sdlc/` scaffolding exists.
4. Drive the pipeline:

   ```text
   Run the SDLC sequential workflow against this project. For each phase, act as the matching role (load agents/<role>.agent.md), implement to the real source tree, and record the build/test command + result in .sdlc/progress.md before advancing.
   ```

5. The orchestrator's gate logic applies: no phase advances without a real command+result in `progress.md`.

---

## Verification checklist

- [ ] `AGENTS.md` exists at the project root.
- [ ] `.cursor/rules/*.mdc` exist for the roles and languages this project uses.
- [ ] Each `.mdc` has valid frontmatter (`description`, `globs`/`alwaysApply`).
- [ ] `.cursor/mcp.json` parses; MCP servers connect (Settings → MCP).
- [ ] A "scaffold .sdlc/" prompt creates `.sdlc/` files.
- [ ] `.sdlc/progress.md` accumulates real command+result lines.

---

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| Rule never injects | `globs` mismatch or `alwaysApply: false` and no matching file open | open a matching file, or set `alwaysApply: true` for a small root rule |
| `AGENTS.md` ignored | Cursor version predates AGENTS support | upgrade Cursor or rely on `.cursor/rules/readme.mdc` with `alwaysApply: true` |
| MCP server not connecting | wrong `command`/`args` shape | `command` is a string, `args` is a string array; reload the window |
| Composer pastes full agent body into context | reference rule loaded `@file` inline | use the reference form (no paste) and rely on on-demand reads |

---

## See also

- [Awesome-VibeCoder root README](../../README.md)
- [SDLC system overview](../README.sdlc-system.md)
- Cursor docs: <https://docs.cursor.com> (Rules, MCP)