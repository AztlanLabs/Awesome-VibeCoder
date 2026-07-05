# Linking Awesome-VibeCoder into Antigravity

> Goal: surface this repo's agents, skills, instructions, workflows, and MCP servers in **Google Antigravity**, and run the SDLC pipeline against the `.sdlc/` shared state.

Antigravity is Google's agentic coding environment. It reads a root **`AGENTS.md`** as the project's agent manual (the cross-tool convention), supports **MCP servers** configured via a project `mcp.json` (VS Code-style), and exposes project-specific rules/instructions in its settings panel. Antigravity's UI evolves quickly — where a step depends on a menu name, the file-based equivalents below keep working across updates.

---

## What you are linking

| Asset | Repository path | Antigravity target |
| --- | --- | --- |
| Project manual | new root `AGENTS.md` | loaded by the Antigravity agent |
| Path-specific instructions | `instructions/*.instructions.md` (have `applyTo`) | referenced from `AGENTS.md` and (where supported) the Rules/Custom Instructions panel |
| Role agents | `agents/sdlc-*.agent.md` | referenced from `AGENTS.md`; bodies loaded on demand |
| Skills | `skills/<name>/SKILL.md` | referenced from `AGENTS.md`; bodies loaded on demand |
| Workflows | `workflows/*.workflow.md` | referenced from `AGENTS.md` and the orchestrator |
| Shared state | `.sdlc/` (created at runtime) | nothing to wire |
| MCP | `.vscode/mcp.json` or project `mcp.json` | tool surface |

---

## Prerequisites

- Antigravity installed and open in your target project.
- This repository cloned, e.g. `~/src/Awesome-VibeCoder`.
- A **target project** where the SDLC team will work.

---

## Step 1 — Root `AGENTS.md`

In the target project root, create:

```markdown
# Agents guide

This project uses the Awesome-VibeCoder SDLC multi-agent system. The agents, skills, instructions, and workflows live at `~/src/Awesome-VibeCoder/`.

## Acting as a role
When asked to perform an SDLC role, read `~/src/Awesome-VibeCoder/agents/<role>.agent.md` and follow its workflow, patterns, indicators of done, and boundaries verbatim. Shared state lives in `.sdlc/` at the project root; read `.sdlc/activeContext.md`, `.sdlc/progress.md`, and the relevant `.sdlc/contracts/*.md` before acting. Write source code to the project's real source tree — never into `.sdlc/`.

## Instructions (load on demand)
| Domain | File |
| --- | --- |
| Frontend / Next.js | ~/src/Awesome-VibeCoder/instructions/nextjs.instructions.md |
| Tailwind v4 + Vite | ~/src/Awesome-VibeCoder/instructions/tailwind-v4-vite.instructions.md |
| React (modern) | ~/src/Awesome-VibeCoder/instructions/… (see expert-react-frontend-engineer.agent.md) |
| Security / OWASP | ~/src/Awesome-VibeCoder/instructions/security-and-owasp.instructions.md |
| Accessibility | ~/src/Awesome-VibeCoder/instructions/a11y.instructions.md |
| Markdown / docs | ~/src/Awesome-VibeCoder/instructions/markdown-gfm.instructions.md |

When working in a file, read the matching instruction first and follow it.

## Workflows
- Sequential: ~/src/Awesome-VibeCoder/workflows/sdlc-sequential.workflow.md
- Parallel: ~/src/Awesome-VibeCoder/workflows/sdlc-parallel.workflow.md

## Build & validate
- npm install
- npm run build
- npm test
- npm run lint

Treat each agent file's "Definition of Done" as a hard gate: only mark a task complete after a real build + test run with command + result cited in `.sdlc/progress.md`.
```

Antigravity's agent reads `AGENTS.md` from the workspace root, so this single file is the backbone of the integration.

---

## Step 2 — Project rules / custom instructions (UI)

Antigravity exposes project rules in its settings panel (the exact label varies by version — look for a "Rules", "Custom instructions", or "Memory" section). Add a one-line pointer to your `AGENTS.md` plus a short list of instruction files you want always-on. Recommended: keep always-on rules small and load the rest on demand.

If Antigravity's rules editor supports file globs (like Cursor's `.mdc`), add the repo's instruction files with their `applyTo` value as the glob. The repo's `instructions/*.instructions.md` already declare `applyTo`, so use them as-is:

- `nextjs.instructions.md` → `applyTo: "**/*.tsx, **/*.ts, **/*.jsx, **/*.js, **/*.css"`
- `tailwind-v4-vite.instructions.md` → adapt `applyTo` to your project's CSS / config paths
- `security-and-owasp.instructions.md` → broad globs or always-on for security-sensitive repos

> Antigravity's product UI changes; if a given glob/scoping feature is missing, fall back to "always-on" rules in the panel that simply reference the instruction file by path. The file-based `AGENTS.md` keeps working across updates.

---

## Step 3 — Role agents

Antigravity doesn't expose a per-agent file format like opencode/Claude Code, so role agents are reached through `AGENTS.md` references and prompts that name the role:

