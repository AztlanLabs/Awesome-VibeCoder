# Awesome-VibeCoder — Implementation Plan

> Execution plan for [`docs/roadmap.md`](roadmap.md). Derived from the Planning Agent's review of the roadmap against the live repository (all roadmap claims verified: 35 agents, 42 skills, hardcoded path bug on `scripts/validate-assets.py:6`, empty `.github/workflows/`, stale "16 specialized roles" in `README.md:56`, no `CHANGELOG.md`).

**Status legend**: `[ ]` not started · `[~]` in progress · `[x]` completed

---

## Completion Protocol (read before touching any checkbox)

1. **One part = one checkbox.** Each `- [ ]` line below is an atomic task with an exact file target and a runnable validation command.
2. **Mark in-progress when you start.** Change `- [ ]` → `- [~]` for the single task you are working on. Only one task should be `[~]` at a time per phase.
3. **Mark completed only after validation passes.** When the task's `TEST-*` command exits 0, change `- [~]` → `- [x]`. Do **not** mark completed on prose summary alone — this mirrors the repo's own evidence gate (AGENTS.md §3).
4. **Update all related `.md` files in the same commit as the checkbox.** Every task lists a `Updates:` line naming the markdown files that must be edited alongside it (catalogs, counts, trees, indexes). A task is not complete until those files are reconciled.
5. **Cite the command + result.** When marking `[x]`, the commit message or PR description must include the real command run and its result (e.g. `python3 scripts/validate-assets.py — exit 0`).
6. **Do not skip phases.** Phase N depends on Phase N-1's CI/tests being green. P0 is the foundation for everything after it.
7. **One phase at a time.** Do not start Phase 1 tasks until all Phase 0 checkboxes are `[x]` and `.github/workflows/validate.yml` is green on the default branch.

---

## Phase 0 — P0: Maintenance & correctness (foundation; one weekend)

**GOAL-0**: Harden what is already shipped so all later tiers build on verified ground.

### 0.1 🐛 Fix hardcoded workspace path in validator
- [x] **TASK-0.1**: Replace `workspace_dir = "/home/crowne/Documents/Documents/VS Code/Awesome-VibeCoder"` on line 6 of `scripts/validate-assets.py` with `workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))`.
  - **Files**: `scripts/validate-assets.py`
  - **Updates**: none
  - **TEST-0.1**: `python3 scripts/validate-assets.py` exits 0 when run from any cwd (e.g. `cd /tmp && python3 /path/to/scripts/validate-assets.py`).

### 0.2 Adapter self-tests
- [x] **TASK-0.2**: Create `scripts/test_adapter.py` covering `detect_bucket`, `detect_mode`, `default_skills_for`, `slug_from_name`, the three-bucket presets, and `--backport-superset` round-trip. Use `unittest` or `pytest`; assert against known agent files (e.g. `agents/sdlc-orchestrator.agent.md`).
  - **Files**: `scripts/test_adapter.py` (new)
  - **Updates**: none
  - **TEST-0.2**: `python3 -m pytest scripts/test_adapter.py` (or `python3 scripts/test_adapter.py`) exits 0.

### 0.3 CI workflow
- [x] **TASK-0.3**: Create `.github/workflows/validate.yml` running on PR: (a) `python3 scripts/validate-assets.py`, (b) loop every `agents/*.agent.md` through `scripts/agent-frontmatter-adapter.py --stdout` (zero failures), (c) `python3 -c "import json; json.load(open('docs/opencode.json'))"`, (d) re-parse `docs/integrations/*.md` for `## Step N` headings.
  - **Files**: `.github/workflows/validate.yml` (new)
  - **Updates**: `CHANGELOG.md` (add entry once TASK-0.7 lands)
  - **TEST-0.3**: workflow file parses as valid YAML; `python3 scripts/agent-frontmatter-adapter.py --src agents/sdlc-orchestrator.agent.md --stdout` succeeds for all 35 agents locally.
  - **Depends on**: TASK-0.1, TASK-0.2

