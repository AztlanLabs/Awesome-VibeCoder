# Linking Awesome-VibeCoder into opencode

> Goal: from inside an opencode session, be able to run any `sdlc-*` role agent, load the matching `skills/sdlc-*/SKILL.md`, apply the repo's framework instructions, and coordinate the SDLC pipeline against the `.sdlc/` shared state.

This guide is **self-contained**. opencode validates config strictly and refuses to start on a wrong field shape — when a field is in doubt, fetch the authoritative schema at <https://opencode.ai/config.json>.

---

## What you are linking

| Asset | Repository path | opencode target |
| --- | --- | --- |
| Agents | `agents/*.agent.md` | `.opencode/agent/<name>.md` |
| Skills | `skills/<name>/SKILL.md` | `skills.paths: ["skills"]` in `opencode.json` (no copy needed) |
| Instructions | `instructions/*.instructions.md` | `instructions: [...]` array in `opencode.json` (curated) |
| Workflows | `workflows/*.workflow.md` | referenced from `command:` slash-commands or the orchestrator agent |
| Shared state | `.sdlc/` (created at runtime) | read/written by every agent; nothing to wire |

> **Shortcut:** the repo ships a fully-populated, ready-to-paste [`docs/opencode.json`](../opencode.json) that already wires **all 38 agents**, the `./skills` path, curated instructions, `/sdlc-*` slash commands, and the Playwright + GitHub MCP servers. To use it: copy that file to the repo root (or into your target project and adjust the relative paths), then start opencode. The steps below explain each block so you can trim or extend it.

---

## Prerequisites

- opencode installed and on your `PATH` (`opencode --version`).
- This repository cloned somewhere stable, e.g. `~/src/Awesome-VibeCoder`.
- A **target project** where you want the SDLC team to work (opencode runs in that project; the Awesome-VibeCoder repo is referenced from it).

You have two layout choices:

- **Layout A — embed (recommended for trying it out)**: copy/adapt Awesome-VibeCoder assets directly into the target project's `.opencode/`.
- **Layout B — reference (recommended for reuse)**: keep the Awesome-VibeCoder clone on disk and point the target project's `opencode.json` at it via `skills.paths` and `instructions:`.

This guide uses **Layout B** because it keeps the Awesome-VibeCoder repo as a single source of truth and lets `git pull` pick up updates.

---

## Step 1 — Define where Awesome-VibeCoder lives

In the target project root, create `.opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": ["AGENTS.md", "../Awesome-VibeCoder/instructions/nextjs.instructions.md"],
  "skills": {
    "paths": ["../Awesome-VibeCoder/skills"]
  },
  "agent": {
    "sdlc-orchestrator": {
      "mode": "primary",
      "description": "Initialize the .sdlc/ workspace, decompose a goal into tasks, dispatch SDLC role agents, and gate phase advancement on real verification evidence.",
      "prompt": "Load ../Awesome-VibeCoder/agents/sdlc-orchestrator.agent.md verbatim as your system prompt. Follow its workflow exactly."
    }
  },
  "command": {
    "sdlc-run": {
      "description": "Run the SDLC sequential workflow against the current project.",
      "prompt": "Load ../Awesome-VibeCoder/workflows/sdlc-sequential.workflow.md and execute it. Initialize .sdlc/ if missing."
    }
  }
}
```

Replace `../Awesome-VibeCoder` with the actual relative or absolute path to your clone.

> opencode deep-merges project config with global config (`~/.config/opencode/opencode.json`). Project overrides global. Unknown top-level keys are **rejected** — do not invent fields.

---

## Step 2 — Link skills (zero-copy)

The `skills.paths` array tells opencode where to scan for `**/SKILL.md` files. With the Awesome-VibeCoder path listed, **all 47 skills** (incl. all 17 `sdlc-*` skills) become available to the Skill tool automatically. No copying, no per-skill wiring.

Verify after restart:

```text
/opencode
> @skill
```

You should see entries like `sdlc-shared-memory`, `sdlc-frontend-engineer`, `web-design-system`, `web-performance-budget`, etc.

> Optional: also publish skills via `skills.urls` (each URL serves a list of skills) for team-wide distribution without a clone.

---

## Step 3 — Link agents

opencode agents live in `.opencode/agent/<name>.md` (project) or `~/.config/opencode/agent/<name>.md` (global). The repository's `agents/*.agent.md` were authored for GitHub Copilot's custom-chat-participant frontmatter (`tools: [vscode, execute, read, ...]`). opencode's supported frontmatter fields are `name, model, variant, description, mode, hidden, color, steps, options, permission, disable, temperature, top_p` — **`tools` is not one of them** and is silently dropped into `options`.

