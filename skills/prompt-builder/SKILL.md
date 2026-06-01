---
name: prompt-builder
description: Create production-ready GitHub Copilot .prompt.md files by running a structured discovery interview (purpose, persona, task, context variables, tools, output, validation) and then generating the complete prompt file content. Use when the user needs a new prompt file or wants a full rewrite of an existing one. Composable with prompt-maintainer (post-run improvement), prompt-markdown-sanitizer (sanitize output), and technical-overview-maintainer (document implementation changes). Supports MCP tool interface for pipeline integration.
---

# Prompt Builder

Use this skill when a user wants to create or refine a GitHub Copilot prompt file (`*.prompt.md`) and needs it to be clear, tool-aligned, and production-ready.

## Workflow Decision Tree

1. Determine intent:

  - **Inline `PROMPT:` block without a file** → Split on the first case-insensitive `PROMPT:` marker. Treat text before it as builder directives and text after it as the supplied prompt body. Create a new canonical prompt file in `.github/prompts/`.
   - **New prompt** → Run the discovery interview (sections below), then generate the full file.
  - **Existing file + inline `PROMPT:` block** → Read the existing prompt, treat text before the marker as change directives, and treat text after the marker as prompt-body content to expand/merge into the existing `PROMPT:` section by default.
   - **Update existing prompt** → Read the existing prompt, identify gaps (tools, variables, structure), ask only the missing questions, then output an updated full file.

2. If the user already has partial answers, skip covered sections.

## Repository Conventions (Follow These)

- **Canonical Storage**: All prompt files MUST be saved ONLY in `.github/prompts/` as the canonical source of truth.
- **Default prompt path**: When creating a new user prompt file, save it in `.github/prompts/` unless the user explicitly requests a different existing prompt file.
- **Canonical filename derivation**: When the user does not provide a filename, derive a short, clear kebab-case filename from the prompt purpose (for example, `review-sql-indexes.prompt.md`).
- **Variable syntax**: Use `${...}` tokens (e.g., `${selection}`, `${file}`, `${workspaceFolder}`, `${input:name}`) consistently.
- **Front matter**:
   - Always include `description` and `agent`.
   - Include `tools` only when the body actually instructs using them.
   - Include `model` only when explicitly required.
   - Keep YAML valid; prefer stable key order: `agent`, `description`, `tools`, `model`.
- **Tools naming**: Prefer the repo’s existing conventions (e.g., `search/codebase`, `search`, `edit/editFiles`, `problems`, `changes`, `testFailure`, `runTasks`).
- **Output determinism**: The prompt must clearly state whether the assistant should **edit files** vs **only output text**, and what to say after edits.

## Discovery Interview (Ask In Batches)

Keep questions tight: ask the minimum needed, usually 3–6 questions per round.

If the user already supplied an inline `PROMPT:` block, infer the task body from the text after the marker and treat any text before the marker as prompt-generation directives. Ask only for material gaps such as filename, agent mode, or missing validation requirements.

### A) Identity & Purpose

- Intended filename (e.g., `generate-react-component.prompt.md`)
- One-sentence `description` (what it accomplishes)
- Category (generation, analysis, refactor, docs, testing, architecture)

### B) Persona

- What role Copilot should embody (seniority + domain)
- Stack / technologies the prompt should assume
- Hard constraints (security/compliance/style guides)

### C) Task Spec

- Primary task (measurable)
- Secondary/optional tasks (if any)
- Expected user inputs (selection, file, parameters)
- Must-follow do/don’t constraints

### D) Context Variables

Decide which variables are needed and why:

- `${selection}`
- `${file}`
- `${workspaceFolder}`
- `${input:...}` variables

Also decide whether the prompt must inspect other files in the workspace.

### E) Tools

Select only tools required by the steps (no passengers). Typical buckets:

- File ops: `search`, `search/codebase`, `edit/editFiles`
- Diagnostics: `problems`, `changes`, `testFailure`, `todos`
- Execution: `runCommands`, `runTasks`, `runTests`
- External: `web/fetch`, `githubRepo`, `openSimpleBrowser`

### F) Output + Validation

- Exact output format (what the assistant must print)
- Whether it should create new files or modify existing ones
- Validation criteria (“done” checks; common failure modes to guard against)

## Generation Rules