### 0.4 Reconcile role counts
- [x] **TASK-0.4**: Change "16 specialized roles" → accurate current count (35) in `README.md` line 56; cross-check `docs/README.sdlc-system.md`, `docs/README.agents.md`, `AGENTS.md` §5.
  - **Files**: `README.md`, `docs/README.sdlc-system.md`, `docs/README.agents.md`
  - **Updates**: `AGENTS.md` (§5 is the source of truth — confirm count matches `ls agents/*.agent.md | wc -l`)
  - **TEST-0.4**: `grep -rn "16 specialized roles" README.md docs/` returns nothing.

### 0.5 Standardize the `.sdlc/` layout
- [x] **TASK-0.5**: Use `skills/sdlc-shared-memory/SKILL.md` as the authoritative `.sdlc/` scaffold; ensure `contracts/test-strategy.md` and `memory.md` appear in the tree in `README.md`, `AGENTS.md` §2, and the skill.
  - **Files**: `README.md`, `AGENTS.md`, `skills/sdlc-shared-memory/SKILL.md`
  - **Updates**: `docs/README.sdlc-system.md`
  - **TEST-0.5**: `grep -l "test-strategy.md" README.md AGENTS.md skills/sdlc-shared-memory/SKILL.md` returns all three files.

### 0.6 CONTRIBUTING.md cross-host subsection
- [x] **TASK-0.6**: Append a "Cross-host contributions" subsection to `CONTRIBUTING.md` referencing the 5 retro-compat rules, `docs/integrations/compatibility.md`, and instructing contributors to run the adapter after touching `tools:`.
  - **Files**: `CONTRIBUTING.md`
  - **Updates**: none
  - **TEST-0.6**: `grep -c "Cross-host contributions\|agent-frontmatter-adapter" CONTRIBUTING.md` returns ≥ 1.

### 0.7 CHANGELOG.md
- [x] **TASK-0.7**: Create `CHANGELOG.md` at repo root in Keep-a-Changelog format; add an `[Unreleased]` entry summarizing the cookbook + integration-guide + AGENTS.md work.
  - **Files**: `CHANGELOG.md` (new)
  - **Updates**: `README.md` (add a link to `CHANGELOG.md` in the project links section if one exists)
  - **TEST-0.7**: `head -1 CHANGELOG.md` returns `# Changelog` (or equivalent); file contains an `## [Unreleased]` heading.

**Phase 0 gate**: all seven checkboxes `[x]` AND `.github/workflows/validate.yml` green on the default branch. Do not start Phase 1 until this holds.

---

## Phase 1 — P1: High-leverage SDLC + web gaps

**GOAL-1**: Close the obvious holes in the SDLC role catalog and add the missing workflows/commands/templates.

### 1A. New agents

- [x] **TASK-1.1**: Create `agents/sdlc-accessibility-specialist.agent.md` (research bucket). Loads `web-accessibility-audit`, `sdlc-shared-memory`. Writes `.sdlc/contracts/a11y-requirements.md` + remediation reports to `docs/a11y/`. Follow superset frontmatter (Rule 1) + canonical 7-section body.
  - **Files**: `agents/sdlc-accessibility-specialist.agent.md` (new)
  - **Updates**: `AGENTS.md` §5 (add row), `docs/opencode.json` (agents array), `docs/README.agents.md` (count)
  - **TEST-1.1**: `python3 scripts/agent-frontmatter-adapter.py --src agents/sdlc-accessibility-specialist.agent.md --stdout` succeeds.

- [x] **TASK-1.2**: Create `agents/sdlc-code-reviewer.agent.md` (review bucket, `edit: deny`). Consumes `instructions/code-review-generic.instructions.md`; emits findings to `.sdlc/decisions/review-*.md`.
  - **Files**: `agents/sdlc-code-reviewer.agent.md` (new)
  - **Updates**: `AGENTS.md` §5, `docs/opencode.json`, `docs/README.agents.md`
  - **TEST-1.2**: adapter `--stdout` succeeds; frontmatter `tools` does not include `edit`.

