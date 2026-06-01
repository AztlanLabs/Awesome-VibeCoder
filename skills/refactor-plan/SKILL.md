---
name: refactor-plan
description: 'Plan a multi-file refactor with proper sequencing and rollback steps'
---

# Refactor Plan

Use this skill to design and plan a multi-file refactoring process, establishing execution sequences, impact scopes, verification steps, and rollback options before editing codebase files.

## Trigger Conditions

Invoke this skill when:
- Planning a behavior-preserving code restructuring that spans multiple files or modules.
- Introducing new abstractions, shared types, or architectural patterns.
- Ensuring safety, regression protection, and step-by-step verification checklists for code cleanups.

## Centralized State Architecture

On startup, verify the `.sdlc/` workspace state directory. Load the shared state baseline and record all Refactor Plans under `.sdlc/decisions/` or `.sdlc/tasks/`.

1. Read `.sdlc/architecture.md` and `.sdlc/systemPatterns.md` on startup to align with established design guidelines.
2. Format and save the Refactor Plan as an Architecture Decision Record (ADR) under `.sdlc/decisions/ADR-*.md` if it changes system-wide patterns, or write it directly as a task specification under `.sdlc/tasks/`.
3. Add a log entry to `.sdlc/progress.md` referencing the newly created refactoring plan.

## Core Capabilities

- **Dependency and Sequence Mapping**: Plan changes in a logical sequence (e.g., types/interfaces first, then implementations, then test suites).
- **Rollback Planning**: Define specific actions to revert modifications if testing or compilation checks fail at any stage.
- **Risk Assessment**: Identify potential regression vectors, public API breakages, or runtime performance impacts.

## Inputs & Outputs

### Inputs
- `${input:refactorDescription}`: A detailed explanation of the refactoring goal and target areas.

### Outputs
A structured markdown Refactor Plan containing:
1. **Current State**: Description of the existing code smell or architecture.
2. **Target State**: Description of the improved code structure.
3. **Affected Files**: Table mapping files, change types (modify/create/delete), and blocking relationships.
4. **Execution Plan**: Phased checklist (Types, Implementation, Tests, Cleanup) with verification checkpoints.
5. **Rollback Plan**: Clear instructions on how to undo modifications at any point.
6. **Risks**: Assessment of potential regressions and mitigation strategies.

---

## Boundaries & Guardrails

- **Zero Behavior Changes**: Refactoring MUST NOT change the observable behavioral footprint of the application. Do not mix feature additions with refactoring.
- **Test Mandate**: Refactoring requires existing or newly introduced tests. If no tests cover the refactored code, planning MUST include adding tests first.
- **Scope Limitation**: Limit the refactoring plan to the target scope. Avoid "while we are here" edits to unrelated systems.

---

## Verification Checklist

Before finalizing the refactoring plan, verify that:
- [ ] The refactoring goal is clearly defined without behavioral drift.
- [ ] Every affected file is listed along with its dependencies.
- [ ] The execution phases are ordered dependencies-first.
- [ ] A concrete, actionable rollback plan exists for every phase.
- [ ] All potential regression risks are mapped to mitigation strategies.