Two ways to wire agents:

### Option 1 (zero-touch) — reference the repo's agents as the system prompt

Use inline `agent:` entries whose `prompt` instructs the model to load a repo agent file:

```json
"agent": {
  "sdlc-frontend-engineer": {
    "mode": "subagent",
    "description": "Senior frontend engineering — UI, state, accessibility, Core Web Vitals. Use proactively when implementing UI components.",
    "prompt": "Read ../Awesome-VibeCoder/agents/sdlc-frontend-engineer.agent.md and follow it exactly as your operating manual. Always load skills/sdlc-shared-memory and skills/sdlc-frontend-engineer. Write code to the real source tree (not .sdlc/)."
  }
}
```

### Option 2 (native) — adapt each agent into a `.opencode/agent/<name>.md` file

For each role you want first-class, create a file under `.opencode/agent/` that strips the Copilot-style `tools:` field, maps it onto `permission:`, and keeps the markdown body:

```markdown
---
mode: subagent
description: Senior frontend engineering — UI, state, accessibility, Core Web Vitals.
permission:
  edit: allow
  bash: ask
---

(paste the body of agents/sdlc-frontend-engineer.agent.md here)
```

A mechanical translation table (for a one-time conversion script):

| Repo frontmatter | opencode equivalent |
| --- | --- |
| `name: 'SDLC: Frontend Engineer'` | folder name `<slug>.md` (e.g. `sdlc-frontend-engineer.md`) |
| `description: '...'` | `description: '...'` |
| `tools: [vscode, execute, read, agent, edit, search, web, browser]` | drop; set `permission: { edit: allow, bash: ask }` |
| `tools` containing only read/search | `permission: { edit: deny, bash: deny }` + `mode: subagent` |
| `todo`/`ms-python.*` | drop (opencode has no Python-extension tools) |
| body | becomes the agent `prompt` as-is |

Because Option 1 requires no per-agent conversion, prefer it unless you want the agent to appear in the TUI's agent picker with its own colour/model.

---

## Step 4 — Link instructions

opencode loads the strings in `instructions:` as additional context. Listing **all 107 instruction files** bloats context — pick the ones the current project uses:

```json
"instructions": [
  "AGENTS.md",
  "../Awesome-VibeCoder/instructions/nextjs.instructions.md",
  "../Awesome-VibeCoder/instructions/security-and-owasp.instructions.md",
  "../Awesome-VibeCoder/instructions/a11y.instructions.md"
]
```

A pragmatic pattern is to write a target-project `AGENTS.md` that names the relevant Awesome-VibeCoder instruction files by topic and tells the model to load them on demand, then list only `AGENTS.md` in `opencode.json`. That keeps the always-on context small while keeping instructions one `@file` away.

---

## Step 5 — Link workflows as slash commands

The repository ships workflow blueprints and a set of role-targeted slash commands. Map them to opencode slash commands:

### Workflow commands

```json
"command": {
  "sdlc-sequential": {
    "description": "Run the SDLC sequential workflow.",
    "prompt": "Load ../Awesome-VibeCoder/workflows/sdlc-sequential.workflow.md and execute it phase by phase against .sdlc/."
  },
  "sdlc-parallel": {
    "description": "Run the SDLC parallel workflow.",
    "prompt": "Load ../Awesome-VibeCoder/workflows/sdlc-parallel.workflow.md and execute its phases with dependency gates against .sdlc/."
  },
  "sdlc-bug-triage": {
    "description": "Run the bug-triage workflow on a reported bug.",
    "prompt": "Load ../Awesome-VibeCoder/workflows/bug-triage.workflow.md and execute it. Confirm the bug task in .sdlc/tasks/ has a Root Cause section, run the failing → passing test transition, and ship via the DevOps Engineer step."
  },
  "sdlc-docs-regen": {
    "description": "Regenerate the project's user-facing docs from the API contract with a path audit and Responsible AI review.",
    "prompt": "Load ../Awesome-VibeCoder/workflows/docs-regen.workflow.md and execute it: Technical Writer regenerates the affected docs; RepositoryPathAuditor audits paths; Responsible AI signs off on bias / privacy / accessibility."
  }
}
```

Invoke with `/sdlc-sequential`, `/sdlc-parallel`, `/sdlc-bug-triage`, or `/sdlc-docs-regen` from the opencode prompt.

### Role-targeted commands