- [x] **TASK-1.3**: Create `agents/sdlc-api-designer.agent.md` (research bucket). Owns `.sdlc/contracts/api-contracts.md` (split from Backend Engineer). Covers OpenAPI/AsyncAPI, versioning, idempotency, pagination, error taxonomy.
  - **Files**: `agents/sdlc-api-designer.agent.md` (new), `agents/sdlc-backend-engineer.agent.md` (change writer → reader), `skills/sdlc-backend-engineer/SKILL.md` (reflect new reader role)
  - **Updates**: `AGENTS.md` §5, `docs/opencode.json`, `docs/README.agents.md`, `skills/sdlc-shared-memory/SKILL.md` (ownership table: api-contracts.md primary writer → API Designer)
  - **TEST-1.3**: adapter `--stdout` succeeds for both new and edited agent; `grep -c "api-contracts.md" skills/sdlc-shared-memory/SKILL.md` reflects the new owner.

- [x] **TASK-1.4**: Register TASK-1.1–1.3 in `AGENTS.md` §5 catalog (add rows) and `docs/opencode.json` (agents array).
  - **Files**: `AGENTS.md`, `docs/opencode.json`
  - **Updates**: `docs/README.agents.md` (count → 38), `README.md` (role count line if present)
  - **TEST-1.4**: `grep -c "sdlc-accessibility-specialist\|sdlc-code-reviewer\|sdlc-api-designer" AGENTS.md` returns ≥ 3; `python3 -c "import json; json.load(open('docs/opencode.json'))"` exits 0.
  - **Depends on**: TASK-1.1, TASK-1.2, TASK-1.3

### 1B. New skills

- [x] **TASK-1.5**: Create `skills/api-contract-first/SKILL.md` — OpenAPI 3.1 / AsyncAPI / JSON-Schema patterns, deprecation, idempotency-key, problem+json, cursor pagination. Frontmatter: `name` + `description` only (Rule 3).
  - **Files**: `skills/api-contract-first/SKILL.md` (new)
  - **Updates**: `AGENTS.md` (§5 Load column for API Designer), `docs/README.skills.md` (count), `docs/opencode.json` (skills.paths already globs, but confirm)
  - **TEST-1.5**: frontmatter contains exactly `name` + `description` keys.
  - **Depends on**: TASK-1.3

- [x] **TASK-1.6**: Create `skills/observability-three-pillars/SKILL.md` — OTLP/JSON logs, RED/USE metrics, distributed tracing, SLO/SLI/error-budget, RUM vs LAB.
  - **Files**: `skills/observability-three-pillars/SKILL.md` (new)
  - **Updates**: `docs/README.skills.md` (count), `docs/opencode.json`
  - **TEST-1.6**: frontmatter contains exactly `name` + `description` keys.

- [x] **TASK-1.7**: Create `skills/prompt-eval-and-regression/SKILL.md` — golden outputs, model-graded evals, scorer matrix, CI integration.
  - **Files**: `skills/prompt-eval-and-regression/SKILL.md` (new)
  - **Updates**: `docs/README.skills.md` (count), `docs/opencode.json`, `agents/PromptFileAuthor.agent.md` (Load line if applicable)
  - **TEST-1.7**: frontmatter contains exactly `name` + `description` keys.

### 1C. New workflows

- [x] **TASK-1.8**: Create `workflows/bug-triage.workflow.md` — Context Researcher → Cybersecurity Architect (if security) → Developer → QA → DevOps.
  - **Files**: `workflows/bug-triage.workflow.md` (new)
  - **Updates**: `docs/README.workflows.md` (count + entry), `AGENTS.md` §6 (mention), `docs/opencode.json` (workflows array if present)
  - **TEST-1.8**: file exists and contains the 5-role sequence.

- [x] **TASK-1.9**: Create `workflows/docs-regen.workflow.md` — Technical Writer ← `.sdlc/contracts/api-contracts.md` → RepositoryPathAuditor → Responsible AI.
  - **Files**: `workflows/docs-regen.workflow.md` (new)
  - **Updates**: `docs/README.workflows.md`, `AGENTS.md` §6, `docs/opencode.json`
  - **TEST-1.9**: file exists and contains the 3-role sequence.
  - **Depends on**: TASK-1.3

### 1D. Slash commands, templates, runbooks

