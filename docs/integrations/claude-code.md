# Linking Awesome-VibeCoder into Claude Code

> Goal: use any `sdlc-*` role agent as a Claude Code **subagent**, preload the matching `skills/sdlc-*/SKILL.md`, surface the repo's instructions via `CLAUDE.md`, run the SDLC pipeline against the `.sdlc/` shared state, and give the team MCP tools for the browser, GitHub, Playwright, etc.

This guide is self-contained and uses Claude Code's subagent + skills + `CLAUDE.md` + MCP features.

---

## What you are linking

| Asset | Repository path | Claude Code target |
| --- | --- | --- |
| Agents | `agents/*.agent.md` | `.claude/agents/<name>.md` (project) or `~/.claude/agents/<name>.md` (user) |
| Skills | `skills/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` (auto-discovered) or `skills:` frontmatter preload |
| Instructions | `instructions/*.instructions.md` | referenced from `CLAUDE.md` (Claude Code has no per-path instruction loader) |
| Workflows | `workflows/*.workflow.md` | used by the orchestrator subagent (`/agents` or `@agent-...`) |
| Shared state | `.sdlc/` (created at runtime) | read/written by every agent; nothing to wire |

> **Auto-generate the `.claude/agents/` files:** run [`scripts/agent-frontmatter-adapter.py`](../../scripts/agent-frontmatter-adapter.py) over each repo agent — it maps Copilot tool names to Claude's (`Read, Edit, Bash, Agent, …`), injects the matching `skills:` preload list, sets `permissionMode`, and optionally inlines the Playwright MCP server. See the [Cross-Host Compatibility guide](compatibility.md) for the full matrix and presets. The hand-written examples below are what the adapter produces.

---

## Prerequisites

- Claude Code installed and signed in (`claude --version`).
- This repository cloned at a stable path, e.g. `~/src/Awesome-VibeCoder`.
- A **target project** where the SDLC team will work.

Layout choice (this guide uses **reference**, copying nothing): keep Awesome-VibeCoder on disk; the target project's `.claude/` contains thin pointer files. For a committed setup you can instead copy the assets directly into the target project's `.claude/` and check them in — Claude Code treats both forms identically.

---

## Step 1 — Expose skills via the `.claude/skills/` loader

Claude Code recursively scans `.claude/skills/` and `~/.claude/skills/` for `**/SKILL.md` files. Two ways:

### Option A — symlink the whole skills tree (zero-copy)

```bash
cd <target-project>
mkdir -p .claude
ln -s ~/src/Awesome-VibeCoder/skills .claude/skills
```

After restart, all 47 skills (`sdlc-shared-memory`, `web-design-system`, `web-performance-budget`, …) are discoverable by the Skill tool.

### Option B — point skills at the repo with a preload list

Keep the repo on disk and preload per subagent via the `skills:` frontmatter field (see Step 2).

> Claude Code ignores a skill with no `description:` frontmatter. Every Awesome-VibeCoder skill already declares `name` + `description`, so they load as-is.

---

## Step 2 — Wire role agents as subagents

Subagent files live in `.claude/agents/<name>.md` (project scope — checked into the target repo) or `~/.claude/agents/<name>.md` (personal, all projects). Required frontmatter: `name`, `description`. Supported extras: `tools`, `disallowedTools`, `model`, `permissionMode`, `mcpServers`, `hooks`, `skills`, `memory`, `effort`, `isolation`, `color`, `initialPrompt`.

The repo's agent frontmatter uses Copilot-style tool names (`vscode, execute, read, agent, edit, search, web, browser, todo`). Claude Code's tool names are `Read, Write, Edit, Bash, Grep, Glob, WebFetch, WebSearch, Skill, Agent`. Map them.

Create one subagent per role under `.claude/agents/`. Example:

```markdown
---
name: sdlc-frontend-engineer
description: Senior frontend engineering — UI components, state, accessibility (WCAG 2.1 AA), Core Web Vitals, variant composition. Use proactively when implementing or reviewing frontend code.
model: sonnet
tools: Read, Edit, Write, Bash, Grep, Glob, WebFetch, WebSearch, Skill, Agent
skills:
  - sdlc-frontend-engineer
  - sdlc-shared-memory
  - web-accessibility-audit
  - web-performance-budget
permissionMode: acceptEdits
---

Read ~/src/Awesome-VibeCoder/agents/sdlc-frontend-engineer.agent.md and follow it exactly as your operating manual. The repo file overrides any contradiction in this default prompt.

Workflow summary (full rules live in the repo file):
1. On startup, load the .sdlc/ baseline (or scaffold it via sdlc-shared-memory).
2. Read .sdlc/contracts/api-contracts.md and .sdlc/systemPatterns.md.
3. Claim a frontend task from .sdlc/tasks/_index.md.
4. Implement UI in the real source tree (never in .sdlc/). Build + run tests; fix and re-run until green.
5. Write the command + result to .sdlc/progress.md and a one-line pointer to .sdlc/memory.md.
6. Hand off to QA Tester when ready.
```

### Required tool-name mapping

Apply this when translating each repo agent:

| Repo `tools` entry | Claude Code equivalent |
| --- | --- |
| `read`, `search` | `Read`, `Grep`, `Glob` |
| `edit` | `Edit` |
| `execute` (run commands) | `Bash` |
| `agent` (delegate) | `Agent` |
| `web`, `browser` | `WebFetch`, `WebSearch` (browser MCP server covers the rest — Step 5) |
| `vscode`, `todo`, `ms-python.*` | drop (no equivalent built-in) |

### Read-only research roles

Architect, UX/UI Designer, Responsible AI, Scrum Master and the Orchestrator's planning phases are read-only by intent. For those, use:

```yaml
tools: Read, Grep, Glob, WebFetch, Skill, Agent
permissionMode: plan
```

### Orchestrator subagent

```markdown
---
name: sdlc-orchestrator
description: Initialize the .sdlc/ workspace, decompose a project goal into tasks, dispatch SDLC role subagents in sequence or parallel, and gate phase advancement on real verification evidence in .sdlc/progress.md. Use proactively for multi-agent SDLC work.
model: sonnet
tools: Read, Grep, Glob, Edit, Write, Bash, Agent, Skill
permissionMode: default
skills:
  - sdlc-shared-memory
initialPrompt: Initialize the .sdlc/ workspace for this project if missing, then await a goal.
---

Read ~/src/Awesome-VibeCoder/agents/sdlc-orchestrator.agent.md and follow it. When the Agent tool is available, dispatch the next role subagent directly rather than only recommending it.
```

Save under `.claude/agents/sdlc-orchestrator.md`.

> Claude Code watches `.claude/agents/` and reloads within seconds — no restart needed when editing an existing agent file. Restart **once** after adding the first agent file to a brand-new `agents/` directory.

---

## Step 3 — Surface instructions via `CLAUDE.md`

Claude Code has **no per-path instruction loader** like Copilot. Instead it loads `CLAUDE.md` (and `.claude/CLAUDE.md` and ancestor `CLAUDE.md` files up the tree). Use one of these patterns.

### Pattern A — single index file

In the target project root, `CLAUDE.md`:

```markdown
# Project operating instructions

Always load ~/src/Awesome-VibeCoder/instructions/<file>.md when the work touches that domain:

| Domain | Instruction file (load on demand) |
| --- | --- |
| Next.js | ~/src/Awesome-VibeCoder/instructions/nextjs.instructions.md |
| React 19 | ~/src/Awesome-VibeCoder/agents/expert-react-frontend-engineer.agent.md |
| Tailwind v4 + Vite | ~/src/Awesome-VibeCoder/instructions/tailwind-v4-vite.instructions.md |
| Security / OWASP | ~/src/Awesome-VibeCoder/instructions/security-and-owasp.instructions.md |
| Accessibility | ~/src/Awesome-VibeCoder/instructions/a11y.instructions.md |
| Markdown / docs | ~/src/Awesome-VibeCoder/instructions/markdown-gfm.instructions.md |

When working on a file, fetch the matching instruction first (Read tool) and follow it.
```

### Pattern B — per-folder `CLAUDE.md` "child" instructions

Drop `CLAUDE.md` files into `apps/web/CLAUDE.md`, `apps/api/CLAUDE.md`, etc. Each points at the relevant instruction file from Awesome-VibeCoder. Claude Code walks up from the cwd and loads every ancestor `CLAUDE.md`, so per-area rules reach only the agents working in that area.

