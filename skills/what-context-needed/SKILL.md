---
name: what-context-needed
description: 'Determine which codebase files and context are required to answer a user question before performing reasoning or implementation.'
---

# What Context Needed

Use this skill when a user asks a complex question about a codebase or requests a change, and you need to inspect files in the repository to provide an accurate answer. This skill helps avoid guessing by establishing a targeted list of files to read first.

## Trigger Conditions

Invoke this skill immediately when:
- The user asks about class definitions, functions, or configurations that are not present in the active document.
- The user's query references module interactions or architecture paths that have not yet been read.
- The task requires changes that span multiple files, and the dependency boundaries are not fully clear.

## Centralized State Architecture

On startup, verify the `.sdlc/` workspace state directory. Load the shared state baseline and record mapped paths inside `.sdlc/activeContext.md`.

1. Read `.sdlc/activeContext.md` and active task files under `.sdlc/tasks/` on startup to determine which files have already been mapped or modified by other roles.
2. Formulate the list of files required for the current task.
3. Write the proposed context path files directly to `.sdlc/activeContext.md` using the append-only pattern to establish a clear trace of investigated pathways.

## Core Capabilities

- **Dependency Scoping**: Analyze the user's question to identify which specific files, modules, or directories are likely to contain the answers or be affected by the changes.
- **Context Classification**: Group files into "Must See" (critical dependencies) and "Should See" (helpful context/references).
- **Redundancy Reduction**: Maintain a list of files already inspected in the active session to avoid redundant reading.
- **Uncertainty Mapping**: Call out specific architectural or operational details that cannot be resolved without code access.

## Inputs & Outputs

### Inputs
- `${input:question}`: The user's question or task description.
- Active document and search results (if any).

### Outputs
A structured request formatted as:
```markdown
## Context Discovery Plan

### Must See (critical files required for accurate response)
- `path/to/file.ts` — [specific explanation of why this file is required]

### Should See (files containing helpful patterns or config)
- `path/to/file.ts` — [explanation of how this file provides useful context]

### Already Inspected
- `path/to/file.ts` — [relevance from earlier in the session]

### Uncertainties
- [Key technical details or assumptions that require source code validation]
```

---

## Boundaries & Guardrails

- **Do NOT Guess**: If you are unsure where a component or function is defined, do not make assumptions. Explicitly request file access or use `search` / `codebase` tools to locate it first.
- **No Early Output**: Do not attempt to answer the user's question in the same turn that you request context. Declare that you are waiting for file access.
- **Declarative Requests**: State clearly what you are searching for and why, rather than asking the user's permission to search.

---

## Verification Checklist

Before emitting the context request, verify that:
- [ ] Every file in the "Must See" list has a direct, specific rationale tied to the user's question.
- [ ] No files listed in the "Must See" list are already open or fully read in the current conversation.
- [ ] The output follows the structured `Context Discovery Plan` layout verbatim.