- [x] **TASK-1.10**: Add slash commands `/review`, `/a11y`, `/explain`, `/implement`, `/test`, `/rfc`, `/pr` to `docs/opencode.json` mapped to the right agents.
  - **Files**: `docs/opencode.json`
  - **Updates**: `docs/integrations/opencode.md` (document the new commands)
  - **TEST-1.10**: `python3 -c "import json; d=json.load(open('docs/opencode.json')); cmds=d['command']; assert all(k in cmds for k in ['/review','/a11y','/explain','/implement','/test','/rfc','/pr'])"` exits 0. (Note: the real opencode schema key is `command`, singular — the original `slash_commands`/`commands` key names in this test were wrong and have been corrected.)
  - **Depends on**: TASK-1.4

- [x] **TASK-1.11**: Create `templates/` with `ADR.md`, `task.md`, `handoff.md`, `*.prompt.md`, `copilot-instructions.md`, `opencode.json` starter, `mcp.json` starters, `.sdlc/` skeleton files.
  - **Files**: `templates/` (new directory + files)
  - **Updates**: `README.md` (mention templates/ in the asset table), `AGENTS.md` §1 (add row to the asset-class table), `CONTRIBUTING.md` (point contributors at templates/)
  - **TEST-1.11**: `ls templates/ADR.md templates/task.md templates/handoff.md` succeeds.

- [x] **TASK-1.12**: Create `docs/recipes/author-agent.md`, `author-skill.md`, `author-instruction.md` with frontmatter templates, superset rule, adapter call, copy-paste skeleton.
  - **Files**: `docs/recipes/` (new)
  - **Updates**: `docs/README.agents.md`, `docs/README.skills.md`, `docs/README.instructions.md` (link to the relevant recipe), `AGENTS.md` §9 (link to recipes)
  - **TEST-1.12**: all three recipe files exist and each references `scripts/agent-frontmatter-adapter.py` or the superset rule.

**Phase 1 gate**: all twelve checkboxes `[x]` AND `python3 -c "import json; json.load(open('docs/opencode.json'))"` exits 0 AND `python3 scripts/validate-assets.py` exits 0.

---

## Phase 2 — P2: Ecosystem expansion (selective; pick ONE cluster)

**GOAL-2**: Broaden role coverage by exactly one cluster (Platform & SRE **or** Data & ML) plus the highest-demand instruction gaps. Do not attempt both clusters in a first pass.

### 2A. Role cluster — choose ONE (recommended: Platform & SRE)

- [ ] **TASK-2.1**: Create `agents/sdlc-sre.agent.md` (implementation) — runbooks, on-call, incident command, SLO/error-budget, postmortems.
  - **Files**: `agents/sdlc-sre.agent.md` (new)
  - **Updates**: `AGENTS.md` §5, `docs/opencode.json`, `docs/README.agents.md`, `README.md` (role count)
  - **TEST-2.1**: adapter `--stdout` succeeds.

- [ ] **TASK-2.2**: Create `agents/sdlc-finops-engineer.agent.md` (research) — cloud cost optimization, rightsizing, commitment planning.
  - **Files**: `agents/sdlc-finops-engineer.agent.md` (new)
  - **Updates**: `AGENTS.md` §5, `docs/opencode.json`, `docs/README.agents.md`, `README.md`
  - **TEST-2.2**: adapter `--stdout` succeeds.

- [ ] **TASK-2.3**: Create `skills/sre-incident-command/SKILL.md` and `skills/finops-cloud-cost/SKILL.md`.
  - **Files**: `skills/sre-incident-command/SKILL.md`, `skills/finops-cloud-cost/SKILL.md` (new)
  - **Updates**: `docs/README.skills.md` (count), `docs/opencode.json`, `AGENTS.md` §5 (Load column)
  - **TEST-2.3**: both frontmatters contain exactly `name` + `description` keys.
  - **Depends on**: TASK-2.1, TASK-2.2

- [ ] **TASK-2.4**: Register both new agents in `AGENTS.md` §5 and `docs/opencode.json`.
  - **Files**: `AGENTS.md`, `docs/opencode.json`
  - **Updates**: `docs/README.agents.md` (count), `README.md` (role count)
  - **TEST-2.4**: `ls agents/*.agent.md | wc -l` == count referenced in `AGENTS.md` §5.
  - **Depends on**: TASK-2.1, TASK-2.2

> **Option B (deferred): Data & ML** — `sdlc-data-engineer`, `sdlc-mlops-engineer`, `sdlc-evaluation-engineer` + 3 skills. Schedule after Option A lands. Do not check these in the same pass.

