---
name: architecture-option-evaluator
description: Evaluate architecture options, boundaries, and consolidation decisions for agents, skills, modules, or workflows. Use when the user asks to merge overlapping roles, compare structures, reduce redundancy, or choose an implementation architecture. Produces a current-state summary, explicit options, a recommendation, trade-offs, and migration risks.
---

# Architecture Option Evaluator

## When to Use This Skill

Use this skill when the task requires an architecture recommendation instead of immediate implementation.

Examples:

- Merge overlapping agents, skills, services, or modules
- Compare alternative folder structures or workflow boundaries
- Remove redundant roles without losing capability coverage
- Decide whether a capability belongs in an agent or a skill

## Inputs

Collect these inputs before evaluating options:

- The target capability or family being changed
- The overlapping files or roles
- Hard constraints and exclusions
- Existing patterns that must be preserved
- Migration tolerance and compatibility requirements

## Outputs

Return all of the following:

- Current-state summary
- 2-3 mutually exclusive options
- One recommended option
- Explicit trade-offs for every option
- Migration impacts and risks

## Step-by-Step Workflow

1. Summarize the current overlap in exact terms.
2. Name each option precisely.
3. Score each option against these criteria:
   - semantic clarity
   - separation of concerns
   - redundancy reduction
   - migration cost
   - extensibility
4. Reject options that preserve ambiguity or duplicate responsibilities.
5. Recommend one option and state why the rejected options are weaker.
6. List the concrete migration effects on files, names, and documentation.

## Output Format

```markdown
## Architecture Decision

### Current State
- ...

### Options
| Option | Benefits | Drawbacks | Score |
|---|---|---|---|
| Option A | ... | ... | 4/5 |

### Recommendation
- ...

### Migration Impact
- ...

### Risks
- ...
```

## Do Not Do

- Do not implement code changes.
- Do not return overlapping options that differ only by naming.
- Do not recommend a structure that mixes agent and skill responsibilities.

## Verification Check

- The options are mutually exclusive.
- The recommendation is explicit.
- The trade-offs are concrete.
- The migration impact is listed.
- The output reduces ambiguity instead of preserving it.