```text
Act as the SDLC Backend Engineer: read ~/src/Awesome-VibeCoder/agents/sdlc-backend-engineer.agent.md, then implement <task>. Consume .sdlc/contracts/api-contracts.md unchanged. Write to src/api/. Record build/test command + result in .sdlc/progress.md.
```

For roles you use frequently, add a short rule entry in the settings panel that names the role and its trigger:

```text
Role: SDLC Frontend Engineer — trigger when implementing or reviewing UI. Always load
~/src/Awesome-VibeCoder/agents/sdlc-frontend-engineer.agent.md and skills/sdlc-frontend-engineer/SKILL.md.
```

---

## Step 4 — Skills

Skills are referenced on demand from `AGENTS.md`. To make a skill auto-surface in a domain, add a small "skills available" table to `AGENTS.md`:

```markdown
## Skills (load when the trigger condition matches)
| Skill | Trigger |
| --- | --- |
| sdlc-shared-memory | any SDLC role — read on startup |
| sdlc-frontend-engineer | UI implementation, accessibility, Core Web Vitals |
| web-accessibility-audit | running WCAG 2.2 AA/AAA audits |
| web-performance-budget | defining/enforcing Core Web Vitals and asset budgets |
| web-design-system | design tokens, theming, primitive APIs |
```

Antigravity's agent loads the matching `skills/<name>/SKILL.md` when the user's request matches the trigger — no proprietary packaging required.

---

## Step 5 — MCP servers

Antigravity supports standard MCP servers via a project `mcp.json` at the workspace root **or** `.vscode/mcp.json` (VS Code-style). Use whichever your Antigravity version expects (try `.vscode/mcp.json` first; if a "MCP servers" panel rejects it, move it to root `mcp.json`).

`.vscode/mcp.json`:

```json
{
  "servers": {
    "playwright": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest", "--caps=vision"]
    },
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    }
  }
}
```

> Some Antigravity builds use the key `"mcpServers"` instead of `"servers"`; check the in-product schema preview in the MCP panel. After editing, reload the workspace.

Antigravity namespaces MCP tools by server name (e.g. `playwright/browser_navigate`).

---

## Step 6 — Run a canonical SDLC session

1. Confirm `AGENTS.md` exists at the project root, and `.vscode/mcp.json` (or root `mcp.json`) is configured.
2. In the Antigravity agent prompt:

   ```text
   Act as the SDLC Orchestrator (read ~/src/Awesome-VibeCoder/agents/sdlc-orchestrator.agent.md). Scaffold .sdlc/ for this project if missing, then decompose the goal "<your goal>" into role-assigned tasks in .sdlc/tasks/.
   ```

3. Verify `.sdlc/` scaffolding exists.
4. Drive the pipeline:

   ```text
   Run the SDLC sequential workflow: ~/src/Awesome-VibeCoder/workflows/sdlc-sequential.workflow.md. For each phase, act as the matching role, implement to the real source tree, and cite the build/test command + result in .sdlc/progress.md before advancing.
   ```

5. The orchestrator's gates apply unchanged: no phase advances without a real command+result cited in `progress.md`.

---

## Verification checklist

- [ ] `AGENTS.md` exists at the project root and references the Awesome-VibeCoder paths.
- [ ] Antigravity's Rules/Custom Instructions panel shows your always-on rules (or `AGENTS.md` alone, which is enough).
- [ ] `.vscode/mcp.json` (or root `mcp.json`) parses and servers list their tools in the MCP panel.
- [ ] A "scaffold .sdlc/" prompt creates `.sdlc/` files.
- [ ] `.sdlc/progress.md` accumulates real command+result lines after each role.
- [ ] Each role's "Definition of Done" / "Indicators of Done" is satisfied before handoff.

---

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| MCP server not listed | wrong file location or wrong key (`servers` vs `mcpServers`) | try `.vscode/mcp.json` then root `mcp.json`; match the in-product schema preview |
| `AGENTS.md` ignored | Antigravity version predates AGENTS support | upgrade, or replicate the same content into the Rules/Custom Instructions panel |
| Tool calls fail permission | Antigravity permission prompt dismissed | re-approve in the panel or workspace settings |
| Too much context | every instruction + skill loaded always-on | keep only `AGENTS.md` always-on; let the rest load on demand from `AGENTS.md` references |

---

## Notes on Antigravity evolution

Antigravity's UI labels and config keys evolve; this guide deliberately leans on **file-based standards** (`AGENTS.md` and `mcp.json`) which Antigravity honors across releases. When an in-product feature (e.g. a Rules/Globs editor) is available in your version, use it to scope the repo's `applyTo` instruction files per path — it is equivalent to `.cursor/rules/*.mdc` or Copilot's `.github/instructions/`. Verify exact panel names and the MCP config key against the in-product schema preview.

---

## See also

- [Awesome-VibeCoder root README](../../README.md)
- [SDLC system overview](../README.sdlc-system.md)
- Universal cross-host notes: [opencode integration guide](opencode.md#step-7-mcp-servers)