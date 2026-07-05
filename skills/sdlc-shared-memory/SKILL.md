---
name: sdlc-shared-memory
description: 'Initialize, read, write, and maintain the .sdlc/ shared knowledge directory. Provides always-on centralized state management, automatic scaffolding, handoff management, task lifecycle, decision records, and contract protocols.'
---

# SDLC Shared Memory

## Always-On Centralized State Architecture

This skill is the core state management engine for all agentic workflows. All agents and skills are required to load and interact with this skill to maintain a single, version-controlled project baseline.

On startup, every agent and skill performs these actions:
1. Check for the presence of the `.sdlc/` directory at the project root.
2. If the `.sdlc/` directory is missing, automatically initialize it by creating the standard file structure and templates.
3. Load the project brief, active context, progress registry, and decision logs from `.sdlc/` to establish the execution baseline.
4. Write all generated specifications, requirements, ADRs, designs, audits, and research reports directly to their designated locations within the `.sdlc/` folder. Source code, tests, and infrastructure/pipeline files are never written here — they belong in the project's real source tree, and only their paths + verification results are recorded in `.sdlc/`.
5. In addition to role-specific files, append a short pointer entry to the centralized project chronicle in `.sdlc/memory.md`: the real artifact paths changed and, for any executable work, the exact build/test/validation command run and its result. Memory is a **side effect** of verified work, not the deliverable itself — do not treat writing to `memory.md` as equivalent to completing the task.

## Initialization

Any SDLC agent can scaffold the `.sdlc/` directory on user request.

### Scaffold Command

When a user says "initialize sdlc workspace", "create sdlc state", or equivalent:

1. Create the `.sdlc/` directory at the project root.
2. Create these files with starter templates:

```text
.sdlc/
├── projectbrief.md
├── architecture.md
├── techContext.md
├── activeContext.md
├── progress.md
├── systemPatterns.md
├── tasks/
│   └── _index.md
├── decisions/
│   └── _index.md
├── contracts/
│   ├── api-contracts.md
│   ├── db-schema.md
│   ├── security-requirements.md
│   └── test-strategy.md
├── handoffs/
│   └── _index.md
└── memory.md
```

3. Populate `projectbrief.md` with information from the user's request.
4. Report: "SDLC workspace initialized at `.sdlc/`. All agents will now operate in team mode."

### File Templates

#### projectbrief.md

```markdown
# Project Brief

## Project Name
[Name]

## Goals
- [Primary goal]

## Scope
- **In Scope**: [What to build]
- **Out of Scope**: [What to exclude]

## Constraints
- [Technical, timeline, budget constraints]

## Success Criteria
- [Measurable criteria]
```

#### tasks/_index.md

```markdown
# Tasks Index

## In Progress

## Pending

## Completed

## Abandoned
```

#### decisions/_index.md

```markdown
# Decision Log

| ID | Title | Status | Date | Decided By |
|---|---|---|---|---|
```

#### handoffs/_index.md

```markdown
# Handoff Log

| ID | From | To | Status | Created |
|---|---|---|---|---|
```

## Read Protocol

When entering team mode, read files in this order:

1. `projectbrief.md` — understand project scope and goals
2. `activeContext.md` — understand current focus and recent decisions
3. `progress.md` — understand what is done and what remains
4. `architecture.md` — understand system structure (if your role needs it)
5. `systemPatterns.md` — understand coding conventions (if your role needs it)
6. `techContext.md` — understand tech stack (if your role needs it)
7. `tasks/_index.md` — check for assigned tasks
8. `handoffs/_index.md` — check for pending handoffs addressed to your role
9. Role-relevant `contracts/*.md` — read contracts your role consumes

Do not read every file. Read only what your role requires. The first three files are mandatory for all roles.

## Write Protocol

### Ownership Rules

Each `.sdlc/` file has a primary writer. In team mode, respect these boundaries:

| File | Primary Writer | Rule |
|---|---|---|
| `projectbrief.md` | Orchestrator or initializing agent | Write once, update rarely |
| `architecture.md` | Software Architect | Only architect roles write |
| `techContext.md` | Full Stack / DevOps | Implementation roles may append |
| `activeContext.md` | Any agent | Append-only, never delete prior entries |
| `progress.md` | Any agent | Append-only, never delete prior entries |
| `systemPatterns.md` | Software Architect | Only architect roles write |
| `tasks/*` | Creating agent creates; assigned agent updates | Update only your own tasks |
| `decisions/*` | Architect roles | Create with sequential ADR numbering |
| `contracts/*` | Designated owner role | Update only your own contract |
| `handoffs/*` | Producing agent creates; consuming agent acknowledges | Two-party write pattern |
| `memory.md` | Any agent | Append-only |

