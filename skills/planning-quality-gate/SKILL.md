---
name: planning-quality-gate
description: Validate draft architecture advice, implementation plans, and specifications for ambiguity, overlap, missing dependencies, unverifiable steps, and weak output contracts. Use immediately before finalizing a planning deliverable. Produces pass-fail findings and concrete corrections required for release quality planning artifacts.
---

# Planning Quality Gate

## When to Use This Skill

Use this skill as the final validation pass before delivering any planning artifact.

Examples:

- Validate architecture advice before recommending a merge
- Validate a phased implementation plan before handoff
- Validate a formal specification before publishing it

## Inputs

Collect the draft deliverable and, when available:

- user goal
- constraints
- file inventory
- dependencies
- validation expectations

## Outputs

Return all of the following:

- overall status: `PASS` or `FAIL`
- numbered findings
- concrete fixes for every failing finding
- final release recommendation

## Step-by-Step Workflow

1. Check that the deliverable matches its declared mode.
2. Check that requirements and constraints are explicit.
3. Check that files, dependencies, risks, and validation are present when relevant.
4. Check that no task or requirement requires interpretation.
5. Check that agent and skill boundaries remain clear.
6. Mark the draft as `PASS` only if no material ambiguity remains.

## Output Format

```markdown
## Planning Quality Gate

### Status
- PASS | FAIL

### Findings
1. ...

### Required Fixes
1. ...

### Release Recommendation
- ...
```

## Do Not Do

- Do not rewrite the full artifact unless the user asks.
- Do not approve a draft with missing verification steps.
- Do not ignore overlap between planning and execution responsibilities.

## Verification Check

- The result contains PASS or FAIL.
- Every finding is actionable.
- Every failing item includes a concrete fix.
- The gate does not invent new scope.