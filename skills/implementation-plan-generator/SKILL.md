---
name: implementation-plan-generator
description: Generate deterministic implementation plans that are executable by humans or AI. Use when the user asks for step-by-step planning, task decomposition, merge sequencing, refactor planning, or AI-ready execution plans. Produces phased tasks, identifiers, dependencies, file impact, validation steps, and rollback-aware risk notes.
---

# Implementation Plan Generator

## When to Use This Skill

Use this skill when the user needs a concrete plan rather than code.

Examples:

- Plan a multi-file feature or refactor
- Sequence a role or workflow consolidation
- Produce a plan another AI agent can execute directly
- Turn a vague request into atomic implementation phases

## Inputs

Collect these inputs before generating the plan:

- User goal
- Relevant files or folders
- Constraints and exclusions
- Dependencies
- Expected validation method

If a context map already exists, reuse it. Do not duplicate it.

## Outputs

Return all of the following:

- `REQ-*`, `CON-*`, `SEC-*`, and `PAT-*` items
- Phased goals using `GOAL-*`
- Atomic tasks using `TASK-*`
- File impact using `FILE-*`
- Validation steps using `TEST-*`
- Risks and assumptions using `RISK-*` and `ASSUMPTION-*`

## Step-by-Step Workflow

1. Normalize the request into explicit requirements and constraints.
2. Split the work into phases with measurable completion criteria.
3. Write atomic tasks with exact file targets.
4. Declare dependencies between tasks when order matters.
5. Add validation steps for each phase.
6. Add risks, assumptions, and rollback-aware notes.
7. Remove any task that requires guesswork.

## Output Format

```markdown
## Implementation Plan

### Requirements & Constraints
- **REQ-001**: ...
- **CON-001**: ...

### Phases

#### Phase 1
- **GOAL-001**: ...

| Task | Description | File(s) | Depends On |
|---|---|---|---|
| TASK-001 | ... | path/file.ext | — |

### File Impact
- **FILE-001**: path/file.ext — ...

### Testing
- **TEST-001**: ...

### Risks & Assumptions
- **RISK-001**: ...
- **ASSUMPTION-001**: ...
```

## Do Not Do

- Do not generate vague tasks.
- Do not omit file targets when files are implied.
- Do not combine planning and implementation into the same step.

## Verification Check

- Every task is atomic.
- Every phase has a measurable goal.
- Every relevant file is named.
- Dependencies are explicit.
- Validation exists for the complete plan.