### 2B. Instruction gaps (batch by demand)

- [x] **TASK-2.5**: Add the top-requested instruction files in one batch: `swift`, `kotlin`, `python-fastapi`, `python-django`, `python-flask`, `rust-web-axum`, `deno`, `bun`, `solid`, `remix`, `nuxt`, `htmx`, `terraform`, `pulumi`, `postgres-tuning`, `openapi-3-1`, `asyncapi`, `otel-otelcol`, `git-conventional-commits`, `github-actions-workflows`, `sveltekit`. Each with `applyTo` frontmatter.
  - **Files**: `instructions/*.instructions.md` (20 new files — `sveltekit` deliberately skipped: `instructions/svelte.instructions.md` already has a full "SvelteKit Patterns" section covering routing/load functions/form actions/deployment end-to-end; a separate file would be pure duplication)
  - **Updates**: `docs/README.instructions.md` (count + entries), `AGENTS.md` §1 (instruction count if stated), `docs/opencode.json` (instructions array — left untouched; its curated list is deliberately cross-cutting/universal only, not per-framework)
  - **TEST-2.5**: each new file has valid `applyTo` frontmatter; `python3 scripts/validate-assets.py` exits 0.

- [ ] **TASK-2.6**: Create `agents/sdlc-localization-engineer.agent.md` (implementation) hooking the existing `localization.instructions.md`.
  - **Files**: `agents/sdlc-localization-engineer.agent.md` (new)
  - **Updates**: `AGENTS.md` §5, `docs/opencode.json`, `docs/README.agents.md`, `README.md`
  - **TEST-2.6**: adapter `--stdout` succeeds.

- [ ] **TASK-2.7**: Create `agents/sdlc-mobile-engineer.agent.md` (implementation, React Native/Flutter) loading `dart-n-flutter.instructions.md`.
  - **Files**: `agents/sdlc-mobile-engineer.agent.md` (new)
  - **Updates**: `AGENTS.md` §5, `docs/opencode.json`, `docs/README.agents.md`, `README.md`
  - **TEST-2.7**: adapter `--stdout` succeeds.

### 2C. Cookbook expansion (one framework at a time)

- [ ] **TASK-2.8**: Add `cookbook/web-dev/python/` (FastAPI streaming, async SQLAlchemy, AnyIO background tasks) with runnable `recipe/package.json` + README.
  - **Files**: `cookbook/web-dev/python/` (new)
  - **Updates**: `cookbook/README.md` (add entry), `cookbook/cookbook.yml` (if it indexes recipes), `AGENTS.md` §1 (cookbook row if it lists frameworks)
  - **TEST-2.8**: `cd cookbook/web-dev/python/recipe && npm install && npm run <script>` exits 0.

- [ ] **TASK-2.9**: Add `cookbook/web-dev/rust/` (axum SSE + backpressure, tower middleware).
  - **Files**: `cookbook/web-dev/rust/` (new)
  - **Updates**: `cookbook/README.md`, `cookbook/cookbook.yml`
  - **TEST-2.9**: recipe build/run command exits 0.

- [ ] **TASK-2.10**: Add `cookbook/web-dev/vertical-slices/` — one end-to-end recipe composing Backend + Frontend + QA + DS Engineer.
  - **Files**: `cookbook/web-dev/vertical-slices/` (new)
  - **Updates**: `cookbook/README.md`, `cookbook/cookbook.yml`, `docs/README.workflows.md` (cross-link)
  - **TEST-2.10**: recipe runs end-to-end.
  - **Depends on**: TASK-2.8

### 2D. New skills (security/CSS/frontend-testing/docs)

- [ ] **TASK-2.11**: Create `skills/security-supply-chain/SKILL.md` — SBOM (CycloneDX/Syft), SLSA, Sigstore/cosign, provenance, renovate policy.
  - **Files**: `skills/security-supply-chain/SKILL.md` (new)
  - **Updates**: `docs/README.skills.md`, `docs/opencode.json`, `agents/sdlc-cybersecurity-developer.agent.md` (Load line)
  - **TEST-2.11**: frontmatter contains exactly `name` + `description` keys.

