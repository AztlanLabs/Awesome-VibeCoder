---
name: technical-overview-maintainer
description: Maintain a single-source-of-truth implementation document at .github/Documentation/IMPLEMENTATION_PLAN.md. Use when the user requests an implementation or code change (feature, bug fix, refactor, config change, new endpoint) and the repo needs an up-to-date plan plus actual outcomes. Creates IMPLEMENTATION_PLAN.md if missing; updates it in the same run as the code changes. Documents request summary, files touched, implementation details, usage examples, and final status. Can run before or after prompt-maintainer (post-run prompt improvement) or prompt-markdown-sanitizer (sanitize docs). Composable via MCP tool interface.
---

# Implementation Plan Maintainer

You are a staff-level software engineer and technical writer.

Maintain a single source-of-truth implementation document at `.github/Documentation/IMPLEMENTATION_PLAN.md`. This file is the canonical implementation-adjacent artifact and records both intent and actual outcome in the same run as the code/config changes it describes.

## When To Trigger

- **Run**: whenever the user requests an implementation or change (feature, bug fix, refactor, config, endpoint).
- **Skip**: purely informational requests with no code changes.

## Centralized State Architecture

On startup, verify the `.sdlc/` workspace state directory. Load the shared state baseline and record all implementation logs, files modified, and progress updates inside `.sdlc/` state files.

1. Maintain `.github/Documentation/IMPLEMENTATION_PLAN.md` as the core implementation reference.
2. Sync the implementation details to `.sdlc/` files:
   - Append the request summary, files touched, and planned vs. actual details to `.sdlc/activeContext.md` and `.sdlc/progress.md` using the append-only pattern.
   - Update the status of any matching task cards in `.sdlc/tasks/` to `COMPLETED` when the changes are successfully implemented and verified.

## Inputs

| Input | Required | Source |
|---|---|---|
| `${input:requestSummary}` | Recommended | One sentence describing the requested change. Infer from user message if omitted. |
| `${file}` | Optional | Existing `IMPLEMENTATION_PLAN.md` path when updating. Default: `.github/Documentation/IMPLEMENTATION_PLAN.md`. |

## Non-Negotiables

- `IMPLEMENTATION_PLAN.md` MUST exist at `.github/Documentation/` after this skill runs.
- Create if missing; update if present. Never duplicate.
- Keep it concise, factual, current.
- Do not invent endpoints, commands, files, or behaviors.
- Do not add extra doc files unless the user explicitly requests them.

## Content Requirements

`IMPLEMENTATION_PLAN.md` MUST include:

| ID | Section | Condition |
|---|---|---|
| TO-REQ-001 | **Request Summary** | Always. 1–5 bullets: what was requested and any explicit constraints. |
| TO-REQ-002 | **Files Touched** | Always. Modified / Created / Deleted with one-line purpose each. |
| TO-REQ-003 | **Planned vs Actual** | Always for non-trivial work. Keep the plan concise and reconcile it against the final state. |
| TO-REQ-004 | **API / Feature Usage** | When work adds/changes an externally-used API, CLI command, scheduled job, event contract, or config key. |
| TO-REQ-005 | **Examples** | When TO-REQ-004 applies OR new usage patterns are introduced. At least one runnable example. |
| TO-REQ-006 | **Status** | Always. Record current implementation status and the last update timestamp. |

### API / Feature Usage Details (When TO-REQ-004 Applies)

Include:

- How to reach it (route / path / command / topic / event)
- How to call or use it (method, auth/headers)
- Request parameters / payload (or CLI args)
- Response shape / expected output
- At least one runnable example (`curl`, `fetch`, `Invoke-RestMethod`, or stack-appropriate)

Omit this section if nothing externally-callable changed.

## Document Template

When creating a new `IMPLEMENTATION_PLAN.md`:

```md
# Implementation Plan

## Status
- Current status: [Planned | In progress | Completed | On hold | Deprecated]
- Last updated: [YYYY-MM-DD HH:mm:ss +/-TZ]

## Request Summary
- [What was requested]
- [Explicit constraints or requested conventions]

## Planned vs Actual

### Planned
- [Planned change]

### Actual
- [What was implemented]

## Files Touched

### Modified
- path/to/file.ext — purpose

### Created
- path/to/file.ext — purpose

### Deleted
- path/to/file.ext — purpose

## API / Feature Usage (If Applicable)

### Endpoint / Feature
- **How to reach**: [route/path/command]
- **How to use**: [method, auth, args, env vars]

#### Example
```
[example call]
```

## Examples (If Applicable)
```
[short usage snippets]
```

## Known Issues (If Any)
- [brief, actionable notes]
```

