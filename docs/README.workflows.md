# Workflows

This repository contains workflow definitions under [workflows/](../workflows/) that coordinate larger multi-agent software development processes. These workflows orchestrate different roles to work together in a standardized sequence or in parallel with dependency gates.
## SDLC Workflows

We provide two primary workflows for executing multi-agent software development lifecycle (SDLC) projects:

### 1. [SDLC Sequential Workflow](../workflows/sdlc-sequential.workflow.md)

Runs agents one at a time. The user controls the pace, reviewing progress after each agent finishes before running the next agent.

- **Use Case**: Best for projects where you want tight feedback loops, manual inspection of each deliverable, or where you're running agents one by one.
- **Workflow Order**:
  1. **Software Architect** (`sdlc-software-architect`)
  2. **UX/UI Designer** (`sdlc-ux-ui-designer`)
  3. **Database Architect** (`sdlc-db-architect`)
  4. **Backend Engineer** (`sdlc-backend-engineer`)
  5. **Frontend Engineer** (`sdlc-frontend-engineer`)
  6. **Database Developer** (`sdlc-db-developer`)
  7. **Cybersecurity Architect** (`sdlc-cybersecurity-architect`)
  8. **Cybersecurity Developer** (`sdlc-cybersecurity-developer`)
  9. **QA Tester** (`sdlc-qa-tester`)
  10. **DevOps Engineer** (`sdlc-devops-engineer`)

### 2. [SDLC Parallel Workflow](../workflows/sdlc-parallel.workflow.md)

Runs agents concurrently when their tasks have no dependencies on each other. This workflow defines stages and concurrency boundaries.

- **Use Case**: Best for rapid prototyping or larger teams of agents where you want to minimize wait times.
- **Workflow Stages**:
  - **Phase 1 (Conception)**: Software Architect + UX/UI Designer + Database Architect (parallel)
  - **Phase 2 (Implementation)**: Backend Engineer + Frontend Engineer + Database Developer + Cybersecurity Architect (parallel)
  - **Phase 3 (Testing & Securing)**: QA Tester + Cybersecurity Developer (parallel)
  - **Phase 4 (Deployment)**: DevOps Engineer (sequential gate)

### 3. [Bug Triage Workflow](../workflows/bug-triage.workflow.md)

A short, incident-style workflow for triaging a reported bug from intake to a verified, shipped fix. Roles run in this order:

> **Context Researcher → Cybersecurity Architect (if security) → Developer → QA Tester → DevOps Engineer**

- **Use Case**: A regression, customer report, or monitoring alert requires a tight, evidence-gated fix loop.
- **Skip the Cybersecurity Architect step** for non-security bugs (default).
- **Definition of Done**: root cause documented with file/line evidence, a real failing → passing test transition cited, full relevant regression suite green, and production metrics confirming the defect is closed.

### 4. [Documentation Regeneration Workflow](../workflows/docs-regen.workflow.md)

A pipeline-style workflow that regenerates the project's user-facing documentation from the API contract, with a path audit and an ethics / bias / privacy review as quality gates. Roles run in this order:

> **Technical Writer ← `.sdlc/contracts/api-contracts.md` → RepositoryPathAuditor → Responsible AI**

- **Use Case**: The API contract has changed, a new route was added, a version cut is approaching, or a Responsible AI review flagged a new concern that must be reflected in the docs.
- **Definition of Done**: Technical Writer has regenerated the affected docs with a diff cited; RepositoryPathAuditor has run a path audit with no broken links or undocumented surfaces; Responsible AI has filed (or explicitly waived) every concern.

---

## How to Run Workflows

Workflows rely on the shared knowledge layer `.sdlc/` created in the target project. To execute:
1. Initialize the workspace state (usually via [sdlc-orchestrator.agent.md](../agents/sdlc-orchestrator.agent.md) or by asking any agent to scaffold the directory).
2. Execute the workflow files using your orchestration runner or step-by-step manually.

## Related Areas

- [Agents Overview](README.agents.md)
- [Skills Overview](README.skills.md)
- [Instructions Overview](README.instructions.md)
- [SDLC System Overview](README.sdlc-system.md)
