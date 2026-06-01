---
applyTo: '.sdlc/**'
---

# SDLC Shared Memory Protocol

Standards for reading, writing, and maintaining `.sdlc/` shared state files across SDLC agents.

## File Format Contracts

### Timestamps

Use ISO-8601 format for all timestamps: `2026-05-31T06:00:00Z`.

### Append-Only Files

`activeContext.md`, `progress.md`, and `memory.md` use append-only semantics:

```markdown
### 2026-05-31T06:00:00Z — [Agent Role]
[Content]
```

Never edit or delete prior entries. Always append at the end of the file.

### Index Files

All `_index.md` files use status-grouped sections. Keep entries sorted by most-recent-first within each section.

### Sequential IDs

- Tasks: `TASK-001`, `TASK-002`, ...
- Handoffs: `HO-001`, `HO-002`, ...
- Decisions: `ADR-001`, `ADR-002`, ...

Read the corresponding `_index.md` to determine the next available ID before creating a new entry.

## Concurrency Rules

### Primary Writer Ownership

In team mode (multiple agents active), each file has a designated primary writer. Other agents must not write to files they do not own, except for append-only files and acknowledging handoffs.

### Append-Only Safety

Multiple agents may append to `activeContext.md`, `progress.md`, and `memory.md` simultaneously. Each entry is self-contained with a timestamp and role identifier.

### Task Claiming

Tasks use a claim-on-read pattern:

1. Read `tasks/_index.md` to find tasks matching your role.
2. Read the task file to verify status is `PENDING`.
3. Update status to `IN_PROGRESS` and set `Assigned To`.
4. Update `_index.md` to reflect the new status.

If two agents attempt to claim the same task, the first to write wins. The second agent must re-read and select a different task.

## Handoff Protocol

### Status Transitions

```
PENDING → ACKNOWLEDGED → COMPLETED
```

- **PENDING**: The producing agent created the handoff but the consuming agent has not read it yet.
- **ACKNOWLEDGED**: The consuming agent read the handoff and accepted the deliverables.
- **COMPLETED**: The consuming agent finished work based on the handoff deliverables.

### Required Fields

Every handoff file must include: From, To, Status, Created, Deliverables, and Notes for Recipient.

## Task Lifecycle States

```
PENDING → IN_PROGRESS → COMPLETED
                      → BLOCKED → IN_PROGRESS (when unblocked)
                      → ABANDONED (with rationale)
```

### Status Definitions

- **PENDING**: Created but not yet started. Dependencies may or may not be met.
- **IN_PROGRESS**: An agent is actively working on this task.
- **COMPLETED**: All acceptance criteria are met and verified.
- **BLOCKED**: Cannot proceed due to a dependency, missing information, or external blocker. Must include a blocker description.
- **ABANDONED**: Deliberately cancelled with documented rationale.

## Always-On Centralized State Architecture

Every agent and skill checks for the `.sdlc/` directory at the project root on startup:

- If present: Load the `sdlc-shared-memory` skill, read the shared state baseline, and respect ownership rules.
- If absent: Automatically initialize the `.sdlc/` directory and populate it with standard templates. All subsequent operations must utilize this centralized state architecture to maintain a shared codebase baseline.