- [x] **TASK-2.12**: Create `skills/css-architecture/SKILL.md` — ITCSS/CUBE/BEM, `@layer`, CSS modules vs CSS-in-JS, container queries.
  - **Files**: `skills/css-architecture/SKILL.md` (new)
  - **Updates**: `docs/README.skills.md`, `docs/opencode.json`, `agents/sdlc-frontend-engineer.agent.md` (Load line)
  - **TEST-2.12**: frontmatter contains exactly `name` + `description` keys.

- [ ] **TASK-2.13**: Create `skills/frontend-testing-library/SKILL.md` — RTL/Vitest/Playwright Component/Storybook interactions + visual regression.
  - **Files**: `skills/frontend-testing-library/SKILL.md` (new)
  - **Updates**: `docs/README.skills.md`, `docs/opencode.json`, `agents/sdlc-qa-tester.agent.md` (Load line)
  - **TEST-2.13**: frontmatter contains exactly `name` + `description` keys.

- [x] **TASK-2.14**: Create `skills/technical-writing-diataxis/SKILL.md` — Diátaxis validation, docstring-driven reference, plain-language score.
  - **Files**: `skills/technical-writing-diataxis/SKILL.md` (new)
  - **Updates**: `docs/README.skills.md`, `docs/opencode.json`, `agents/sdlc-technical-writer.agent.md` (Load line)
  - **TEST-2.14**: frontmatter contains exactly `name` + `description` keys.

**Phase 2 gate**: all checked tasks `[x]` AND `python3 scripts/validate-assets.py` exits 0 AND `python3 -c "import json; json.load(open('docs/opencode.json'))"` exits 0 AND `ls agents/*.agent.md | wc -l` == count in `AGENTS.md` §5.

---

## Phase 3 — P3: Polish & scale (opportunistic subset)

**GOAL-3**: Land the highest-payoff polish items; defer the L-tier generator/website work.

- [x] **TASK-3.1**: Create root `llms.txt` + `llms-full.txt` listing every agent/skill/instruction/workflow with one-line descriptions.
  - **Files**: `llms.txt`, `llms-full.txt` (new)
  - **Updates**: `README.md` (mention llms.txt), `AGENTS.md` (mention), `.gitignore` (ensure `/llms.txt` line is removed or kept consistent)
  - **TEST-3.1**: `llms.txt` line count == `ls agents/*.agent.md | wc -l` + `ls skills/*/SKILL.md | wc -l` + `ls instructions/*.instructions.md | wc -l` + `ls workflows/*.workflow.md | wc -l`.
  - **Depends on**: Phase 1 (so the catalog is stable)

- [x] **TASK-3.2**: Generate `docs/matrix.md` cross-tabulating agents × 4 hosts × 5 retro-compat rules.
  - **Files**: `docs/matrix.md` (new)
  - **Updates**: `AGENTS.md` §7 (link to matrix), `docs/integrations/README.md` (link)
  - **TEST-3.2**: file contains a table with one row per agent.
  - **Depends on**: Phase 1

- [x] **TASK-3.3**: Extend `scripts/validate-assets.py` (or new `scripts/lint-docs.py`) to enforce: canonical 7-section agent bodies, skill `When to Use`/`Patterns`/`Indicators of Done` headings, broken-link check (lychee), no absolute `file:///` in `docs/`, no hardcoded machine paths.
  - **Files**: `scripts/lint-docs.py` (new) or `scripts/validate-assets.py` (extended)
  - **Updates**: `.github/workflows/validate.yml` (add lint job), `CONTRIBUTING.md` (mention linter)
  - **TEST-3.3**: `python3 scripts/lint-docs.py` exits 0. Note: the 7-section/skill-heading checks are WARN-only (non-fatal) — dozens of pre-existing legacy skills/standalone agents predate the SDLC canonical structure and are documented as intentionally free-form (see `docs/README.agents.md`/`docs/README.skills.md`); only broken internal links, `file:///` paths, and hardcoded machine paths are hard-gated errors. Internal-link checking substitutes for `lychee` (no external-tool dependency); run `lychee --offline docs/ *.md` separately for external-URL checking.
  - **Depends on**: TASK-0.3