### Append-Only Pattern

For `activeContext.md`, `progress.md`, and `memory.md`:

```markdown
### [ISO-8601 Timestamp] — [Agent Role]
[Content]
```

Never edit or delete prior entries. Always append at the end.

For roles that write executable artifacts (code, tests, IaC, pipelines), `[Content]` must include the real file paths changed and the exact verification command + result, for example:

```markdown
### 2026-06-30T10:00:00Z — SDLC Developer
Files: src/orders/order-service.ts, src/orders/order-service.test.ts
Verification: `npm test -- order-service` — 12 passed, 0 failed
```

A prose description with no file paths and no command/result is not a valid entry for executable work.

### Single-Agent Execution Pattern

When running in sequential execution (one agent active at a time), the active agent has read/write authority to update task statuses and progress in `.sdlc/` files relevant to its task, but must respect the standard append-only structure.

## Task Lifecycle

### Task States

```
PENDING → IN_PROGRESS → COMPLETED
                      → BLOCKED → IN_PROGRESS
                      → ABANDONED
```

### Creating a Task

1. Generate next sequential ID: `TASK-NNN`.
2. Create `tasks/TASK-NNN-[short-name].md`:

```markdown
# TASK-NNN — [Task Name]

**Status**: PENDING
**Assigned To**: [role name or "unassigned"]
**Created**: [ISO-8601]
**Updated**: [ISO-8601]

## Description
[What needs to be done]

## Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]

## Dependencies
- [TASK-NNN or "none"]

## Progress Log
```

3. Add entry to `tasks/_index.md` under the appropriate status section.

### Claiming a Task

1. Read `tasks/_index.md` for tasks matching your role.
2. Open the task file. Verify status is `PENDING` and dependencies are met.
3. Update status to `IN_PROGRESS`. Set `Assigned To` to your role name. Update timestamp.
4. Move the entry in `_index.md` from Pending to In Progress.

### Completing a Task

1. Verify all acceptance criteria are met.
2. Update status to `COMPLETED`. Update timestamp.
3. Add a final progress log entry summarizing what was delivered.
4. Move the entry in `_index.md` from In Progress to Completed.
5. If downstream roles depend on this work, create a handoff.

## Handoff Protocol

### Creating a Handoff

1. Generate next sequential ID: `HO-NNN`.
2. Create `handoffs/HO-NNN-[short-name].md`:

```markdown
# HO-NNN — [Deliverable Description]

**From**: [your role]
**To**: [target role]
**Status**: PENDING
**Created**: [ISO-8601]

## Deliverables
- [File or artifact 1]
- [File or artifact 2]

## Dependencies Met
- [x] [Prerequisite 1]

## Notes for Recipient
- [Key information the next role needs]
```

3. Add entry to `handoffs/_index.md`.

### Acknowledging a Handoff

1. Read handoffs addressed to your role with status `PENDING`.
2. Update status to `ACKNOWLEDGED`.
3. After completing work based on the handoff, update status to `COMPLETED`.

## Decision Records

### Creating an ADR

1. Generate next sequential ID: `ADR-NNN`.
2. Create `decisions/ADR-NNN-[short-title].md`:

```markdown
# ADR-NNN — [Decision Title]

**Status**: Proposed | Accepted | Deprecated | Superseded
**Date**: [ISO-8601]
**Decided By**: [role]

## Context
[What forces are at play]

## Decision
[What we decided]

## Consequences
- **Positive**: [Benefits]
- **Negative**: [Trade-offs]

## Alternatives Considered
- [Alternative 1 and why rejected]
```

3. Add entry to `decisions/_index.md`.

## Contract Updates

Contracts are shared agreements between roles. Each contract file has a designated owner:

| Contract | Owner | Consumers |
|---|---|---|
| `api-contracts.md` | Backend Engineer | Frontend, Full Stack, QA |
| `db-schema.md` | DB Architect | DB Developer, Backend |
| `security-requirements.md` | Cybersecurity Architect | All roles |
| `test-strategy.md` | QA Tester | All roles |