The repo also ships seven role-targeted slash commands that map directly to a single agent. They are wired in `docs/opencode.json` under `command:` and are listed here for discoverability:

| Slash command | Loads | Purpose |
| --- | --- | --- |
| `/review` | `sdlc-code-reviewer` | Review a diff, PR, or staged change for code quality, SOLID, and security |
| `/a11y` | `sdlc-accessibility-specialist` | Audit the current page or component for WCAG 2.1 AA and produce a remediation report |
| `/explain` | `context-researcher` | Explain a code section in plain language with file:line evidence |
| `/implement` | `sdlc-orchestrator` + relevant specialist | Implement a feature end-to-end against the API contract, with tests |
| `/test` | `sdlc-qa-tester` | Write or extend the test suite, enforce quality gates, report coverage |
| `/rfc` | `sdlc-software-architect` | Draft an ADR / RFC with context, options, trade-offs, and a decision |
| `/pr` | `sdlc-devops-engineer` | Open a pull request with a structured title, description, and Definition-of-Done checklist |

Invoke any of these directly from the opencode prompt; the agent is dispatched with the relevant context.

---

## Step 6 — Configure MCP servers

opencode's `mcp:` block is an object keyed by server name. `command` is an **array of strings**, `type` is required. Add the servers your SDLC team needs (browser automation for the frontend engineer, GitHub for the orchestrator, Playwright for QA, etc.):

```json
"mcp": {
  "playwright": {
    "type": "local",
    "command": ["npx", "-y", "@playwright/mcp@latest", "--caps=vision"],
    "enabled": true,
    "env": {}
  },
  "github": {
    "type": "local",
    "command": ["npx", "-y", "@modelcontextprotocol/server-github"],
    "enabled": true,
    "env": { "GITHUB_TOKEN": "{env:GITHUB_TOKEN}" }
  }
}
```

Notes:
- `{env:VAR}` and `{file:path}` interpolation is supported for string values; `${VAR}` is **not** substituted.
- Use `"enabled": false` to disable a server inherited from parent config.
- Scope an MCP server to a single agent by adding it inside that agent's `options`/frontmatter rather than globally.

---

## Step 7 — Run a canonical SDLC session

From the target project root:

1. Start opencode: `opencode`.
2. Initialize the shared workspace:

   ```text
   Use @agent-sdlc-orchestrator to scaffold .sdlc/ for this project and decompose the goal "<your goal>" into tasks.
   ```

3. Confirm `.sdlc/` exists (`ls .sdlc/` should show `projectbrief.md`, `architecture.md`, `tasks/`, etc.).
4. Drive the pipeline:

   ```text
   /sdlc-sequential
   ```

   Or invoke individual roles: `@agent-sdlc-software-architect`, `@agent-sdlc-backend-engineer`, `@agent-sdlc-frontend-engineer`, `@agent-sdlc-qa-tester`, …

5. The orchestrator gates each phase on **evidence** in `.sdlc/progress.md` (real command + result), not on `COMPLETED` status alone. Open `.sdlc/progress.md` to verify.

---

## Verification checklist

- [ ] `opencode.json` parses (opencode starts without `ConfigInvalidError`).
- [ ] `@skill` lists the Awesome-VibeCoder skills (esp. `sdlc-shared-memory`).
- [ ] The role agents you wired appear in the agent picker.
- [ ] `/sdlc-sequential` (or `/sdlc-parallel`) is offered as a command.
- [ ] `.sdlc/` is created by the first agent you run.
- [ ] `.sdlc/progress.md` accumulates real command + result lines after each role.

---

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `ConfigInvalidError` on startup | unknown top-level key or wrong shape | cross-check field against <https://opencode.ai/config.json>; remove or fix the field |
| Skills not surfaced | skill folder lacks `SKILL.md`, or no `description:` frontmatter | confirm `skills/<name>/SKILL.md` exists and has `name` + `description` |
| Agent's `tools` ignored | opencode has no `tools` frontmatter field | use `permission:` instead; or use Option 1 (reference the repo agent by path) |
| MCP server not connecting | `command` is a string, not an array | make it `["npx", "-y", "..."]`; ensure `type` is set |
| Changes don't take effect | opencode loads config once at startup | quit and restart opencode after saving config |

---

## See also

- [Awesome-VibeCoder root README](../../README.md)
- [SDLC system overview](../README.sdlc-system.md)
- [Skills catalog](../README.skills.md) · [Agents catalog](../README.agents.md) · [Workflows](../README.workflows.md)
- opencode config schema: <https://opencode.ai/config.json>