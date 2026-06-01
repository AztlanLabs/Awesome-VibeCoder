---
name: context-map
description: 'Generate a map of all files relevant to a task before making changes'
---

# Context Map

Use this skill to systematically identify and map all codebase dependencies, files, tests, and reference patterns related to a target task before any modifications begin.

## Trigger Conditions

Invoke this skill when:
- Preparing to make non-trivial, multi-file code modifications.
- Assessing ripple effects, import/export dependency chains, or potential API contract breakages.
- Discovering existing codebase patterns to mirror for consistency.

## Centralized State Architecture

On startup, verify the `.sdlc/` workspace state directory. Load the shared state baseline and record all generated context maps directly inside `.sdlc/activeContext.md`.

1. Read `.sdlc/activeContext.md` on startup to align with the current development focus.
2. Append the generated Context Map to the end of `.sdlc/activeContext.md` using the append-only pattern.
3. If this mapping belongs to a specific task, log the file mappings in the corresponding `.sdlc/tasks/TASK-*.md` file.

## Core Capabilities

- **Codebase Dependency Mapping**: Scan and locate all files that will be directly edited or indirectly impacted.
- **Reference Pattern Identification**: Identify nearby or similar implementations to follow for stylistic and architectural consistency.
- **Test Context Discovery**: Locate all related tests and validation suites that cover the target codebase files.
- **Risk Assessment**: Classify risk factors like public API changes, database migrations, or config shifts.

## Inputs & Outputs

### Inputs
- `${input:taskDescription}`: A detailed explanation of the task or change to be performed.

### Outputs
A structured markdown Context Map containing:
1. **Files to Modify**: Table of target files, their purpose, and specific changes needed.
2. **Dependencies**: Table of downstream or upstream files impacted by imports, exports, or types.
3. **Test Files**: Table of associated test cases and suites to run.
4. **Reference Patterns**: Similar codebase implementations to follow as style guides.
5. **Risk Assessment**: Clear checklists for public API, DB migrations, or configuration risks.

---

## Boundaries & Guardrails

- **No Premature Coding**: This skill is strictly for mapping and planning. Do not write or execute product implementation code during this step.
- **Accurate Paths**: Only list file paths that exist in the workspace or are explicitly scheduled for creation.
- **Minimal Touch**: Gather only the context necessary for the task at hand; do not widen scope to unrelated subsystems.

---

## Verification Checklist

Before finalizing the context map, verify that:
- [ ] Every file scheduled for direct modification is documented with its purpose.
- [ ] Dependency tracing is done for all modified files' public interfaces.
- [ ] At least one relevant test file or validation script is mapped for testing.
- [ ] The risk checklist has been explicitly evaluated.