- Prefer explicit requirements over generic advice.
- Keep structure stable: a reader should be able to follow it without interpretation.
- If something materially affects the output, ask 1–3 clarifying questions (don’t guess).
- Don’t include tools that aren’t referenced in the instructions.
- Do not introduce new scope/behavior beyond what the user requested; tighten wording, constraints, and validation instead.
- Ensure every `${...}` token used in the body is explained in a Context/Inputs section.
- When the request contains an inline `PROMPT:` block, preserve the split: pre-marker text becomes model-facing instructions or change directives, and post-marker text becomes the prompt body candidate.
- When an existing prompt file is also provided, default to expanding/merging the existing `PROMPT:` section with the new prompt-body content unless the user explicitly asks for replacement or a full rewrite.

## Output Template (Strict)

Generate the final deliverable as a complete `*.prompt.md` file content:

```markdown
---
description: "[Clear, concise description]"
agent: "[agent|ask|edit]"
tools: ["[tool-1]", "[tool-2]"]
model: "[optional - only if explicitly required]"
---

# [Prompt Title]

[Persona definition - specific role and expertise]

## Task

[Clear task description with measurable requirements]

## Instructions

[Step-by-step instructions]

## Context / Inputs

[Variables used and what the user must provide]

## Output

[Exact output format and structure]

## Validation

[Checks to run; what “done” means]
```

## Examples That Should Trigger This Skill

- “Make me a `.prompt.md` that reviews SQL and suggests indexes.”
- “Turn this checklist into a Copilot prompt with tools + output format.”
- “Here’s my prompt file — fix the tools list and make the instructions measurable.”

## Final Check Before Delivering

- `description` matches the actual behavior.
- `agent` mode matches the intended autonomy.
- `tools` list is necessary and sufficient.
- Variables used in the body are declared/obvious.
- Output section tells Copilot exactly what to produce.

## If Asked To “Implement” A Prompt

Treat “implement” as: rewrite the `*.prompt.md` file to be production-ready while preserving intent.

- Add missing sections (Inputs/Context, Output, Validation) when absent.
- Convert vague language into MUST/SHOULD constraints.
- Keep edits minimal and avoid adding unrelated features.

## Skill Ecosystem — Composability

This skill is part of a composable skill pipeline. It can run independently or chain with sibling skills.

### Sibling Skills

| Skill | Relationship |
|---|---|
| **prompt-maintainer** | Improves existing prompts post-run. Hand off to prompt-builder only when a prompt needs a full rewrite rather than incremental improvement. |
| **prompt-markdown-sanitizer** | Sanitizes markdown for consistency. Run after prompt-builder to catch structural issues in newly generated prompts. |
| **technical-overview-maintainer** | Maintains `.github/Documents/IMPLEMENTATION_PLAN.md`. Run after prompt-builder when the newly created prompt triggers implementation work that should be documented. |

### Chaining Patterns

| Pipeline | Use Case |
|---|---|
| **prompt-builder → prompt-markdown-sanitizer** | Generate a new prompt, then sanitize for formatting, variable consistency, and tool alignment. |
| **prompt-builder → prompt-maintainer** | Generate a prompt, use it in a run, then hand off to maintainer for post-run refinement. |
| **prompt-builder → technical-overview-maintainer** | Generate a prompt that drives implementation, then document the changes. |
| **prompt-maintainer → prompt-builder** | When maintainer determines a prompt is beyond incremental repair, escalate to builder for a full rewrite. |

### MCP Integration

This skill exposes a composable interface for MCP tool servers:

```
Tool: prompt-builder
Inputs:
  - purpose: string        (one sentence: what the prompt accomplishes)
  - persona: string        (optional: role Copilot should embody)
  - stack: string[]        (optional: technologies the prompt should assume)
  - tools: string[]        (optional: tools the prompt should use)
  - mode: "interview" | "generate" | "full"  (default: "full")
Outputs:
  - filePath: string       (path to the generated *.prompt.md)
  - content: string        (full prompt file content)
  - suggestedNext: string[] (sibling skills to run next, if applicable)
```

When invoked via MCP:

- **interview**: Run the discovery interview only. Return structured answers.
- **generate**: Skip interview; generate from provided inputs directly.
- **full** (default): Interview then generate.

### Delegation Signals

- After generating a prompt, suggest **prompt-markdown-sanitizer** for a consistency pass.
- If the generated prompt drives implementation, suggest **technical-overview-maintainer** to document changes.
- If the user later reports the prompt underperformed, suggest **prompt-maintainer** for post-run refinement.

## Verification Check

Before finishing, confirm all of the following:

- The generated or rewritten prompt preserves the user's requested scope and intent.
- Any new prompt file path is canonical under `.github/prompts/`, unless the user explicitly targeted a different existing prompt.
- Every `${...}` token used in the prompt body is documented in a Context / Inputs section.
- The output contract and Definition of Done are explicit and deterministic.
- Inline `PROMPT:` input, when provided, was parsed so that text before the marker is not merged into the prompt body.
