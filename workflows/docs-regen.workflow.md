# Documentation Regeneration Workflow

Regenerate the project's user-facing documentation from the source of truth: the API contract, the repository path map, and the responsible-AI review. This is a **pipeline-style** workflow — Technical Writer is the writer, RepositoryPathAuditor and Responsible AI are quality gates.

## When to Use

- The API contract in `.sdlc/contracts/api-contracts.md` has changed (new endpoint, deprecation, schema change).
- A new module, route, or public symbol has been added or renamed.
- A version cut / release is approaching and the docs need to be in sync.
- The Responsible AI review flagged a new bias, privacy, or accessibility concern that must be reflected in the docs.

Skip this workflow for purely internal refactors that don't change the public surface.

## Prerequisites

- `.sdlc/` workspace initialized.
- `.sdlc/contracts/api-contracts.md` is the **single source of truth** for API docs.
- `.sdlc/memory.md` and `.sdlc/architecture.md` are up to date.
- The Technical Writer agent has access to the project's existing doc tree (`README.md`, `docs/`, `reference/`, etc.).

## Role Sequence

> **Technical Writer ← `.sdlc/contracts/api-contracts.md` → RepositoryPathAuditor → Responsible AI**

| Step | Agent | Goal | Gate (must be true to advance) |
|---|---|---|---|
| 1 | **Technical Writer** | Regenerate / refresh the public docs from the API contract and the repository path map. | A diff is written under `docs/` showing the regenerated pages; references resolve; examples are runnable. |
| 2 | **RepositoryPathAuditor** | Audit the regenerated docs against the actual repository paths, routes, references, and companion-file links. | No broken internal links, no stale file references, no documented route that no longer exists. A "Path audit" report is appended to `.sdlc/progress.md`. |
| 3 | **Responsible AI** | Review the regenerated docs for bias, accessibility, privacy, and ethical guardrails. | A "Doc review" report is appended to `.sdlc/progress.md` listing concerns, or an explicit "no concerns" note. Issues are filed as tasks in `.sdlc/tasks/`. |

## Detailed Steps

### 1. Technical Writer — Regenerate Docs

- Read `.sdlc/contracts/api-contracts.md` — the single source of truth for every API surface, its data models, and its error codes.
- Read `.sdlc/architecture.md` and `.sdlc/memory.md` for context.
- Read the existing doc tree to understand the conventions, tone, and Diátaxis structure (tutorial / how-to / reference / explanation) in use.
- Regenerate the affected doc pages **in the project's source tree** — `editFiles` is the writer, not a narration tool. Pages include:
  - API reference (endpoint, params, request, response, errors, examples) for every changed endpoint.
  - Changelog entries for every contract change (cite the contract version).
  - Migration notes for every deprecation (link to the `Deprecation` / `Sunset` headers from the contract).
  - Updated tutorials / how-tos when the contract change breaks a code sample.
- Every code sample in the docs must be runnable. Use the [`sdlc-shared-memory`](../skills/sdlc-shared-memory/SKILL.md) protocol to record the diff in `.sdlc/progress.md` and to hand off to the RepositoryPathAuditor.

> **Definition of Done (step 1)**: the diff under `docs/` is complete; code samples have been syntax-checked or executed where feasible; the Technical Writer has appended a "Doc regeneration" section to `.sdlc/progress.md` with the list of changed files.

### 2. RepositoryPathAuditor — Path & Reference Audit

- Run the [`technical-path-indexer`](../skills/technical-path-indexer/SKILL.md) skill to scan the repository for paths, routes, references, and companion-file links.
- Cross-check every link and path referenced in the regenerated docs against the **actual** files, routes, and exported symbols in the source tree.
- Flag any of the following for fix:
  - **Broken internal links** — a `docs/` page references a file or anchor that doesn't exist.
  - **Stale file references** — a doc references a module, function, or route that has been renamed or removed.
  - **Documented-but-nonexistent routes** — the doc lists an endpoint, page, or feature that the code doesn't expose.
  - **Undocumented new routes** — the code exposes a new public surface that no doc page describes.
- **Output**: a "Path audit" report appended to `.sdlc/progress.md` with:
  - Pass/fail count.
  - A list of broken links and stale references (file:line where possible).
  - A list of undocumented public surfaces to be added.
- Hand off to Responsible AI for the next gate.

> **If the path audit fails, return to step 1** with the audit's issue list. The Technical Writer fixes the broken references and re-submits.

### 3. Responsible AI — Ethics, Bias, Privacy, Accessibility

- Read the regenerated docs and the API contract.
- Review for:
  - **Bias** — language that stereotypes, excludes, or misrepresents user groups.
  - **Accessibility** — alt text, color contrast references, plain-language summaries, keyboard-navigation notes, screen-reader-friendly examples.
  - **Privacy** — examples that leak real PII, secrets, or sensitive data; documentation of data-handling that glosses over consent or retention.
  - **Ethical guardrails** — claims about model or system behavior that overpromise, mislead, or omit failure modes.
- **Output**: a "Doc review" report appended to `.sdlc/progress.md` with:
  - A pass/fail verdict.
  - A list of concrete issues (file:line + suggestion).
  - An explicit "no concerns" note if everything is clean.
- For each issue, file a task in `.sdlc/tasks/` and hand back to the Technical Writer for the next pass.

> **Definition of Done (step 3)**: the doc review report is recorded; every issue is either resolved in the same regeneration pass or filed as a tracked task in `.sdlc/tasks/`.

## Definition of Done (workflow-level)

The documentation regeneration is considered complete when **all three** conditions hold:

1. The Technical Writer has regenerated the affected docs from the API contract; a diff is cited in `.sdlc/progress.md`.
2. The RepositoryPathAuditor has run a path audit with no broken links, no stale references, and no undocumented public surfaces — the audit report is recorded.
3. The Responsible AI review has either passed with a "no concerns" note or has filed tracked tasks for every issue raised.

## Customization

- **Insert a step between 1 and 2** for a Code Reviewer review of code samples in the docs, if the project policy requires it.
- **Insert a step between 2 and 3** for an Accessibility Specialist review, if the doc surface is user-facing and large.
- **Loop steps 1 → 2 → 3** as many times as needed; the workflow is idempotent and safe to re-run after each contract change.
- **Skip step 3** only if the project explicitly opts out of Responsible AI review for docs — not recommended.

## Related

- [`workflows/sdlc-sequential.workflow.md`](sdlc-sequential.workflow.md) — for full-feature delivery (not doc-only).
- [`agents/sdlc-technical-writer.agent.md`](../agents/sdlc-technical-writer.agent.md) — the writer in this pipeline.
- [`agents/RepositoryPathAuditor.agent.md`](../agents/RepositoryPathAuditor.agent.md) — the path-audit gate.
- [`agents/sdlc-responsible-ai.agent.md`](../agents/sdlc-responsible-ai.agent.md) — the ethics / bias / privacy gate.
- [`skills/technical-path-indexer/SKILL.md`](../skills/technical-path-indexer/SKILL.md) — the path-audit skill.
