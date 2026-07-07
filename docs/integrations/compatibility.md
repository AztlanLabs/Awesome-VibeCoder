# Cross-Host Compatibility & Claude Readiness

> Are the repo's agents and skills ready for Claude Code? And how do we make the **same `.agent.md`/`SKILL.md` files work in opencode, Claude Code, GitHub Copilot, and Cursor without per-host rewrites?

This is the analysis + the protocol. For installation steps per host, see the [host guides](README.md). For the ready-to-paste opencode config, see [`docs/opencode.json`](../opencode.json).

---

## TL;DR verdict

| Asset class | Claude Code ready? | opencode ready? | Copilot ready? | Cursor ready? |
| --- | --- | --- | --- | --- |
| **`SKILL.md` skills** (47) | ✅ as-is (Claude scans `**/SKILL.md`, requires `name`+`description` — repo has both) | ✅ as-is (opencode scans `**/SKILL.md`, same frontmatter) | ✅ as-is (referenced from `AGENTS.md`/`copilot-instructions.md`) | ✅ via `.mdc` wrapper that points at the skill |
| **`.agent.md` agents** (38) | ⚠️ mostly (frontmatter `name`+`description` load; Claude's `tools`/`permissionMode`/`skills`/`mcpServers` are *not* set) | ⚠️ via config translation (opencode uses filename identity + `permission`, not `tools`) | ✅ as-is (Copilot-style frontmatter was the authoring target) | ⚠️ via `.mdc` wrapper (`description`+`globs`) |

**One sentence:** the skills are already cross-host portable; the agents are portable in *their system prompt* but need per-host frontmatter translation — that translation is mechanical and fully automated by [`scripts/agent-frontmatter-adapter.py`](../../scripts/agent-frontmatter-adapter.py).

---

## 1. Frontmatter field compatibility matrix

| Frontmatter field | opencode (`opencode.json` agent) | Claude Code (`.claude/agents/*.md`) | GitHub Copilot (chat mode/participant) | Cursor (`.cursor/rules/*.mdc`) |
| --- | --- | --- | --- | --- |
| `name` | derived from **filename** (`.opencode/agent/<name>.md`) | ✅ required | ✅ required | ignored (derived from filename) |
| `description` | ✅ | ✅ required | ✅ required | ✅ required (used for on-demand injection) |
| `tools` | ❌ silently dropped into `options`; use `permission:` | ✅ allowed list (Claude tool names); inherits all if omitted | ✅ allowed list (Copilot tool names) | ignored |
| `model` | ✅ (`provider/model-id`) or omit to inherit | ✅ `sonnet`/`opus`/`haiku`/`inherit` or omit | sometimes (chat-mode) | ignored |
| `mode` | ✅ `primary`/`subagent`/`all` | n/a (Claude auto-decides) | n/a | n/a |
| `permission` (opencode object) | ✅ | use `permissionMode:` instead | n/a | n/a |
| `permissionMode` (Claude) | n/a | ✅ `default`/`acceptEdits`/`plan`/… | n/a | n/a |
| `skills` (preload list) | n/a (skills auto-load via `skills.paths`) | ✅ explicit list, content injected at startup | via `AGENTS.md` reference | via `.mdc` body reference |
| `mcpServers` | n/a (global `mcp:` in config) | ✅ inline per-subagent | `.github/mcp.json` (global) | ignored |
| `hooks` | n/a (top-level config) | ✅ per-subagent lifecycle | n/a | n/a |
| `memory` | n/a | ✅ `user`/`project`/`local` | n/a | n/a |
| `globs` | n/a | n/a | use `applyTo` (instructions only) | ✅ (path targeting) |
| `alwaysApply` | n/a | n/a | n/a | ✅ `true`/`false` |
| `applyTo` (instructions) | n/a | n/a | ✅ on `.instructions.md` | n/a (map to `globs:`) |
| `temperature` / `top_p` | ✅ | n/a | n/a | n/a |

Legend: ✅ = read and obeyed; ❌ = rejected/silently dropped; n/a = not a concept in that host.

**Key inference:** no single frontmatter satisfies all four. `name`+`description` is the universal common denominator; everything else is host-specific.

---

## 2. Tool-name aliasing

Repo agents declare Copilot tool names. Claude Code and opencode use different names. The mapping used by the adapter:

| Repo/frontmatter `tools:` entry | Claude Code name | opencode equivalent | Cursor |
| --- | --- | --- | --- |
| `read` | `Read` | `read` (permission) | inherits |
| `edit` | `Edit` | `edit` (permission) | inherits |
| (write new files) | `Write` | `edit` (permission) | inherits |
| `execute` (run commands) | `Bash` | `bash` (permission) | inherits |
| `search` | `Grep`, `Glob` | `grep`, `glob` (permission) | inherits |
| (file discovery) | `Glob` | `glob`, `list` (permission) | inherits |
| `agent` (delegate to subagent) | `Agent` | `task` (permission) | inherits |
| `web` | `WebFetch` | `webfetch` (permission) | inherits |
| `browser` | MCP browser server | MCP browser server | MCP browser server |
| `search` (web) | `WebSearch` | `websearch` (permission) | inherits |
| (skill loading — not in tools) | `Skill` | `skill` (permission) / auto via `skills.paths` | via `.mdc` body |
| `vscode` | provider-specific / drop | drop | inherits |
| `todo` | drop (no built-in) / use `Task` | `todowrite` (permission) | inherits |
| `ms-python.python/*` | drop (no Python extension) | drop | drop |

> Claude Code **does not** have a `TodoWrite`/`task` overlap — `Task` was renamed to `Agent` in v2.1.63; `todo` in repo frontmatter has no Claude equivalent and should be dropped.

---

## 3. What's missing for full Claude Code readiness

Per agent, to be first-class in Claude Code the file needs (in addition to `name`+`description` which already exist):

1. **`tools:`** with Claude tool names — else the subagent inherits **all** tools (no scoping). Read-only artifacts (architect, governance reviewer) currently can't lock down to `Read, Grep, Glob, WebFetch`.
2. **`skills:`** preload list — the agent bodies say "Always load skills/sdlc-shared-memory"; in Claude Code this can be enforced via `skills:` frontmatter instead of relying on the body instruction.
3. **`permissionMode:`** — implementation roles want `acceptEdits` (run builds/tests without prompting on each edit); research roles want `plan` (read-only).
4. **`mcpServers:`** for browser-dependent roles (frontend engineer, web-design-reviewer, QA) — inline the Playwright MCP server name.

The repo's agent **bodies** (system prompts) are already host-neutral — they reference `.sdlc/`, skills, and skills by relative path, which Claude Code honors via Read/Skill tools. So no body rewrite is needed; only the frontmatter layer.

---

## 4. Retro-compatible authoring protocol

To keep **one source of truth** (the repo's `agents/*.agent.md`) and ship to all four hosts:

### Rule 1 — Author the repo file in "superset" frontmatter

Keep the Copilot-style `tools:` field (Copilot reads it; Claude/opencode ignore unknown tool names quietly) **and** layer host-specific extras under clearly-namespaced keys that other hosts drop silently:

```markdown
---
name: 'SDLC: Frontend Engineer'
description: 'Senior frontend engineering — UI, state, WCAG 2.2 AA, Core Web Vitals.'
tools: [vscode, execute, read, agent, edit, search, web, browser, todo]
# --- Claude Code extras (ignored by Copilot/opencode/Cursor) ---
mode: subagent
model: inherit
toolsClaude: [Read, Edit, Write, Bash, Grep, Glob, WebFetch, WebSearch, Skill, Agent]
permissionMode: acceptEdits
skills: [sdlc-frontend-engineer, sdlc-shared-memory, web-accessibility-audit, web-performance-budget]
---
```

Why this is safe:
- **Copilot** reads `name`, `description`, `tools`; ignores `mode`/`model`/`toolsClaude`/`permissionMode`/`skills`.
- **opencode** reads `mode`, ignores `tools` (unknown → `options`); other hosts' extras also drop into `options` harmlessly.
- **Claude Code** reads `name`, `description`, `tools` (but the *values* are Copilot names → no real scoping), `mode` (ignored), `model`, `permissionMode`, `skills` ← these extras give it first-class behavior. The `tools:` line stays Copilot-flavoured but Claude tolerates unknown tool names by dropping them; if you want real scoping in Claude, switch `tools:` to the Claude list (Rule 2 covers via the adapter rather than touching the source).
- **Cursor** ignores everything except `description` (and `globs`/`alwaysApply` added by the adapter's `.mdc` wrapper).

### Rule 2 — Don't hand-translate; let the adapter emit per-host files

[`scripts/agent-frontmatter-adapter.py`](../../scripts/agent-frontmatter-adapter.py) reads a repo `agents/<name>.agent.md` and emits:

- a **Claude** subagent under `.claude/agents/<name>.md` with Claude tool names, `permissionMode`, and `skills:` preload;
- an **opencode** subagent under `.opencode/agent/<name>.md` with `mode`/`permission`/`description` and the body unchanged;
- a **Cursor** rule under `.cursor/rules/<name>.mdc` with `description` + `globs` + the body;
- (optional) **superset** frontmatter written back into the source file so the repo file itself becomes cross-host loadable.

Re-run it any time the repo agents change; it is idempotent and only rewrites the generated files, not your hand-authored source (unless you opt into the `--backport-superset` mode).

### Rule 3 — Keep skills as the portable knowledge layer

`SKILL.md` files already use only `name`+`description`, which every host accepts. **Do not** add host-specific keys to skill frontmatter. Hosts reach skills via:
- opencode: `skills.paths` (auto-scan) ← done in `docs/opencode.json`.
- Claude Code: `skills:` preload list on each agent (adapter injects it) + auto-discovery in `.claude/skills/`.
- Copilot: `AGENTS.md` reference; loaded on demand.
- Cursor: `.mdc` wrapper that points at the skill file.

### Rule 4 — Put cross-cutting run rules in `AGENTS.md`, not in every agent

`AGENTS.md` (read by Claude Code, Copilot cloud agent, Antigravity, and many agentic hosts) is the *cheapest* cross-host seam. Put the `.sdlc/` contract, build/test/lint commands, and the "Definition of Done requires cited command+result" rule there once, not in each agent's body.

### Rule 5 — MCP is per-host config, not per-agent

MCP server **definitions** belong in:
- `.github/mcp.json` (Copilot cloud agent; secret prefix `COPILOT_MCP_`),
- `.vscode/mcp.json` or `mcp.json` (Antigravity/Cursor),
- `.mcp.json` (Claude Code global),
- `mcp:` block in `opencode.json` (opencode),

or inline in a single subagent's `mcpServers:` (Claude Code). Don't embed MCP server tokens inside agent files — keep secrets out of version-controlled agent bodies.

---

## 5. What I'd need to change in the repo to *fully* close the gap (optional backport)

These are the changes the adapter applies *to the generated* files; the lists below are what would go into the **source** files if the team chooses to make the repo agents cross-host loadable directly (i.e., without running the adapter).

For each `agents/sdlc-*.agent.md` and `agents/web-*.agent.md`:
- Add `mode:` (`primary` for the orchestrator, `subagent` for the rest, `all` for the autonomous standalone agents).
- Add `permission:` / `permissionMode:` per the role's write surface (see §6).
- Add `skills:` preload (matching skill folder + `sdlc-shared-memory`; plus a11y/perf budgets for frontend roles).
- For browser-dependent roles: `mcpServers:` referencing `playwright`.

For each implementation role, the Claude `tools:` list should be `[Read, Edit, Write, Bash, Grep, Glob, WebFetch, WebSearch, Skill, Agent]`; for read-only roles `[Read, Grep, Glob, WebFetch, Skill, Agent]` plus `permissionMode: plan`.

> Choosing to backport into source is a **team policy** call — see `docs/opencode.json` for the **fully-populated, ready-to-paste** opencode version that already encodes every decision (38 agents, 12 commands, 10 instructions, 2 MCP servers, `sdlc-orchestrator` as default agent, per-role permissions). For Claude Code/Cursor, run the adapter.

---

## 6. Per-role permission & tool presets (used by the adapter and `docs/opencode.json`)

| Role bucket | opencode `permission` | Claude `tools` + `permissionMode` | Reason |
| --- | --- | --- | --- |
| **Implementation** (developer, backend, frontend, fullstack, db-developer, cybersecurity-developer, qa-tester, devops, technical-writer, web-design-system, web-performance, Beast, CoderBeast, ExpertCoder, gpt-5-beast-mode, expert-react-frontend) | `{ "edit": "allow", "bash": "ask" }` | `[Read, Edit, Write, Bash, Grep, Glob, WebFetch, WebSearch, Skill, Agent]` + `acceptEdits` | writes product code + runs builds/tests; ask before bash for safety |
| **Design / research** (orchestrator, software-architect, ux-ui-designer, db-architect, cybersecurity-architect, product-manager, responsible-ai, scrum-master, planning-agent, refine-issue, modernization, context-researcher) | `{ "edit": { "*": "deny", ".sdlc/**": "allow", "docs/**": "allow", ".github/**": "allow" }, "bash": "ask" }` | `[Read, Edit (scoped to .sdlc/, docs/), Bash, Grep, Glob, WebFetch, Skill, Agent]` + `plan` or `default` | writes only shared state + docs, never product code |
| **Pure review/audit** (governance-reviewer, electron-angular-native, RepositoryPathAuditor-read-only-mode, scientific-paper-research, search-ai-optimization-expert, simple-app-idea-generator) | `{ "edit": "deny", "bash": "ask" }` | `[Read, Grep, Glob, WebFetch, Skill, Agent]` + `plan` | reads-only review/research |

---

## 7. Adapter reference

```
scripts/agent-frontmatter-adapter.py --src agents/sdlc-frontend-engineer.agent.md \
        --claude .claude/agents/sdlc-frontend-engineer.md \
        --opencode .opencode/agent/sdlc-frontend-engineer.md \
        --cursor .cursor/rules/sdlc-frontend-engineer.mdc
```

Flags:
- `--src` (required): path to repo agent.
- `--claude` / `--opencode` / `--cursor`: emit that host's file at the given path.
- `--bucket implementation|research|review`: select the tool/permission preset from §6 (auto-detected from the description keywords if omitted).
- `--skills a,b,c`: extra skills to preload in the Claude file (auto-defaults to `sdlc-shared-memory` + the matching role skill).
- `--backport-superset`: rewrite the source `--src` file's frontmatter with the portable superset from Rule 1 (off by default — only generated files are touched).
- `--mcp playwright`: add an inline `mcpServers:` entry for browser-driven roles (Claude target only).
- `--globs "**/*.tsx"`: a glob for the Cursor `.mdc` file (otherwise `alwaysApply: true`).

The script is idempotent and only edits frontmatter; the agent's markdown **body** is passed through unchanged to every target.

---

## 8. Concrete call sites ("when to use which agent")

This is encoded in `docs/opencode.json`'s `description` fields so the host surfaces them in the picker. Read the `description` of any agent entry in that file for its trigger, and the `permission` block for its write surface. Sample mapping:

| User says… | Call |
| --- | --- |
| "set up the SDLC workspace for this repo" | `sdlc-orchestrator` via `/sdlc-init` |
| "design the architecture / write ADRs" | `sdlc-software-architect` |
| "design the data model / schema" | `sdlc-db-architect` |
| "design the API and write contracts" | `sdlc-backend-engineer` |
| "implement the UI components" | `sdlc-frontend-engineer` |
| "build the vertical slice end-to-end" | `sdlc-fullstack-engineer` |
| "threat-model this surface" | `sdlc-cybersecurity-architect` |
| "fix the OWASP findings" | `sdlc-cybersecurity-developer` |
| "write tests / enforce the quality gate" | `sdlc-qa-tester` |
| "configure the pipeline / IaC" | `sdlc-devops-engineer` |
| "write the API reference / tutorial" | `sdlc-technical-writer` |
| "define user stories / prioritize backlog" | `sdlc-product-manager` |
| "audit WCAG / accessibility" | `sdlc-responsible-ai` (+ `sdlc-ux-ui-designer` for specs) |
| "extend the design tokens / primitives" | `web-design-system-engineer` |
| "this route is over LCP budget" | `web-performance-engineer` |
| "plan but don't code" | `planning-agent` |
| "investigate the bug / find root cause" | `context-researcher` |
| "review this Electron/Angular/native code" | `electron-angular-native` |
| "write a reusable prompt file" | `PromptFileAuthor` |
| "audit repo structure freshness" | `RepositoryPathAuditor` |
| "review agent safety/governance" | `agent-governance-reviewer` |
| "refine this GitHub issue" | `refine-issue` |
| "modernize this legacy project" | `modernization` |
| "do the whole task autonomously" | `Beast` / `CoderBeast` / `ExpertCoder` / `gpt-5-beast-mode` |
| "advanced React 19 work" | `expert-react-frontend-engineer` |
| "literature review" | `scientific-paper-research` |
| "SEO / AEO / GEO advice" | `search-ai-optimization-expert` |
| "brainstorm an app idea" | `simple-app-idea-generator` |

---

## See also

- Ready-to-paste opencode config: [`docs/opencode.json`](../opencode.json)
- Per-host install guides: [opencode](opencode.md) · [Claude Code](claude-code.md) · [GitHub Copilot](github-copilot.md) · [Cursor](cursor.md)
- Adapter script: [`scripts/agent-frontmatter-adapter.py`](../../scripts/agent-frontmatter-adapter.py)
- Legacy Copilot-flavoured MCP reference: [`docs/mcp-integration-guide.md`](../mcp-integration-guide.md)