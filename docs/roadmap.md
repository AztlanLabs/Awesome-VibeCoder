# Awesome-VibeCoder — Proposed Roadmap

A reviewed list of improvements, new agents, new skills, new instructions, new workflows, and tooling the repo could absorb next. Prioritized so a contributor can pick a tier and execute. Each item lists **what**, **why** (the gap it closes), **where** (target path), and an estimate.

Status of this doc: a **proposal** — none of it is implemented yet. Items marked **🐛 bug** are fixes to existing files.

Priority tiers:
- **P0 — maintenance & correctness** (do these first; they protect what's already there)
- **P1 — high-leverage gaps** (close obvious holes in the SDLC + web coverage)
- **P2 — ecosystem expansion** (broaden languages/frameworks/roles)
- **P3 — polish & scale** (quality-of-life, scale, automation)

Estimates: S (≤ half day), M (1–2 days), L (3–5 days).

---

## P0 — Maintenance & correctness

### 0.1 🐛 `scripts/validate-assets.py` — hardcoded workspace path
- **What**: line 6 hardcodes `workspace_dir = "/home/crowne/Documents/Documents/VS Code/Awesome-VibeCoder"`. Replace with `workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))`.
- **Why**: anyone else running it gets wrong results or false errors; CI on a fork would fail.
- **Where**: `scripts/validate-assets.py`.
- **Estimate**: S.

### 0.2 Add a CI workflow that runs the validator + adapter smoke test
- **What**: `.github/workflows/validate.yml` that on PR runs `python3 scripts/validate-assets.py`, then loops every `agents/*.agent.md` through `scripts/agent-frontmatter-adapter.py --stdout` (zero failures expected).
- **Why**: the repo now has a 5-rule retro-compatibility contract; a PR should not silently break it. No CI exists today (`.github/workflows/` is empty).
- **Estimate**: S.
- **Bonus**: a job that re-loads `docs/opencode.json` with `json` to prove it parses, and re-parses `docs/integrations/*.md` for the canonical `## Step N` headings.

### 0.3 Adapter self-tests
- **What**: `scripts/test_adapter.py` covering `detect_bucket`, `detect_mode`, `default_skills_for`, `slug_from_name`, the three-bucket presets, and `--backport-superset` round-trip.
- **Why**: the adapter is now load-bearing for Claude/Cursor/opencode parity; it has zero tests.
- **Estimate**: S.

### 0.4 `README.md` role count vs §5 of `AGENTS.md`
- **What**: root README still says "16 specialized roles" in the prose; the catalog has grown to 19 (17 SDLC + 2 web specialists + orchestrator). Reconcile counts across `README.md`, `docs/README.sdlc-system.md`, `docs/README.agents.md`, `AGENTS.md`.
- **Why**: stale counts erode trust.
- **Estimate**: S.

### 0.5 Standardize the `.sdlc/` layout across README / AGENTS.md / skill
- **What**: the root README's `.sdlc/` tree lacks `contracts/test-strategy.md` and `memory.md` parity; align on the skill's authoritative scaffold and re-render everywhere.
- **Estimate**: S.

### 0.6 `CONTRIBUTING.md`: reference the 5 rules and the adapter
- **What**: a "Cross-host contributions" subsection pointing at [`docs/integrations/compatibility.md`](integrations/compatibility.md) and instructing contributors to run the adapter after touching `tools:`.
- **Estimate**: S.

### 0.7 `CHANGELOG.md`
- **What**: introduce a Keep-a-Changelog-format file; one entry summarizing the recent cookbook + integration-guide + AGENTS.md work so future changes are trackable.
- **Estimate**: S.

---

## P1 — High-leverage gaps in the SDLC + web coverage

### 1.1 New agent — **Accessibility Specialist** (research)
- **What**: a dedicated `sdlc-accessibility-specialist.agent.md` that owns WCAG 2.2 AAA audits, AT compatibility, and remediation plans. Today only `sdlc-ux-ui-designer` and `sdlc-responsible-ai` touch this tangentially; the `web-accessibility-audit` skill has no dedicated escalation point.
- **Load**: `web-accessibility-audit`, `sdlc-shared-memory`.
- **Bucket**: research (writes `.sdlc/contracts/a11y-requirements.md`, remediation reports to `docs/a11y/`).
- **Estimate**: M.

### 1.2 New agent — **Code Reviewer** (review)
- **What**: `sdlc-code-reviewer.agent.md` — read-only review bucket that consumes `code-review-generic.instructions.md` (which exists today with no agent owner), checks PRs against `.sdlc/systemPatterns.md` + the relevant `instructions/*.instructions.md`, and emits structured findings to `.sdlc/decisions/review-*.md`. Replaces the generic "review my code" gap currently filled only by `electron-angular-native` (domain-specific) and the Copilot-style vendor review.
- **Bucket**: review (`permission: edit: deny`).
- **Estimate**: M.

### 1.3 New agent — **API Designer** (research, contract-first)
- **What**: `sdlc-api-designer.agent.md` owning OpenAPI/AsyncAPI specs, versioning (`vN` URL prefixing, deprecation headers), idempotency contracts, pagination strategy, error-code taxonomies. Splits the `sdlc-backend-engineer` "design contract" task into its own role so frontend can start before backend exists.
- **Output**: `.sdlc/contracts/api-contracts.md` (today the Backend Engineer writes it — split cleanly).
- **Estimate**: M.

### 1.4 New skill — **api-contract-first**
- **What**: patterns for OpenAPI 3.1 / AsyncAPI / JSON-Schema, deprecation policies, idempotency-key schemes, problem+json error catalogues, cursor pagination, version negociation. Supplements the existing `sdlc-backend-engineer` skill (1.3's matching skill).
- **Estimate**: M.

### 1.5 New skill — **observability-three-pillars**
- **What**: structured logs (OTLP/JSON), RED/USE metrics, distributed tracing, SLO/SLI/error-budget enforcement, RUM vs LAB. Today "observability" is sprinkled across backend + devops skills without a single home.
- **Estimate**: M.

### 1.6 New skill — **prompt-eval-and-regression**
- **What**: regression-test `.prompt.md` files with golden outputs, model-graded evals, scorer matrix, and CI integration. Closes the gap that `PromptFileAuthor` writes prompts but never validates them — the obvious missing half.
- **Estimate**: M.

### 1.7 New workflow — **`workflows/bug-triage.workflow.md`**
- **What**: Context Researcher → Cybersecurity Architect (if security bug) → Developer → QA → DevOps. Optimized for "a bug report came in" rather than greenfield.
- **Estimate**: S.

### 1.8 New workflow — **`workflows/docs-regen.workflow.md`**
- **What**: Technical Writer consumes `.sdlc/contracts/api-contracts.md` → regenerates reference + tutorials → RepositoryPathAuditor verifies technical-path freshness → Responsible AI reviews for plain language. Triggers from "release" or "contract changed".
- **Estimate**: S.

### 1.9 Slash-command library in `docs/opencode.json`
- **What**: today only `/sdlc-*` exist. Add `/review` (Code Reviewer), `/a11y` (Accessibility Specialist), `/explain` (Planning Agent, read-only), `/implement` (Developer), `/test` (QA), `/rfc` (Planning Agent → ADR), `/pr` (Technical Writer draft PR description from `.sdlc/contracts/`). Makes single-role use one keystroke.
- **Estimate**: S.

### 1.10 Templates directory
- **What**: `templates/` with `ADR.md`, `task.md`, `handoff.md`, `*.prompt.md`, `copilot-instructions.md`, `opencode.json` starter, `mcp.json` starters, and `.sdlc/` skeleton files. Contributors copy from these instead of improvising.
- **Estimate**: S.

### 1.11 `docs/recipes/` — "how to build a new agent / skill / instruction" runbooks
- **What**: three focused guides (`author-agent.md`, `author-skill.md`, `author-instruction.md`) with frontmatter templates, the superset rule, adapter call, and a copy-paste skeleton. Today the protocol lives inside `compatibility.md`; extracted runbooks are friendlier.
- **Estimate**: M.

---

## P2 — Ecosystem expansion (new roles, skills, languages)

### 2.1 New role cluster — **Platform & SRE**
- **sdlc-sre.agent.md** (implementation) — owns runbooks, on-call playbooks, incident command, SLO/error-budget breaches, postmortems. Modern complement to `sdlc-devops-engineer` (which is build-and-release, not run).
- **sdlc-finops-engineer.agent.md** (research) — cloud cost optimization, unit economics, rightsizing, commitment planning, idle-resource sweeps. Currently no role owns this.
- Matching skills: `sre-incident-command`, `finops-cloud-cost`.
- **Estimate**: L.

### 2.2 New role cluster — **Data & ML**
- **sdlc-data-engineer.agent.md** (implementation) — ETL/ELT, dbt models, warehouse schemas, pipeline idempotency, backfill, data contracts. Distinct from DB Architect (OLTP). Output: `.sdlc/contracts/data-contracts.md`.
- **sdlc-mlops-engineer.agent.md** (implementation) — model registry, feature stores, training/inference pipelines, drift detection, rollback of model versions.
- **sdlc-evaluation-engineer.agent.md** (research) — eval harness design, golden sets, model-graded scorers, bias audits (extends `sdlc-responsible-ai`).
- Matching skills: `data-pipeline-patterns`, `mlops-lifecycle`, `model-evaluation`.
- **Estimate**: L.

### 2.3 New role — **Localization Engineer**
- **What**: `sdlc-localization-engineer.agent.md` (implementation) — i18n message extraction, pluralization/ICU, RTL, locale fallback, translation memory. Hooks the existing `localization.instructions.md` (which has no agent owner today).
- **Estimate**: M.

### 2.4 New role — **Mobile Engineer** (cross-platform split)
- **What**: `sdlc-mobile-engineer.agent.md` (implementation, React Native / Flutter). Distinct from `expert-react-frontend-engineer` (web only). Loads the existing `dart-n-flutter.instructions.md`.
- **Estimate**: M.

### 2.5 New role — **API Documentation / OpenAPI Specialist**
- **What**: overlaps 1.3; if separated, the API Designer becomes contract-owner and this role becomes doc-emitter (的主角). Lower priority than 1.3.
- **Estimate**: M.

### 2.6 Instruction gaps (targeted additions)
- **What**: instructions for languages/frameworks the cookbook mentions or that are commonly requested but absent:
  - `swift.instructions.md` (iOS native — currently absent entirely; `swift-mcp-server` exists only)
  - `kotlin.instructions.md` (Android/JVM standalone — only `kotlin-mcp-server` exists)
  - `python-fastapi.instructions.md`, `python-django.instructions.md`, `python-flask.instructions.md`
  - `rust-web-axum.instructions.md` / `rust-web-actix.instructions.md`
  - `deno.instructions.md`, `bun.instructions.md`
  - `solid.instructions.md`, `remix.instructions.md`, `nuxt.instructions.md`, `htmx.instructions.md`
  - `terraform.instructions.md`, `pulumi.instructions.md`, `opentofu.instructions.md`
  - `postgres-tuning.instructions.md`, `mysql-tuning.instructions.md`
  - `openapi-3-1.instructions.md`, `asyncapi.instructions.md`
  - `otel-otelcol.instructions.md` (matches 1.5)
  - `git-conventional-commits.instructions.md`, `github-actions-workflows.instructions.md`
  - `sveltekit.instructions.md` (currently `svelte.instructions.md` covers the language but not the meta-framework end-to-end)
- **Why**: removes the case where a contributor fares "instructions for X" only via Google.
- **Estimate**: M (one day per few files).

### 2.7 Cookbook expansion — backend web frameworks
- **What**: `cookbook/web-dev/python/` (FastAPI streaming, async SQLAlchemy sessions, background tasks with `AnyIO`), `cookbook/web-dev/rust/` (axum SSE + backpressure, tower middleware), `cookbook/web-dev/deno/` (Hono on Deno Deploy edge), `cookbook/web-dev/bun/` (Bun.serve streaming). The current cookbook only has `nodejs` for backend; the repo preaches polyglot.
- **Estimate**: L (one weekend per framework, runnable example each).

### 2.8 Cookbook — vertical-slice recipes
- **What**: `cookbook/web-dev/vertical-slices/` — end-to-end recipes that compose Agent + Skill + Instruction (e.g. "build a paginated, accessible, contract-first user list" using Backend + Frontend + QA + DS Engineer). Demonstrates the SDLC team in miniature.
- **Estimate**: L.

### 2.9 New skill — **security-supply-chain** (SBOM & SLSA)
- **What**: SBOM generation (CycloneDX/Syft), SLSA levels, signed artifacts (Sigstore/cosign), provenance attestation, dependency pinning + renovate policy. Extends `sdlc-cybersecurity-developer`.
- **Estimate**: M.

### 2.10 New skill — **css-architecture**
- **What**: ITCSS / CUBE / BEM-tiered CSS layers, `@layer`, CSS modules vs CSS-in-JS trade-offs, container queries, cascade origins, cascade layers. Frontend skill covers accessibility/perf but not CSS structure at scale.
- **Estimate**: M.

### 2.11 New skill — **frontend-testing-library**
- **What**: patterns for RTL / Vitest / Playwright Component Testing / Storybook interactions + visual regression. Closes the gap that `sdlc-qa-tester` is generic; frontend testing deserves a skill.
- **Estimate**: M.

### 2.12 New skill — **technical-writing-diataxis**
- **What**: Validate doc trees against Diátaxis (tutorial/how-to/reference/explanation), docstring-driven reference, runnable examples, plain-language score (Hemingway/Flesch). Turns the existing `sdlc-technical-writer` "patterns" section into an enforceable checklist.
- **Estimate**: S.

---

## P3 — Polish & scale

### 3.1 Generator CLI — `npx create-vibecoder`
- **What**: a Node CLI that scaffolds a target project with `.sdlc/`, `AGENTS.md`, `docs/opencode.json` (trimmed to chosen roles), `.github/mcp.json` (chosen servers), and `.cursor/rules/` + `.claude/agents/` generated via the adapter. Removes the manual copy-paste step in the install guides.
- **Why**: the install guides are still ~7 steps each; a generator collapses them to one.
- **Estimate**: L.

### 3.2 Online catalog generator
- **What**: a script emitting `docs/catalog.json` (agents + skills + instructions + workflows + cooks) consumed by an Astro site (`website/`, which is already referenced in `.gitignore`). One-line "Add to your host" buttons per asset.
- **Estimate**: L.

### 3.3 `llms.txt` + `llms-full.txt`
- **What**: standard LLM index files at the repo root (already referenced in `.gitignore` as `/llms.txt`) listing every agent/skill/instruction/workflow with one-line descriptions, so an LLM tool can auto-discover the catalog. The `.gitignore` line implies intent; nothing emits them.
- **Estimate**: S.

### 3.4 Slash-command / agent matrix doc
- **What**: a generated `docs/matrix.md` cross-tabulating the 35 agents × 4 hosts × the 5 retro-compat rules; proves the matrix stays consistent and gives a one-glance audit page.
- **Estimate**: S.

### 3.5 Docs linter
- **What**: extend `validate-assets.py` (or a new `scripts/lint-docs.py`) to enforce markdown-heading conventions (every agent has the canonical 7 sections; every skill has `When to Use`, `Patterns, Rules & Standards`, `Indicators of Done`), broken-link check via `lychee`, no absolute `file:///` paths in `docs/`, no hardcoded machine paths anywhere.
- **Why**: the bug in 0.1 would not have shipped if such a linter existed.
- **Estimate**: M.

### 3.6 `.sdlc/` schema + CLI validators
- **What**: a JSON Schema for `.sdlc/*.md` front-matter-free envelopes (task status blocks, handoff headers, ADR sections) and a small `scripts/sdlc-validate.ts` that a project can run locally to verify the SDLC state at any time.
- **Estimate**: M.

### 3.7 Storybook for prompts
- **What**: pair `*.prompt.md` files with golden outputs + a runner that diffs new model versions against the goldens; surfaces regressions when models upgrade. Pairs with 1.6.
- **Estimate**: M.

### 3.8 Adopt Renovate / Dependabot for the cookbooks
- **What**: per-recipe `package.json` updates on a monthly cadence with grouped PRs; pins React 19 / Next 16 / Astro 5 / Svelte 5 / Vue 3 majors explicitly in the renovate config.
- **Estimate**: S.

### 3.9 MCP server catalog in `docs/integrations/`
- **What**: `mcp-catalog.md` enumerating recommended servers (Playwright, GitHub, Filesystem, Sequential-Thinking, Memory, Postgres, Slack, Sentry) with the suggested per-role grants (e.g. Frontend Engineer → playwright + browser; DevOps → github; QA → playwright + git). Today MCP wiring is scattered across 5 guides.
- **Estimate**: S.

### 3.10 Accessibility statement + repo-level a11y policy
- **What**: `ACCESSIBILITY.md` declaring conformance targets (WCAG 2.2 AA), test tooling, AT matrix, and pointer to the Accessibility Specialist role (1.1). Most serious OSS projects now ship one.
- **Estimate**: S.

### 3.11 `SECURITY.md`
- **What**: vulnerability reporting policy, supported versions, response SLAs, and an SBOM pointer (links to 2.9).
- **Estimate**: S.

### 3.12 Diagrams as code
- **What**: replace the `mermaid` block in `README.md` with a maintained `docs/diagrams/*.mmd` set rendered into PNG/SVG on CI; covers `.sdlc` flow, workflow phases, retro-compat pipeline. Easier to keep in sync than inline mermaid.
- **Estimate**: M.

### 3.13 Internationalization of core docs
- **What**: mirror `AGENTS.md`, `README.md`, and the 5 integration guides in at least ES and PT-BR (the repo author's locale signal suggests it). Pair with 2.3's Localization Engineer role as a dogfood.
- **Estimate**: L.

### 3.14 "Definition of Done" auto-validation
- **What**: an opencode plugin / Claude hook that on `SubagentStop` reads the agent's `Definition of Done`/`Indicators of Done` and asserts each row against `.sdlc/progress.md`. Closes the loop between the prose gate and the actual gate.
- **Estimate**: L.

### 3.15 Adapter: VS Code extension wrapper
- **What**: a tiny VS Code extension exposing "Adapt agent to host" as a command, so non-CLI contributors get a button.
- **Estimate**: M.

### 3.16 Performance regression cookbook
- **What**: `cookbook/web-dev/perf-regression/` — three recipes (LCP, INP, CLS) where a "before" repo state is provided and the Web Performance Engineer applies fixes with before/after numbers. Demonstrates 1.6's skill end-to-end.
- **Estimate**: M.

---

## Suggested sequencing

1. **P0 first** — ship the validator fix, CI, adapter tests, count reconciliations, CHANGELOG (one weekend). This hardens what's already shipped so the rest is built on solid ground.
2. **P1 next** — the Accessibility Specialist, Code Reviewer, API Designer + matching skills, plus the two new workflows and `/review`-style commands. This is the highest leverage for the SDLC story the repo tells.
3. **P2 selectively** — pick the role cluster (Platform & SRE or Data & ML) that best matches the contributing team's domain; add the language instructions requested most often; expand the cookbook one framework at a time.
4. **P3 opportunistically** — the generator CLI, `llms.txt`, docs linter, and auto DoD validation are the things that pay back over years but can wait.

---

## What I deliberately did **not** propose (and why)

- **More autonomous "Beast-style" agents** — the repo already has four (`Beast`, `CoderBeast`, `ExpertCoder`, `gpt-5-beast-mode`); adding more duplicates a working pattern.
- **A host-specific "Cursor rules engine" or "opencode plugin runtime"** — out of scope for an asset catalog; those belong in their host OS's downstream repos.
- **Replacing markdown with JSON/YAML for agents/skills** — markdown-with-frontmatter is the cross-host lowest common denominator (Rule 3 of the retro-compatibility contract); losing it would break every host.

---

## Open this doc

`docs/roadmap.md`.

If a maintainer wants, I can apply P0 (items 0.1–0.3) in one commit set this turn — they are all S-tier and lower the risk of everything that follows.