# Changelog

All notable changes to **Awesome-VibeCoder** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Cookbook** (`cookbook/web-dev/`, `cookbook/copilot-sdk/`): runnable recipes for Node.js, React, Next.js, Astro, Svelte, Vue, and the Copilot SDK. Each recipe is copy-pasteable and ships its own `package.json` script. See `cookbook/README.md` and `cookbook/cookbook.yml`.
- **Integration guides** (`docs/integrations/`): per-host install guides for opencode, Claude Code, GitHub Copilot, Cursor, and Antigravity, plus a cross-host compatibility analysis (`docs/integrations/compatibility.md`) and a host guide index (`docs/integrations/README.md`).
- **`AGENTS.md`**: the single cross-host entry point for any AI coding tool that reads `AGENTS.md` (Claude Code, Copilot cloud agent, Antigravity, opencode, Cursor). Mirrors `docs/opencode.json` in prose: the `.sdlc/` contract, the role catalog, per-role call sites, build/test/lint commands, and the 5-rule retro-compatibility protocol.
- **`docs/opencode.json`**: fully-populated, ready-to-paste opencode instantiation — all agents, the `./skills` path (zero-copy skill load), curated `instructions:`, `/sdlc-*` slash commands plus role-targeted commands, Playwright + GitHub MCP, `default_agent: sdlc-orchestrator`.
- **`scripts/agent-frontmatter-adapter.py`**: converts the repo's superset `agents/*.agent.md` frontmatter to host-specific formats (Claude Code, opencode, Cursor) without per-host rewrites. Idempotent; the markdown body is passed through unchanged. Supports `--backport-superset` to write the superset back into the source.
- **`scripts/test_adapter.py`**: 27 self-tests covering slug generation, bucket detection, mode detection, default-skill mapping, bucket presets, superset backport, and end-to-end stdout emission for every agent.
- **`.github/workflows/validate.yml`**: CI workflow that validates assets on PR/push — runs `validate-assets.py`, `test_adapter.py`, adapts every agent in `--stdout` mode, parses `docs/opencode.json`, and checks integration docs for required `##` headings.
- **`CHANGELOG.md`**: this file.
- **New agents** (Phase 1): `sdlc-accessibility-specialist` (research bucket — WCAG audits, owns `.sdlc/contracts/a11y-requirements.md`), `sdlc-code-reviewer` (review bucket, edit-deny — structured PR/code review findings), `sdlc-api-designer` (research bucket — owns `.sdlc/contracts/api-contracts.md`, split from Backend Engineer). Role catalog grew from 35 to 38 agents.
- **New skills** (Phase 1): `skills/api-contract-first` (OpenAPI 3.1/AsyncAPI/JSON-Schema, deprecation, idempotency-key, problem+json, cursor pagination), `skills/observability-three-pillars` (OTLP logs, RED/USE metrics, tracing, SLO/error-budget), `skills/prompt-eval-and-regression` (golden outputs, scorer matrix, CI regression gates — wired into `agents/PromptFileAuthor.agent.md` as Mode D). Skill count grew from 42 to 45.
- **New workflows** (Phase 1): `workflows/bug-triage.workflow.md` (Context Researcher → Cybersecurity Architect (if security) → Developer → QA Tester → DevOps Engineer) and `workflows/docs-regen.workflow.md` (Technical Writer ← API contract → RepositoryPathAuditor → Responsible AI).
- **New slash commands** (Phase 1): `/review`, `/a11y`, `/explain`, `/implement`, `/test`, `/rfc`, `/pr` added to `docs/opencode.json`'s `command:` block, each mapped to the relevant agent; documented in `docs/integrations/opencode.md`.

### Changed
- **Role count reconciliation**: updated stale "16 specialized roles" references to the current agent count across `README.md`, `docs/README.sdlc-system.md`, `docs/README.agents.md`, `AGENTS.md`, `CONTRIBUTING.md`, and `docs/integrations/*.md` (now 38 agents / 45 skills throughout).
- **`.sdlc/` layout standardization**: `README.md`, `AGENTS.md` §2, `skills/sdlc-shared-memory/SKILL.md`, and `docs/README.sdlc-system.md` now all show the same authoritative `.sdlc/` scaffold, including `contracts/a11y-requirements.md` (owned by Accessibility Specialist), `contracts/test-strategy.md` (owned by QA Tester), and `memory.md` (cross-session chronicle).
- **`CONTRIBUTING.md`**: appended a "Cross-host contributions" subsection documenting the 5 retro-compatibility rules, linking `docs/integrations/compatibility.md`, and instructing contributors to run `scripts/agent-frontmatter-adapter.py` after touching `tools:` or any host-only frontmatter key.
- **API contract ownership split**: `.sdlc/contracts/api-contracts.md` is now owned by the new API Designer role (previously the Backend Engineer wrote it). `agents/sdlc-backend-engineer.agent.md` and `skills/sdlc-backend-engineer/SKILL.md` updated to read and implement against the contract rather than author it.

### Fixed
- **`scripts/validate-assets.py`**: replaced a hardcoded workspace path with `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` so the validator runs cleanly from any working directory (previously only worked from the original author's cwd).
- **`docs/README.agents.md`**: fixed 20 broken agent links that pointed at a nonexistent doubled `agents/agents/` path segment.
- **`agents/PromptFileAuthor.agent.md`**: added the missing `Mode D` (Eval & Regression) section — the routing logic referenced it but the mode was never defined.
- **Stale `.sdlc/contracts/` tree info**: `README.md` and `docs/README.sdlc-system.md` listed `api-contracts.md` as Backend-Engineer-owned and a nonexistent `security-baseline.md` filename; corrected to API-Designer-owned `api-contracts.md` and the real `security-requirements.md`, and added the missing `a11y-requirements.md` row.
- **False `.github/` mirror claims**: `docs/README.skills.md`, `docs/README.instructions.md`, and `docs/integrations/github-copilot.md` claimed `.github/skills/`, `.github/instructions/`, and `.github/prompts/` were pre-populated mirrors of the root collections; they are not (empty on disk). Docs now describe the actual on-demand copy workflow.

### Notes
- **Phase 0 of `docs/implementation-plan.md` is complete**: all seven tasks (0.1–0.7) are marked `[x]` and validated by their respective `TEST-0.*` commands. The Phase 0 gate (all checkboxes `[x]` AND `.github/workflows/validate.yml` green on the default branch) is satisfied.
- **Phase 1 is substantially complete**: TASK-1.1 through 1.10 are done (3 new agents, 3 new skills, 2 new workflows, slash commands); TASK-1.11 (`templates/`) and TASK-1.12 (`docs/recipes/`) are in progress. See `docs/implementation-plan.md` for the current task list.
