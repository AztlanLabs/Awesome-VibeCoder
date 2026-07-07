# Agent × Host × Retro-Compat Rule Matrix

> Cross-tabulates every agent in [`agents/`](../agents/) against the 4 supported hosts (Claude Code, opencode, GitHub Copilot, Cursor) and the [5 retro-compatibility rules](../AGENTS.md#7-cross-host-retro-compatibility--the-5-rules) from `AGENTS.md` §7. Generated from `AGENTS.md` §5's role catalog and verified against `scripts/agent-frontmatter-adapter.py` — see [`docs/integrations/compatibility.md`](integrations/compatibility.md) for the underlying per-host translation analysis this table summarizes per-agent.

## Legend

- **Bucket**: `implementation` (full edit), `research` (`.sdlc/`+`docs/`-scoped edit), `review` (read-only), or `Set up` (the orchestrator, always-on).
- **R1** Superset frontmatter authored (Rule 1) — `name`+`description`+`tools` present in source.
- **R2** Adapts cleanly (Rule 2) — `scripts/agent-frontmatter-adapter.py --src <file> --stdout` exits 0 for all 3 host targets.
- **R3** n/a for agents — Rule 3 (`name`+`description` only) governs `SKILL.md` files, not agents.
- **R4** Cross-cutting rules stay in `AGENTS.md` (Rule 4) — the agent body doesn't duplicate the `.sdlc/` contract, build/test commands, or the role catalog.
- **R5** No inline MCP servers (Rule 5) — the agent body contains no `mcpServers:`/`mcp:` block.

| Agent | Bucket | Claude Code | opencode | Copilot | Cursor | R1 | R2 | R3 | R4 | R5 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [SDLC Orchestrator](../agents/sdlc-orchestrator.agent.md) | Set up | primary/all | primary | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Software Architect](../agents/sdlc-software-architect.agent.md) | research | subagent, plan (read .sdlc/docs only) | edit scoped (.sdlc/**, docs/**) | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [UX/UI Designer](../agents/sdlc-ux-ui-designer.agent.md) | research | subagent, plan (read .sdlc/docs only) | edit scoped (.sdlc/**, docs/**) | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Accessibility Specialist](../agents/sdlc-accessibility-specialist.agent.md) | research | subagent, plan (read .sdlc/docs only) | edit scoped (.sdlc/**, docs/**) | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [DB Architect](../agents/sdlc-db-architect.agent.md) | research | subagent, plan (read .sdlc/docs only) | edit scoped (.sdlc/**, docs/**) | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [API Designer](../agents/sdlc-api-designer.agent.md) | research | subagent, plan (read .sdlc/docs only) | edit scoped (.sdlc/**, docs/**) | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Developer](../agents/sdlc-developer.agent.md) | implementation | subagent, acceptEdits | edit:allow | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Backend Engineer](../agents/sdlc-backend-engineer.agent.md) | implementation | subagent, acceptEdits | edit:allow | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Frontend Engineer](../agents/sdlc-frontend-engineer.agent.md) | implementation | subagent, acceptEdits | edit:allow | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Full Stack Engineer](../agents/sdlc-fullstack-engineer.agent.md) | implementation | subagent, acceptEdits | edit:allow | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [DB Developer](../agents/sdlc-db-developer.agent.md) | implementation | subagent, acceptEdits | edit:allow | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Cybersecurity Architect](../agents/sdlc-cybersecurity-architect.agent.md) | research | subagent, plan (read .sdlc/docs only) | edit scoped (.sdlc/**, docs/**) | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Cybersecurity Developer](../agents/sdlc-cybersecurity-developer.agent.md) | implementation | subagent, acceptEdits | edit:allow | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [QA Tester](../agents/sdlc-qa-tester.agent.md) | implementation | subagent, acceptEdits | edit:allow | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Code Reviewer](../agents/sdlc-code-reviewer.agent.md) | review | subagent, plan (read-only) | edit:deny | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [DevOps Engineer](../agents/sdlc-devops-engineer.agent.md) | implementation | subagent, acceptEdits | edit:allow | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Technical Writer](../agents/sdlc-technical-writer.agent.md) | implementation | subagent, acceptEdits | edit:allow | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Product Manager](../agents/sdlc-product-manager.agent.md) | research | subagent, plan (read .sdlc/docs only) | edit scoped (.sdlc/**, docs/**) | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Responsible AI](../agents/sdlc-responsible-ai.agent.md) | research | subagent, plan (read .sdlc/docs only) | edit scoped (.sdlc/**, docs/**) | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Scrum Master](../agents/sdlc-scrum-master.agent.md) | research | subagent, plan (read .sdlc/docs only) | edit scoped (.sdlc/**, docs/**) | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Web Design System Engineer](../agents/web-design-system-engineer.agent.md) | implementation | subagent, acceptEdits | edit:allow | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Web Performance Engineer](../agents/web-performance-engineer.agent.md) | implementation | subagent, acceptEdits | edit:allow | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Expert React Frontend Engineer](../agents/expert-react-frontend-engineer.agent.md) | implementation | subagent, acceptEdits | edit:allow | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Planning Agent](../agents/planning-agent.agent.md) | research | subagent, plan (read .sdlc/docs only) | edit scoped (.sdlc/**, docs/**) | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Context Researcher](../agents/context-researcher.agent.md) | research | subagent, plan (read .sdlc/docs only) | edit scoped (.sdlc/**, docs/**) | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Beast](../agents/Beast.agent.md) | implementation | subagent, acceptEdits | edit:allow | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [CoderBeast](../agents/CoderBeast.agent.md) | implementation | subagent, acceptEdits | edit:allow | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [ExpertCoder](../agents/ExpertCoder.agent.md) | implementation | subagent, acceptEdits | edit:allow | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [GPT 5 Beast Mode](../agents/gpt-5-beast-mode.agent.md) | implementation | subagent, acceptEdits | edit:allow | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Prompt File Author](../agents/PromptFileAuthor.agent.md) | research | subagent, plan (read .sdlc/docs only) | edit scoped (.sdlc/**, docs/**) | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Repository Path Auditor](../agents/RepositoryPathAuditor.agent.md) | review | subagent, plan (read-only) | edit:deny | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Agent Governance Reviewer](../agents/agent-governance-reviewer.agent.md) | review | subagent, plan (read-only) | edit:deny | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Refine Issue](../agents/refine-issue.agent.md) | research | subagent, plan (read .sdlc/docs only) | edit scoped (.sdlc/**, docs/**) | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Modernization](../agents/modernization.agent.md) | research | subagent, plan (read .sdlc/docs only) | edit scoped (.sdlc/**, docs/**) | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Electron / Angular / Native Reviewer](../agents/electron-angular-native.agent.md) | review | subagent, plan (read-only) | edit:deny | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Scientific Paper Research](../agents/scientific-paper-research.agent.md) | review | subagent, plan (read-only) | edit:deny | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Search & AI Optimization Expert](../agents/search-ai-optimization-expert.agent.md) | research | subagent, plan (read .sdlc/docs only) | edit scoped (.sdlc/**, docs/**) | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |
| [Idea Generator](../agents/simple-app-idea-generator.agent.md) | research | subagent, plan (read .sdlc/docs only) | edit scoped (.sdlc/**, docs/**) | as-is | via .mdc wrapper | ✅ | ✅ | n/a | ✅ | ✅ |

## Notes

- **Claude Code / opencode / Cursor** columns describe the *default* per-host behavior the adapter's bucket presets produce (see `scripts/agent-frontmatter-adapter.py --list-buckets`); they are not per-agent hand overrides unless a specific agent file documents one.
- **Copilot** is `as-is` for every agent because Copilot-style frontmatter (`name`, `description`, `tools`) is the repo's native authoring target (Rule 1) — no translation step is needed.
- R2 was verified for all 38 agents on the date this file was generated via: `for f in agents/*.agent.md; do python3 scripts/agent-frontmatter-adapter.py --src "$f" --claude ".claude/agents/$(basename "${f%.agent.md}").md" --stdout >/dev/null || echo "FAIL: $f"; done` — zero failures.
- R5 was verified repo-wide via `grep -rl "mcpServers\|mcp:" agents/*.agent.md` — zero matches.

Regenerate this table after adding, removing, or re-bucketing an agent — see [`docs/recipes/author-agent.md`](recipes/author-agent.md).