> Avoid pasting all 107 instruction files into `CLAUDE.md` — context budget. One `@`-reference per active domain is the right size.

---

## Step 4 — Link workflows

There are no "workflow" plugin files in Claude Code for arbitrary multi-step orchestration — but the orchestrator subagent can run the workflow blueprints directly:

```text
 @"sdlc-orchestrator (agent)" load ~/src/Awesome-VibeCoder/workflows/sdlc-sequential.workflow.md and execute it phase by phase against this project's .sdlc/.
```

Or, for the parallel workflow:

```text
@"sdlc-orchestrator (agent)" load ~/src/Awesome-VibeCoder/workflows/sdlc-parallel.workflow.md and run its phases with the dependency gates.
```

The orchestrator reads the workflow file, advances phases, and dispatches role subagents using the `Agent` tool.

---

## Step 5 — Configure MCP servers

Create `.mcp.json` at the target project root (Claude Code's MCP manifest). Supported types: `stdio`, `http`, `sse`, `ws`.

```json
{
  "mcpServers": {
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

Scope an MCP server to a single subagent by listing it in that subagent's `mcpServers:` frontmatter instead of the global `.mcp.json`. Inline servers connect when the subagent starts and disconnect when it finishes — useful for keeping browser-tool descriptions out of the main context.

Example for the frontend engineer:

```yaml
mcpServers:
  - playwright:
      type: stdio
      command: npx
      args: ["-y", "@playwright/mcp@latest"]
```

> Plugin subagents cannot declare `mcpServers`, `hooks`, or `permissionMode`. If you publish agents via a plugin, copy the file into `.claude/agents/` instead.

---

## Step 6 — Run a canonical SDLC session

From the target project root:

1. Launch Claude Code in the project: `claude`.
2. Scaffold the shared state:

   ```text
   @"sdlc-orchestrator (agent)" scaffold .sdlc/ and decompose the goal "<your goal>" into role-assigned tasks.
   ```

3. Verify: `ls .sdlc/` (expect `projectbrief.md`, `architecture.md`, `tasks/`, `decisions/`, `contracts/`, `handoffs/`).
4. Run the pipeline (one of):

   ```text
   @"sdlc-orchestrator (agent)" run the SDLC sequential workflow.
   ```

   or invoke roles directly:

   ```text
   @"sdlc-orchestrator (agent)" dispatch @sdlc-software-architect for TASK-001, then @sdlc-backend-engineer for TASK-002 after the architect's handoff.
   ```

5. The orchestrator advances a phase **only when `.sdlc/progress.md` cites a real command + result** for that phase. Open `progress.md` to verify — the same gate the repository's agents already enforce.

---

## Verification checklist

- [ ] `/agents` lists your role subagents (`sdlc-orchestrator`, `sdlc-frontend-engineer`, …).
- [ ] A `Skill` tool call can load `sdlc-shared-memory` without error.
- [ ] `CLAUDE.md` exists and references instruction files by absolute/relative path.
- [ ] Running `@agent-sdlc-orchestrator` creates a `.sdlc/` directory.
- [ ] `/mcp` shows your configured servers and their tools.
- [ ] `.sdlc/progress.md` accumulates real command+result lines after each role.

---

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| New agent not listed | `agents/` directory was empty at session start | restart Claude Code once |
| Subagent can't edit files | `permissionMode` left at default and project requires approval | switch to `acceptEdits` or approve when prompted |
| Skills not auto-loading | skill folder lacks `SKILL.md` or `description` | verify `skills/<name>/SKILL.md` and its frontmatter |
| MCP server not visible | wrong type/shape in `.mcp.json` | supported types: `stdio`, `http`, `sse`, `ws`; restart after editing |
| `Agent(restricted-type)` errors | target subagent not in allowed list | add `Agent(<name>)` to the parent agent's `tools` |

---

## See also

- [Awesome-VibeCoder root README](../../README.md)
- [SDLC system overview](../README.sdlc-system.md)
- Claude Code docs: <https://docs.claude.com/en/docs/claude-code/sub-agents> · <https://docs.claude.com/en/docs/claude-code/skills> · <https://docs.claude.com/en/docs/claude-code/mcp>