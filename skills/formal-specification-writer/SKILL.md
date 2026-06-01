---
name: formal-specification-writer
description: Write machine-readable specifications for features, process changes, agent behavior, and workflow definitions. Use when the user asks for a formal spec, explicit requirements, acceptance criteria, constraints, or durable planning artifacts. Produces structured markdown with purpose, scope, definitions, REQ/CON/SEC/PAT items, interfaces, and acceptance criteria.
---

# Formal Specification Writer

## When to Use This Skill

Use this skill when the output must become a durable specification rather than a transient plan.

Examples:

- Draft a feature specification
- Define agent or skill behavior formally
- Capture requirements before implementation begins
- Convert planning notes into a reusable specification

## Inputs

Collect these inputs before authoring the specification:

- Purpose of the specification
- Scope boundaries
- Required behaviors
- Constraints and security requirements
- Interfaces, contracts, or file targets when relevant

## Outputs

Return all of the following sections:

- Purpose and scope
- Definitions
- Requirements, constraints, and patterns
- Interfaces and data contracts when applicable
- Acceptance criteria
- Test strategy
- Risks or assumptions when relevant

## Step-by-Step Workflow

1. State the purpose and scope precisely.
2. Define any acronyms or domain-specific terms.
3. Convert behaviors into explicit requirements.
4. Use identifiers such as `REQ-*`, `CON-*`, `SEC-*`, and `PAT-*`.
5. Write acceptance criteria in Given-When-Then form when applicable.
6. Add interface or contract details when the task involves files, schemas, or APIs.
7. Remove contextual references that depend on unstated history.

## Output Format

```markdown
## Specification

### Purpose & Scope
- ...

### Definitions
- ...

### Requirements, Constraints & Patterns
- **REQ-001**: ...
- **CON-001**: ...
- **SEC-001**: ...
- **PAT-001**: ...

### Interfaces & Contracts
- ...

### Acceptance Criteria
- **AC-001**: Given ..., When ..., Then ...

### Test Strategy
- ...
```

## Do Not Do

- Do not write aspirational statements without acceptance criteria.
- Do not rely on unstated repository knowledge.
- Do not mix implementation steps into the specification body unless the user explicitly requests process requirements.

## Verification Check

- The specification is self-contained.
- Requirements are labeled.
- Acceptance criteria are testable.
- Ambiguous terms have been removed or defined.
- The result can be reused without conversation history.