- [ ] **TASK-3.4**: Create `docs/integrations/mcp-catalog.md` enumerating recommended MCP servers with per-role grants.
  - **Files**: `docs/integrations/mcp-catalog.md` (new)
  - **Updates**: `docs/integrations/README.md` (link), `AGENTS.md` §8 (link), each `docs/integrations/<host>.md` (link to catalog)
  - **TEST-3.4**: file lists ≥ 8 servers with per-role grant rows.

- [ ] **TASK-3.5**: Create `ACCESSIBILITY.md` (WCAG 2.2 AA conformance target, tooling, AT matrix, pointer to Accessibility Specialist).
  - **Files**: `ACCESSIBILITY.md` (new)
  - **Updates**: `README.md` (link), `AGENTS.md` (link), `docs/integrations/README.md` (link)
  - **TEST-3.5**: file exists and references `sdlc-accessibility-specialist`.
  - **Depends on**: TASK-1.1

- [ ] **TASK-3.6**: Create `SECURITY.md` (reporting policy, supported versions, response SLAs, SBOM pointer).
  - **Files**: `SECURITY.md` (new)
  - **Updates**: `README.md` (link), `AGENTS.md` (link)
  - **TEST-3.6**: file exists and references the supply-chain skill or SBOM.
  - **Depends on**: TASK-2.11

- [ ] **TASK-3.7**: Adopt Renovate/Dependabot config for cookbooks; pin React 19 / Next 16 / Astro 5 / Svelte 5 / Vue 3 majors.
  - **Files**: `.github/renovate.json` (new)
  - **Updates**: `CONTRIBUTING.md` (mention), `cookbook/README.md` (mention)
  - **TEST-3.7**: `python3 -c "import json; json.load(open('.github/renovate.json'))"` exits 0.
  - **Depends on**: TASK-2.8

### Deferred (L-tier, schedule later — not in this plan's checkboxes)

- `npx create-vibecoder` generator CLI (roadmap 3.1)
- Online catalog generator + Astro site (3.2)
- `.sdlc/` JSON Schema + CLI validators (3.6)
- Storybook for prompts (3.7) — depends on TASK-1.7
- Definition-of-Done auto-validation hook (3.14)
- Adapter VS Code extension wrapper (3.15)
- i18n of core docs (3.13) — depends on TASK-2.6

**Phase 3 gate**: all checked tasks `[x]` AND `python3 scripts/lint-docs.py` exits 0 (once TASK-3.3 lands).

---

## Cross-cutting update checklist (run after every phase)

After marking a phase complete, verify these stay consistent — they are the files most prone to drift:

- [ ] `AGENTS.md` §5 role count == `ls agents/*.agent.md | wc -l`
- [ ] `AGENTS.md` §1 skill count == `ls skills/*/SKILL.md | wc -l`
- [ ] `docs/README.agents.md` count == `AGENTS.md` §5 count
- [ ] `docs/README.skills.md` count == `AGENTS.md` §1 count
- [ ] `docs/README.instructions.md` count == `ls instructions/*.instructions.md | wc -l`
- [ ] `docs/README.workflows.md` count == `ls workflows/*.workflow.md | wc -l`
- [ ] `README.md` role count == `AGENTS.md` §5 count
- [ ] `docs/opencode.json` parses: `python3 -c "import json; json.load(open('docs/opencode.json'))"`
- [ ] `python3 scripts/validate-assets.py` exits 0
- [ ] All 35+ agents pass adapter: `for f in agents/*.agent.md; do python3 scripts/agent-frontmatter-adapter.py --src "$f" --stdout >/dev/null || echo "FAIL: $f"; done` prints nothing

---

## Suggested sequencing

1. **Phase 0 first** — one commit set, one weekend. Hardens what's shipped.
2. **Phase 1 next** — Accessibility Specialist, Code Reviewer, API Designer + matching skills, two workflows, slash commands, templates, recipes. Highest SDLC leverage.
3. **Phase 2 selectively** — pick the role cluster (Platform & SRE recommended) that matches the contributing team's domain; add the instruction batch; expand the cookbook one framework at a time.
4. **Phase 3 opportunistically** — `llms.txt`, `docs/matrix.md`, `lint-docs.py` pay back the most and cost the least.

---

## Source

Derived from [`docs/roadmap.md`](roadmap.md) via the Planning Agent review. All roadmap claims were verified against the live repository on 2026-07-05.
