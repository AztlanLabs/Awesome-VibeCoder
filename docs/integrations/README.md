# Integration Guides

One file per host. Each guide is a standalone, step-by-step walkthrough for wiring **this repository's** assets (agents, skills, instructions, workflows, MCP) into a specific AI coding tool, then running a canonical SDLC session against the `.sdlc/` shared state.

## Available guides

| Host | File | What it links |
| --- | --- | --- |
| **opencode** | [opencode.md](opencode.md) | `.opencode/agent/`, `.opencode/skills/`, `opencode.json` `instructions`, `command:`, `mcp:` |
| **Claude Code** | [claude-code.md](claude-code.md) | `.claude/agents/`, `.claude/skills/`, `CLAUDE.md`, `.mcp.json`, `skills:` preload |
| **GitHub Copilot** (VS Code + Copilot cloud agent) | [github-copilot.md](github-copilot.md) | `.github/copilot-instructions.md`, `.github/instructions/`, `AGENTS.md`, `.github/prompts/`, chat modes, `.github/mcp.json` |
| **Cursor** | [cursor.md](cursor.md) | `.cursor/rules/*.mdc`, `.cursor/mcp.json`, agentic rules |
| **Antigravity** (Google) | [antigravity.md](antigravity.md) | root `AGENTS.md`, `.vscode/mcp.json`, project rules |

A cross-host MCP reference lives in the older [MCP Integration Guide](../mcp-integration-guide.md) (Copilot-flavoured). Each host guide re-states the host-specific MCP shape so it is self-contained.

## Ready-to-paste config & cross-host compatibility

- **[`docs/opencode.json`](../opencode.json)** — fully populated opencode config: all **38 agents** wired as inline `agent:` entries with per-role `mode`/`permission`, `skills.paths` pointing at `./skills` (zero-copy, all 47 skills auto-load), curated `instructions:`, `command:` slash-commands for `/sdlc-init`, `/sdlc-sequential`, `/sdlc-parallel`, `/sdlc-status`, `/sdlc-handoff`, `mcp:` for Playwright + GitHub, and `default_agent: sdlc-orchestrator`. Drop it at the repo root (or copy into a target project and adjust paths).
- **[Cross-Host Compatibility & Claude Readiness](compatibility.md)** — frontmatter field matrix, tool-name aliasing, what's missing for Claude Code, the retro-compatible authoring protocol, per-role presets, and the "when to call which agent" table.
- **[`scripts/agent-frontmatter-adapter.py`](../../scripts/agent-frontmatter-adapter.py)** — idempotent translator that turns one repo `agents/*.agent.md` into a Claude `.claude/agents/*.md`, an opencode `.opencode/agent/*.md`, or a Cursor `.cursor/rules/*.mdc` (or backports a portable superset frontmatter into the source). Powers the compatibility guide's Rule 2.
- **[`docs/matrix.md`](../matrix.md)** — a generated, one-row-per-agent table cross-tabulating every agent against all 4 hosts and the 5 retro-compatibility rules; a one-glance audit page.

## How the asset types map

| Repository asset | Where it lives | What it does |
| --- | --- | --- |
| Agents | `agents/*.agent.md` (incl. `agents/sdlc-*.agent.md`) | Role personas with `tools`, descriptions, and a system prompt body |
| Skills | `skills/<name>/SKILL.md` | Trigger-conditioned knowledge packs loaded by the model |
| Instructions | `instructions/*.instructions.md` | Globbed (`applyTo`) language/framework/security/rules files |
| Workflows | `workflows/*.workflow.md` | Orchestration blueprints (sequential / parallel) for the SDLC team |
| Shared state | `.sdlc/` (created at runtime) | Centralized memory the agents read/write to coordinate |

The guides below all converge on the same end-state: a host that can run any `sdlc-*` agent individually, or run the Orchestrator to drive the full SDLC pipeline against `.sdlc/`.

## Recommended starting point

If you only read one guide, read the one for your host. If your host is not listed, the [AGENTS.md / MCP universal pattern](opencode.md#step-7-mcp-servers) (each host guide's "MCP servers" step) is the lowest-common-denominator approach that works in any tool supporting `AGENTS.md` + MCP.