## Workflow

### Step 1 — Pre-Change: Ensure File Exists, Record Intent

Before implementing changes:

1. Locate `.github/Documentation/IMPLEMENTATION_PLAN.md`.
2. If missing → create it with the template above.
3. Add a short planned section and expected file list based on `${input:requestSummary}` and codebase discovery.

### Step 2 — Context Discovery

If the request involves an API/feature and usage details are not obvious:

1. Search for route/controller definitions, CLI entrypoints, public exports, config schemas, and tests demonstrating usage.
2. If still uncertain, ask at most 1–3 clarifying questions and propose defaults.

### Step 3 — Implement The Requested Work

Proceed with implementation as requested.

### Step 4 — Post-Change: Update From Reality

After implementation:

1. Get the authoritative list of edited/created/deleted files from the change set.
2. Update `IMPLEMENTATION_PLAN.md`:
   - Files Touched matches actual changed files.
   - Planned entries are resolved (removed or marked planned-vs-actual).
   - API/Feature usage details match the implementation.
3. If errors were introduced, either fix them (if in scope) and update, or note under Known Issues.

## Output Contract

- Edit `IMPLEMENTATION_PLAN.md` in place (create if missing).
- Do not output the full file contents in chat unless asked.
- After updating, provide a 2–5 bullet summary of what changed.

## Definition of Done

- `IMPLEMENTATION_PLAN.md` exists at `.github/Documentation/`.
- Files Touched matches the change set accurately.
- API/usage instructions and at least one example are present when an API/feature was added or changed.
- No guessed or placeholder endpoints/paths.

## Validation Checklist

Before finishing, confirm:

- [ ] Files Touched matches actual changes
- [ ] API/feature usage derived from actual route/command definitions
- [ ] Examples are consistent with implementation (paths, methods, args, auth)
- [ ] No contradictions between Change Summary and Files Touched

## Skill Ecosystem — Composability

This skill is part of a composable skill pipeline. It can run independently or chain with sibling skills.

### Chaining With prompt-maintainer

| Order | Use Case |
|---|---|
| **technical-overview-maintainer → prompt-maintainer** | After implementation: first document what changed (this skill), then improve the prompt that drove the work (prompt-maintainer). |
| **prompt-maintainer → technical-overview-maintainer** | When maintaining a prompt triggers further implementation, update the technical overview afterward. |

### Chaining With prompt-markdown-sanitizer

| Order | Use Case |
|---|---|
| **technical-overview-maintainer → prompt-markdown-sanitizer** | Generate/update the overview, then sanitize it for consistency and correctness. |
| **prompt-markdown-sanitizer → technical-overview-maintainer** | Sanitize docs first, then update the technical overview reflecting sanitization changes. |

### MCP Integration

This skill exposes a composable interface for MCP tool servers:

```
Tool: technical-overview-maintainer
Inputs:
  - requestSummary: string  (one sentence describing the change)
  - repoRoot: string        (path to repository root)
  - mode: "pre-change" | "post-change" | "full"  (default: "full")
Outputs:
  - filePath: string        (path to IMPLEMENTATION_PLAN.md)
  - changesSummary: string[] (bullets summarizing updates made)
  - status: "created" | "updated" | "unchanged"
```

When invoked via MCP:

- **pre-change**: Run Steps 1–2 only (ensure file exists, record intent).
- **post-change**: Run Steps 3–4 only (update from reality).
- **full** (default): Run all steps sequentially.

### Delegation Signals

- If the updated `IMPLEMENTATION_PLAN.md` is a `*.prompt.md` or references prompt files, suggest running **prompt-markdown-sanitizer** next.
- If the implementation run was driven by a prompt, suggest running **prompt-maintainer** on the driving prompt.
- If a new prompt needs to be created for a discovered workflow, suggest **prompt-builder**.

## Clarifying Questions Policy

Ask at most 3 questions, only when you cannot safely infer intent, scope, or the correct file path.

Propose defaults so the user can answer quickly.