When updating a contract:

1. Add a changelog entry at the top with timestamp and summary.
2. Update the contract content.
3. Create a handoff to notify consuming roles of the change.

## Patterns, Rules & Standards

### State File Conventions
- **One purpose per file**: `projectbrief.md` (scope), `architecture.md` (structure), `systemPatterns.md` (conventions + budgets), `techContext.md` (stack), `activeContext.md` (current focus), `progress.md` (verified work), `memory.md` (chronicle) — never duplicate concerns across files.
- **Structured entries**: append-only entries are timestamped and role-attributed (`### [ISO-8601] — [Agent Role]`); executable-work entries carry real file paths + a command/result, not prose.
- **IDs are sequential and unique**: `TASK-NNN`, `HO-NNN`, `ADR-NNN` advance by one; collisions are resolved before writing.
- **Closed shapes**: tasks carry status, assignee, acceptance criteria, dependencies, and a progress log; handoffs carry from/to, deliverables, dependencies-met, and notes; ADRs carry Context/Decision/Consequences/Alternatives.

### Concurrency & Ownership Rules
- **Primary writer per file**: respect the ownership table — `architecture.md`/`systemPatterns.md` only by architect roles, `contracts/*` only by the designated owner role, `decisions/*` only by architect roles.
- **Single-agent write authority**: in sequential execution the active agent owns its task's status/progress writes; other roles propose changes via ADRs or handoffs, never direct edits.
- **Cross-role edits require an ADR**: editing another role's primary file without a recorded ADR or task is forbidden.
- **No destructive edits** to `activeContext.md`, `progress.md`, or `memory.md` — append only; corrections are appended, not back-patched.

### Handoff Rules
- **Two-party write pattern**: the producing agent creates the handoff `PENDING`; the consuming agent sets `ACKNOWLEDGED`, then `COMPLETED` after the work lands.
- **Deliverables are file paths**: a handoff lists concrete artifact paths plus the verification command/result, not a narrative.
- **Downstream notification on contract change**: every `contracts/*.md` edit emits a timestamped changelog entry and a handoff to each consuming role.

### Integrity Rules
- **_index consistency**: `tasks/_index.md`, `handoffs/_index.md`, and `decisions/_index.md` match the individual file statuses at all times.
- **Verification before `COMPLETED`**: a task transitions to `COMPLETED` only when its acceptance criteria are met and, for executable work, a real command/result is cited.
- **Memory is a side effect**: an entry in `memory.md` is evidence of verified work, not a substitute for running the build/test/scan.

## Indicators of Done (Shared Memory)

| Indicator | Target |
| --- | --- |
| Baseline loaded on startup | every agent reads `projectbrief.md`, `activeContext.md`, `progress.md` before acting |
| Task lifecycle status | 100% of tasks have a current lifecycle status (`PENDING`/`IN_PROGRESS`/`COMPLETED`/`BLOCKED`/`ABANDONED`) |
| Handoffs acknowledged | 100% of `PENDING` handoffs reach `ACKNOWLEDGED`, then `COMPLETED`; 0 stale `PENDING` handoffs |
| Orphaned tasks | 0 `IN_PROGRESS` tasks with no assigned role |
| Append-only integrity | 0 destructive edits to `activeContext.md`/`progress.md`/`memory.md` |
| _index consistency | `_index.md` files match individual file statuses |

## Do Not Do

- Do not operate in a stateless mode without initializing or writing to the `.sdlc/` project baseline.
- Do not read all files on startup — read only what your role or task requires.
- Do not edit another role's primary files without creating an ADR or task explaining the change.
- Do not write source code, tests, or infrastructure/pipeline files into `.sdlc/` — those belong in the project's real source tree.
- Do not treat a `memory.md` entry as a substitute for actually running a build, test, or validation command. If a role's Definition of Done requires verification, write to memory only after that verification has actually been run.
- Do not delete any append-only file content.
- Do not output documentation or design reports only in chat; they must be stored in `.sdlc/` files.

## Verification Check

Before completing any operation:

- Task status updates reflect actual work state.
- Handoffs include all deliverables the recipient needs.
- Append-only files were not modified destructively.
- `_index.md` files are consistent with individual file statuses.
- Contracts include changelog entries for any changes.
