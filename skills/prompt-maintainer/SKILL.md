---
name: prompt-maintainer
description: Maintain and improve used GitHub Copilot *.prompt.md files after a run by comparing intended behavior vs implemented repo changes, then updating the same prompt file in place (tighten clarity/validation without changing intended functionality). Use when a prompt was already used and the user wants it improved for the next run. Composable with prompt-builder (create prompts), prompt-markdown-sanitizer (sanitize docs), and technical-overview-maintainer (update .github/Documentation/IMPLEMENTATION_PLAN.md). Can run before or after sibling skills. Supports MCP tool interface.
---

# Prompt Maintainer

Use this skill when a prompt has already been used to implement work and the user wants the original `*.prompt.md` improved so the next run is more correct, complete, and reliable.

This skill is the “post-run” counterpart to the `prompt-builder` skill:

- `prompt-builder`: create/refine prompts from requirements.
- `prompt-maintainer`: improve an already-used prompt based on observed repo outcomes.

## What This Skill Does

- Extract what the prompt intended (requirements, constraints, outputs)
- Infer what was actually implemented in the repo
- Diagnose prompt-level root causes for gaps (ambiguity, missing constraints, weak validation, poor tool guidance)
- Update the same prompt file to prevent repeat failures

## Core Invariants (Do Not Break)

- Preserve the prompt’s original intent and core behavior.
- Do not invent new features or expand scope.
- Do not implement/refactor product code unless the target prompt explicitly instructs it.
- Keep the prompt maintainable: structured sections, minimal redundancy, deterministic language.

## Repository Conventions (Match prompt-builder)

- **Canonical Storage**: All prompt files MUST be saved ONLY in `.github/prompts/` as the canonical source of truth.
- **Variable syntax**: Use `${...}` tokens consistently (e.g., `${selection}`, `${file}`, `${workspaceFolder}`, `${input:name}`).
- **Front matter**:
  - Always keep `agent` and `description`.
  - Keep `tools` minimal and aligned to what the prompt body actually instructs.
  - Keep `model` only if explicitly required.
  - Prefer stable key order: `agent`, `description`, `tools`, `model`.
- **No passengers**: Do not add tools/variables “just in case”.
- **Output determinism**: The prompt must explicitly state whether it edits files vs prints content, and what it outputs after edits.

## Required Input

- `${file}`: the prompt file to maintain.

Optional supporting inputs:

- Additional chat instructions that describe what to improve, fix, complement, or preserve.
- An inline `PROMPT:` block in chat. When present alongside `${file}`, treat text before the marker as maintenance directives and text after the marker as prompt-body content to expand/merge into the existing `PROMPT:` section by default.

If `${file}` is missing or ambiguous, stop and ask for it.

If the request contains only raw prompt text or only an inline `PROMPT:` block with no target file, this skill is not the entry point. Hand off to `prompt-builder` to create a canonical prompt file first.

If the user references a run/PR/branch, use it only as evidence; do not hard-require it.

## Output Contract

- Update `${file}` in place.
- Do not create new prompt files.
- Do not rename or move `${file}`.

After updating `${file}`, provide a short summary (2–8 bullets) of what changed and why.

## Workflow (Use These Steps)

### 1) Read & Inventory the Prompt

Read `${file}` fully. Build an internal inventory (do not output unless the user asks):

If the user also supplied an inline `PROMPT:` block, split on the first case-insensitive marker:

- Text before the marker = maintenance directives
- Text after the marker = prompt-body candidate to merge into and expand the existing `PROMPT:` section by default

- Purpose (one sentence)
- Invariants / must-not-change constraints
- Requirements (explicit + implied)
- Variables referenced: every `${...}` token (e.g., `${selection}`, `${workspaceFolder}`, `${input:...}`)
- Outputs: files to edit/create, formats, templates
- Quality gates: build/test/lint instructions and how specific they are

Also inventory (internal only):

- Whether the prompt’s `tools` list is **necessary and sufficient** for its instructions
- Whether its Inputs/Context section (if present) documents all `${...}` tokens

### 2) Inspect Implementation Signals (What Happened)

Use repo signals to infer what the prior run did and whether it matched intent:

- `changes`: what files were edited/created
- `problems`: errors/warnings introduced or remaining
- `testFailure` (if available): failures from the last test run
- `search/codebase` + `search`: locate the code paths/docs/configs the prompt should have affected

Answer for yourself:

- What is clearly implemented?
- What is missing or partial?
- What looks wrong or low quality (fragile patterns, inconsistent style, unclear naming, no tests)?

If `changes` is empty/inconclusive, rely on searching for the expected outputs implied by the prompt.

If there are no repo signals available (fresh context), maintain the prompt based on the prompt text alone, and explicitly note that validation steps are “best effort”.

### 3) Diagnose Prompt-Level Root Causes

Map the observed gaps back to prompt weaknesses, such as:

- Ambiguity ("should", "handle X") without acceptance criteria
- Missing constraints (scope creep, wrong files touched, style drift)
- Missing tool guidance (where to look, which files to edit, how to verify)
- Missing validation (no concrete commands, no Definition of Done)
- Missing edge cases/failure modes (empty inputs, conflicting instructions)

Prefer diagnosing issues that can be fixed purely by making the prompt more explicit:

- unclear inputs (missing `${file}`/`${selection}` assumptions)
- missing output contract (what files to edit, what to print)
- missing validation (what to run / how to confirm success)
- poor scoping language (causes scope creep)

### 4) Update `${file}` In Place (Prompt Only)

Edit only `${file}` to address the diagnosed weaknesses, while preserving original intent.

Make improvements only when they fit the original intent:

- Convert ambiguous requirements into explicit, testable instructions.
- Add constraints that prevent common failures (editing wrong files, scope creep).
- Strengthen validation steps using repo-specific commands when discoverable.
- Add edge cases/failure modes likely missed last run.
- Improve tool usage guidance (what to search for, what confirms success).
- Ensure YAML front matter matches repo conventions (`agent`, `description`, and `tools` only when used; `model` only if explicitly required).

When changing `tools` in front matter:

- Only add a tool if the prompt body explicitly instructs its usage.
- Only remove a tool if it is not used by the prompt body.

Editing rules:

- Keep existing variables and names unless clearly wrong.
- If a new variable is truly required, document it explicitly in an Inputs/Context section.
- Prefer checklists and MUST/SHOULD language.
- Keep it skimmable; avoid fluff.
- If an inline `PROMPT:` block was provided, update only the `PROMPT:` section unless the user explicitly asks for a broader rewrite.
- Default mixed-input behavior is expansion/merge, not replacement, unless the user explicitly requests replacement or a full rewrite.

If `${file}` lacks one of these sections, add it (when consistent with intent):

- **Context / Inputs**: list and define all `${...}` tokens
- **Output**: what gets edited/created vs printed
- **Validation**: concrete “done” checks, or how to discover the right commands

### 5) Definition of Done (For Maintenance)

Before finishing, confirm `${file}`:

- Still describes the same task and intent as before
- Has explicit Definition of Done with concrete checks
- Has clear inputs/outputs and unambiguous constraints
- Includes actionable validation steps (or instructions to discover the right commands)
- Does not instruct edits outside `${file}` unless explicitly required

Additionally confirm `${file}`:

- Uses `${...}` variables consistently and documents them
- Has a `tools` list that is necessary and sufficient

## Clarifying Questions Policy

Ask at most 3 questions, only if you cannot safely infer intent, success criteria, or the correct `${file}`.

When asking, propose defaults so the user can answer quickly.

Examples of acceptable questions:

- “Should validation run `runTasks` build/test, or just static checks (`problems`)? (Default: run build+tests if available.)”
- “Is this prompt supposed to edit files (`edit`/`agent`) or only output text (`ask`)? (Default: keep current `agent`.)”

## Example User Requests That Should Trigger This Skill

- “We used this `.prompt.md` and the result was off — update the prompt so it won’t miss X next time.”
- “Make this prompt more deterministic and add validation steps based on what changed.”
- “Post-run cleanup: tighten constraints and tool guidance in this prompt without changing intent.”

## Example Improvements This Skill Commonly Makes

- Add/repair a Context section to document `${file}`, `${selection}`, `${input:*}`
- Tighten “don’t change intent / don’t add features” constraints
- Replace vague verbs ("handle", "support") with explicit, testable requirements
- Add a concrete validation checklist using the repo’s build/test workflow when discoverable
## Skill Ecosystem — Composability

This skill is part of a composable skill pipeline. It can run independently or chain with sibling skills.

### Sibling Skills

| Skill | Relationship |
|---|---|
| **prompt-builder** | Creates prompts from scratch. Hand off to prompt-maintainer when an existing prompt needs post-run improvement instead of a full rewrite. |
| **prompt-markdown-sanitizer** | Sanitizes markdown for consistency. Run sanitizer after maintainer to catch structural issues, or before maintainer when the prompt has formatting problems that hinder analysis. |
| **technical-overview-maintainer** | Maintains `.github/Documentation/IMPLEMENTATION_PLAN.md`. Run after this skill when the prompt improvement triggers implementation changes that should be documented. |

### Chaining Patterns

| Pipeline | Use Case |
|---|---|
| **prompt-maintainer → prompt-markdown-sanitizer** | Improve the prompt logic, then sanitize for formatting and consistency. |
| **prompt-markdown-sanitizer → prompt-maintainer** | Fix structural issues first, then improve logic and validation. |
| **prompt-maintainer → technical-overview-maintainer** | Improve the prompt, then document the resulting implementation changes. |
| **technical-overview-maintainer → prompt-maintainer** | Document implementation first, then use the overview as evidence to improve the driving prompt. |

### MCP Integration

This skill exposes a composable interface for MCP tool servers:

```
Tool: prompt-maintainer
Inputs:
  - file: string           (path to the *.prompt.md to maintain)
  - evidence: string[]     (optional: paths to changed files, PR URLs, branch names)
  - mode: "analyze" | "fix" | "full"  (default: "full")
Outputs:
  - filePath: string       (path to the updated prompt file)
  - changesSummary: string[] (2–8 bullets of what changed and why)
  - suggestedNext: string[] (sibling skills to run next, if applicable)
```

When invoked via MCP:

- **analyze**: Run Steps 1–3 only (read, inspect, diagnose). Return diagnosis without editing.
- **fix**: Run Step 4 only (apply fixes). Assumes diagnosis is provided in input.
- **full** (default): Run all steps sequentially.

### Delegation Signals

- If the maintained prompt references `.github/Documentation/IMPLEMENTATION_PLAN.md`, suggest running **technical-overview-maintainer**.
- If the maintained prompt has structural/formatting issues beyond logic, suggest **prompt-markdown-sanitizer**.
- If the prompt is beyond repair and needs a full rewrite, suggest **prompt-builder** instead.

## Verification Check

Before finishing, confirm all of the following:

- `${file}` still represents the same prompt intent and scope as before the maintenance pass.
- Prompt file references use `.github/prompts/` as the canonical prompt location when a canonical path is stated.
- The maintained prompt has explicit inputs, outputs, validation, and deterministic tool guidance.
- No new prompt files were created, renamed, or moved.
- Any inline `PROMPT:` block provided with `${file}` was applied only as requested and did not silently rewrite unrelated instruction sections.