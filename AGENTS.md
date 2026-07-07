# AGENTS.md

> The single cross-host entry point for **any** AI coding tool that reads `AGENTS.md` (Claude Code, Copilot cloud agent, Antigravity, opencode with `instructions:` reference, Cursor's composer, …). It is the prose mirror of [`docs/opencode.json`](docs/opencode.json): the same `.sdlc/` contract, the same role catalog, the same per-role call sites, the same build/test/lint commands, and the same retro-compatibility rules — expressed so a tool that consumes only Markdown can load them without a JSON parser.

This repository is **Awesome-VibeCoder**: a production toolbox of agents, skills, instructions, workflows, and cookbooks for AI-assisted software engineering. Read this file first; load `$SKILL.md` and `$AGENT.md` files on demand.

---

## 1. How this repo is organized

| Asset class | Path | What it is | How a host reaches it |
| --- | --- | --- | --- |
| **Agents** | `agents/*.agent.md` (38) | Role personas — `name`, `description`, `tools`, and a system-prompt body | per-host files emitted from the source by [`scripts/agent-frontmatter-adapter.py`](scripts/agent-frontmatter-adapter.py). Source frontmatter is the portable **superset**. |
| **Skills** | `skills/<name>/SKILL.md` (47) | Trigger-conditioned knowledge packs — `name` + `description` only | any host's `**/SKILL.md` scan. No host-only frontmatter. |
| **Instructions** | `instructions/*.instructions.md` (107) | Globbed (`applyTo`) language/framework/security/style rules | Copilot: `.github/instructions/`; opencode: `instructions:` array; Claude/Cursor/Antigravity: load on demand from this file. |
| **Workflows** | `workflows/*.workflow.md` (4) | SDLC sequential + parallel orchestration blueprints + bug-triage + docs-regen pipelines | the orchestrator agent loads them; see §5. |
| **Cookbook** | `cookbook/web-dev/` + `cookbook/copilot-sdk/` | Runnable recipes (Node.js, React, Next.js, Astro, Svelte, Vue + Copilot SDK) | recipes are copy-pasteable; not loaded by agents. |
| **Shared state** | `.sdlc/` (created at runtime) | Centralized memory the agents read/write to coordinate | see §3. |
| **Templates** | [`templates/`](templates/) | Copy-paste starters for ADRs, tasks, handoffs, prompts, MCP configs, and the `.sdlc/` skeleton | copy into a target project; see [CONTRIBUTING.md](CONTRIBUTING.md). |
| **opencode config** | [`docs/opencode.json`](docs/opencode.json) | Fully-populated, ready-to-paste opencode instantiation | opencode only; other hosts ignore it. |
| **LLM index** | [`llms.txt`](llms.txt) / [`llms-full.txt`](llms-full.txt) | One-line-per-asset manifest of every agent/skill/instruction/workflow | auto-discovered by LLM tools that read a repo's `llms.txt`; see [llmstxt.org](https://llmstxt.org). |
| **Host guide index** | [`docs/integrations/README.md`](docs/integrations/README.md) | Per-host install guides + cross-host compatibility analysis | human reading. |

---

## 2. The `.sdlc/` shared state directory

Agents do not operate in isolation. They read and write to a centralized, file-based state plane at the project root. **Source code, tests, and infrastructure files never go in `.sdlc/`** — only their paths + verification results are recorded there.

When the first SDLC agent runs against a project, it scaffolds `.sdlc/` (via the [`sdlc-shared-memory`](skills/sdlc-shared-memory/SKILL.md) skill) with this shape:

```text
.sdlc/
├── projectbrief.md          # Goals, scope, constraints
├── architecture.md          # System design, models, boundaries
├── techContext.md           # Technology stack + dependencies
├── activeContext.md         # Current focus
├── progress.md              # Task + lifecycle tracking (THE evidence log)
├── systemPatterns.md        # Conventions + coding standards
├── tasks/
│   └── _index.md            # Task lifecycle registry
├── decisions/
│   └── _index.md            # ADRs (Architecture Decision Records)
├── contracts/
│   ├── api-contracts.md     # owned by API Designer — consumed unchanged by Backend/Frontend/Full Stack/QA
│   ├── a11y-requirements.md # owned by Accessibility Specialist — consumed by Frontend/UX/QA
│   ├── db-schema.md         # owned by DB Architect
│   ├── security-requirements.md  # owned by Cybersecurity Architect
│   └── test-strategy.md     # owned by QA Tester
├── handoffs/
│   └── _index.md            # Agent-to-agent task transfer records
└── memory.md                # Cross-session memory + lessons learned
```

Each file has exactly **one primary writer role**. Every role reads `activeContext.md` + `progress.md` + the relevant `contracts/*.md` on startup before acting. See [`skills/sdlc-shared-memory/SKILL.md`](skills/sdlc-shared-memory/SKILL.md) for the full ownership table and the handoff/acknowledgement protocol.

---

## 3. The single most important rule: gate on evidence, not status

> A task is not complete until **`.sdlc/progress.md` cites the real command run and its result** (e.g. `npm test — 42 passed, 0 failed`). Writing `COMPLETED` in `tasks/_index.md` is a *status*, not *evidence*.

This is the contract every `sdlc-*.agent.md` enforces via its `Definition of Done` / `Indicators of Done` block. The orchestrator **does not advance an SDLC phase** when `progress.md` only contains a prose summary — it sends the work back to the role. If you cannot run a build or test command in the current environment, **say so explicitly** instead of describing the work as done.

Implementation roles additionally record a one-line pointer in `memory.md`: the real artifact paths changed + the verification result, not a prose retelling.

---

## 4. Build, test, lint

If this repository is itself the project, the commands are:

```bash
npm install
npm run build     # or: per-recipe build (see cookbook/web-dev/*/recipe/package.json)
npm test
npm run lint
```

For **target projects** consuming Awesome-VibeCoder, declare the commands in this `AGENTS.md` under a `## Build, test, lint` section appended by you (or in a project-local `opencode.json`/`.github/copilot-instructions.md`). Treat any agent file's `Definition of Done` as a hard gate that requires running them and citing the result in `.sdlc/progress.md`.

> When recipes from `cookbook/web-dev/` are run, each `recipe/package.json` declares its own script per recipe (e.g. `npm run streaming-responses`). See `cookbook/web-dev/<framework>/recipe/README.md`.

---

## 5. The role catalog (38 agents)

Roles map onto three write-surface buckets the adapter and `docs/opencode.json` use:

- **`implementation`** — writes product source/docs/tests; `edit: allow`, `bash: ask`.
- **`research`** — writes only `.sdlc/`, `docs/`, `.github/`; scoped `edit`.
- **`review`** — read-only analysis; `edit: deny`.

| Bucket | Role | Load | Trigger ("when to call") |
| --- | --- | --- | --- |
| **Set up** | [SDLC Orchestrator](agents/sdlc-orchestrator.agent.md) | always | "set up the SDLC workspace", "decompose the goal", "run the pipeline" |
| research | [Software Architect](agents/sdlc-software-architect.agent.md) | sdlc-software-architect | "design the architecture", "write ADRs", "evaluate trade-offs" |
| research | [UX/UI Designer](agents/sdlc-ux-ui-designer.agent.md) | sdlc-ux-ui-designer, web-design-system | "map user journeys", "design spec", "WCAG requirements" |
| research | [Accessibility Specialist](agents/sdlc-accessibility-specialist.agent.md) | sdlc-accessibility-specialist, web-accessibility-audit | "WCAG audit", "a11y requirements", "remediation report" |
| research | [DB Architect](agents/sdlc-db-architect.agent.md) | sdlc-db-architect | "design the data model", "schema", "indexing" |
| research | [API Designer](agents/sdlc-api-designer.agent.md) | sdlc-api-designer, api-contract-first | "design the API contract", "OpenAPI spec", "API versioning" |
| implementation | [Developer](agents/sdlc-developer.agent.md) | sdlc-developer | "implement the feature" (not owned by a specialist) |
| implementation | [Backend Engineer](agents/sdlc-backend-engineer.agent.md) | sdlc-backend-engineer, api-contract-first, observability-three-pillars | "implement endpoints against the API contract", "service layer", "data access" |
| implementation | [Frontend Engineer](agents/sdlc-frontend-engineer.agent.md) | sdlc-frontend-engineer, web-accessibility-audit, web-performance-budget, css-architecture | "implement UI components", "accessibility", "Core Web Vitals" |
| implementation | [Full Stack Engineer](agents/sdlc-fullstack-engineer.agent.md) | sdlc-fullstack-engineer | "build the vertical slice end-to-end" |
| implementation | [DB Developer](agents/sdlc-db-developer.agent.md) | sdlc-db-developer | "write migrations", "optimize queries" |
| research | [Cybersecurity Architect](agents/sdlc-cybersecurity-architect.agent.md) | sdlc-cybersecurity-architect | "threat-model this surface", "security controls design" |
| implementation | [Cybersecurity Developer](agents/sdlc-cybersecurity-developer.agent.md) | sdlc-cybersecurity-developer | "fix the OWASP findings", "secure coding", "SAST/DAST" |
| implementation | [QA Tester](agents/sdlc-qa-tester.agent.md) | sdlc-qa-tester | "write tests", "enforce quality gate", "coverage" |
| review | [Code Reviewer](agents/sdlc-code-reviewer.agent.md) | sdlc-code-reviewer | "review this PR", "code quality audit", "SOLID/security findings" |
| implementation | [DevOps Engineer](agents/sdlc-devops-engineer.agent.md) | sdlc-devops-engineer, observability-three-pillars | "configure CI/CD", "IaC", "monitoring", "rollback" |
| implementation | [Technical Writer](agents/sdlc-technical-writer.agent.md) | sdlc-technical-writer, technical-writing-diataxis | "write API reference / tutorial", "Diátaxis docs" |
| research | [Product Manager](agents/sdlc-product-manager.agent.md) | sdlc-product-manager | "user stories", "prioritize backlog", "RICE / MoSCoW" |
| research | [Responsible AI](agents/sdlc-responsible-ai.agent.md) | sdlc-responsible-ai, web-accessibility-audit | "bias review", "model card", "privacy review", "ethics" |
| research | [Scrum Master](agents/sdlc-scrum-master.agent.md) | sdlc-scrum-master | "sprint planning", "remove impediment", "retrospective" |
| implementation | [Web Design System Engineer](agents/web-design-system-engineer.agent.md) | web-design-system | "design tokens", "primitive APIs", "theming" |
| implementation | [Web Performance Engineer](agents/web-performance-engineer.agent.md) | web-performance-budget | "this route is over LCP budget", "perf gate failing" |
| implementation | [Expert React Frontend Engineer](agents/expert-react-frontend-engineer.agent.md) | (inline code examples) | "advanced React 19 work", "Server Components" |
| research | [Planning Agent](agents/planning-agent.agent.md) | planning scripts | "plan but do not code", "formal spec" |
| research | [Context Researcher](agents/context-researcher.agent.md) | context-researcher | "investigate the bug", "root-cause before implementation" |
| implementation | [Beast](agents/Beast.agent.md) | context-map first | "do the whole task autonomously, high precision" |
| implementation | [CoderBeast](agents/CoderBeast.agent.md) | prompt-driven flow | "drive this *.prompt.md to completion" |
| implementation | [ExpertCoder](agents/ExpertCoder.agent.md) | plan + execute | "plan rigorously then execute" |
| implementation | [GPT 5 Beast Mode](agents/gpt-5-beast-mode.agent.md) | tool-using autonomy | "tough multi-step troubleshooting" |
| research | [Prompt File Author](agents/PromptFileAuthor.agent.md) | prompt-builder, prompt-maintainer, prompt-eval-and-regression | "write a reusable .prompt.md", "sanitize my prompt" |
| review | [Repository Path Auditor](agents/RepositoryPathAuditor.agent.md) | technical-path-indexer | "audit repo structure freshness", "canonical technical paths" |
| review | [Agent Governance Reviewer](agents/agent-governance-reviewer.agent.md) | ai-prompt-engineering-safety-review | "governance review of agent code" |
| research | [Refine Issue](agents/refine-issue.agent.md) | refine-issue | "refine this GitHub issue" |
| research | [Modernization](agents/modernization.agent.md) | modernizationplaybook | "modernize this legacy project" |
| review | [Electron / Angular / Native Reviewer](agents/electron-angular-native.agent.md) | — | "review Electron + Angular + native stack" |
| review | [Scientific Paper Research](agents/scientific-paper-research.agent.md) | BGPT MCP | "literature review", "structured experimental data" |
| research | [Search & AI Optimization Expert](agents/search-ai-optimization-expert.agent.md) | — | "SEO", "AEO", "GEO advice" |
| research | [Idea Generator](agents/simple-app-idea-generator.agent.md) | — | "brainstorm an app idea" |

---

## 6. Workflow execution order

The [orchestrator](agents/sdlc-orchestrator.agent.md) loads one of two blueprints:

- **Sequential** ([`workflows/sdlc-sequential.workflow.md`](workflows/sdlc-sequential.workflow.md)) — one role at a time, user reviews between phases:
  Software Architect → UX/UI Designer → DB Architect → Backend Engineer → Frontend Engineer → Full Stack Engineer → DB Developer → Cybersecurity Architect → Cybersecurity Developer → QA Tester → DevOps Engineer → Technical Writer → Responsible AI → Scrum Master.

- **Parallel** ([`workflows/sdlc-parallel.workflow.md`](workflows/sdlc-parallel.workflow.md)) — phased concurrency with dependency gates:
  Phase 1 (conception): Architect + UX/UI Designer + DB Architect; Phase 2 (implementation): Backend + Frontend + DB Developer + Cybersecurity Architect; Phase 3 (testing & securing): QA + Cybersecurity Developer; Phase 4 (deployment): DevOps (sequential gate).

- **Bug Triage** ([`workflows/bug-triage.workflow.md`](workflows/bug-triage.workflow.md)) — short, incident-style fix loop:
  Context Researcher → Cybersecurity Architect (if security) → Developer → QA Tester → DevOps Engineer. Use for reported bugs, regressions, and post-deploy incidents — not for new feature work.

- **Docs Regeneration** ([`workflows/docs-regen.workflow.md`](workflows/docs-regen.workflow.md)) — pipeline-style doc refresh:
  Technical Writer ← `.sdlc/contracts/api-contracts.md` → RepositoryPathAuditor → Responsible AI. Use when the API contract changes, a new public surface is added, or a release cut is approaching.

Phases advance **only** when `progress.md` carries the real command + result for that phase — never on `COMPLETED` status alone.

---

## 7. Cross-host retro-compatibility — the 5 rules

The repo's `agents/*.agent.md` are authored once and shipped to Claude Code, Copilot, opencode, and Cursor **without per-host rewrites**, using these rules (full analysis: [`docs/integrations/compatibility.md`](docs/integrations/compatibility.md); adapter: [`scripts/agent-frontmatter-adapter.py`](scripts/agent-frontmatter-adapter.py)):

1. **Author the source in superset frontmatter.** Keep Copilot-style `tools:` plus host-neutral `name` + `description`. Add Claude-only extras (`mode`, `model`, `toolsClaude`, `permissionMode`, `skills`) under clearly-namespaced keys; non-matching hosts silently drop them.
2. **The adapter emits per-host files — don't hand-translate.** Run `scripts/agent-frontmatter-adapter.py --src agents/<name>.agent.md --claude … --opencode … --cursor …` to regenerate. The markdown **body** is passed through unchanged to every target. `--backport-superset` writes Rule 1's superset back into the source.
3. **Skills stay portable: `name` + `description` only.** Never add host-only keys (`tools`, `mode`, `permission`, `globs`, …) to a `SKILL.md`. Hosts reach skills through their tool's loader (opencode `skills.paths`, Claude `skills:` preload + discovery, Copilot/Antigravity `AGENTS.md` reference, Cursor `.mdc` wrapper). **This rule holds today across all 47 repo skills.**
4. **Put cross-cutting rules in `AGENTS.md` — this file — not in each agent.** The `.sdlc/` contract, build/test/lint commands, the evidence gate (§3), and the role catalog live here once. Agent bodies stay focused on role-specific workflow, patterns, indicators of done, and boundaries.
5. **MCP servers are per-host config, never per-agent.** Server definitions belong in `.github/mcp.json` (Copilot cloud agent; secret prefix `COPILOT_MCP_`), `mcp:` block in `opencode.json`, `.mcp.json` (Claude Code global), or `.vscode/mcp.json`/root `mcp.json` (Antigravity/Cursor); or **inline** in a single Claude subagent's `mcpServers:` only when a server must stay out of the main context. Tokens/secrets never go inside version-controlled agent bodies. **This rule holds today across all 38 repo agent files.**

> The concrete, fully-populated opencode instantiation of these rules is [`docs/opencode.json`](docs/opencode.json) — all 38 agents, the `./skills` path (zero-copy skill load), curated `instructions:`, `/sdlc-*` slash commands, Playwright + GitHub MCP, `default_agent: sdlc-orchestrator`. For Claude Code / Cursor, run the adapter; for Copilot/Antigravity, copy the relevant paths from this file.

> A generated, one-row-per-agent view of these rules cross-tabulated against all 4 hosts lives at [`docs/matrix.md`](docs/matrix.md).

---

## 8. Per-host quick-start (one-line each)

| Host | One-liner |
| --- | --- |
| **opencode** | Copy [`docs/opencode.json`](docs/opencode.json) to the project root (or use as-is inside this repo); `opencode` loads it. Full guide: [`docs/integrations/opencode.md`](docs/integrations/opencode.md). |
| **Claude Code** | `for f in agents/*.agent.md; do python3 scripts/agent-frontmatter-adapter.py --src "$f" --claude ".claude/agents/$(basename ${f%.agent.md}).md"; done`; symlink `skills/` to `.claude/skills/`; add `.mcp.json` for Playwright. Full guide: [`docs/integrations/claude-code.md`](docs/integrations/claude-code.md). |
| **GitHub Copilot** | Ensure `.github/copilot-instructions.md`, `.github/instructions/`, this `AGENTS.md`, and `.github/mcp.json` exist; enable custom instructions in repo Settings → Copilot. Full guide: [`docs/integrations/github-copilot.md`](docs/integrations/github-copilot.md). |
| **Cursor** | `for f in agents/*.agent.md; do python3 scripts/agent-frontmatter-adapter.py --src "$f" --cursor ".cursor/rules/$(basename ${f%.agent.md}).mdc" --globs "<globs>"; done`; add `AGENTS.md` (this file) at the root; drop `.cursor/mcp.json`. Full guide: [`docs/integrations/cursor.md`](docs/integrations/cursor.md). |
| **Antigravity** | This `AGENTS.md` is the manual; configure MCP via `.vscode/mcp.json` or root `mcp.json`. Full guide: [`docs/integrations/antigravity.md`](docs/integrations/antigravity.md). |

---

## 9. Coding style for contributions

- **Agents**: superset frontmatter (Rule 1); body keeps `Centralized State Architecture → Mandatory Skill Loading → Core Workflow → Definition of Done → Patterns, Rules & Structures → Indicators of Done → Boundaries (Do / Do Not Do)`. Runbook: [`docs/recipes/author-agent.md`](docs/recipes/author-agent.md).
- **Skills**: `name` + `description` only; body covers *patterns, rules, indicators of done* for the role. Runbook: [`docs/recipes/author-skill.md`](docs/recipes/author-skill.md).
- **Instructions**: `applyTo` glob frontmatter; one topic per file. Runbook: [`docs/recipes/author-instruction.md`](docs/recipes/author-instruction.md).
- See [`CONTRIBUTING.md`](CONTRIBUTING.md) for PR conventions, and [`docs/integrations/compatibility.md`](docs/integrations/compatibility.md) for the cross-host authoring protocol.