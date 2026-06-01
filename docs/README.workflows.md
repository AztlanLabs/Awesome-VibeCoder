# Workflows

This repository contains workflow definitions under [workflows/](../workflows/) that coordinate larger multi-agent software development processes. These workflows orchestrate different roles to work together in a standardized sequence or in parallel with dependency gates.

## SDLC Workflows

We provide two primary workflows for executing multi-agent software development lifecycle (SDLC) projects:

### 1. [SDLC Sequential Workflow](file:///home/crowne/Documents/Documents/VS%20Code/Awesome-VibeCoder/workflows/sdlc-sequential.workflow.md)

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

### 2. [SDLC Parallel Workflow](file:///home/crowne/Documents/Documents/VS%20Code/Awesome-VibeCoder/workflows/sdlc-parallel.workflow.md)

Runs agents concurrently when their tasks have no dependencies on each other. This workflow defines stages and concurrency boundaries.

- **Use Case**: Best for rapid prototyping or larger teams of agents where you want to minimize wait times.
- **Workflow Stages**:
  - **Phase 1 (Conception)**: Software Architect + UX/UI Designer + Database Architect (parallel)
  - **Phase 2 (Implementation)**: Backend Engineer + Frontend Engineer + Database Developer + Cybersecurity Architect (parallel)
  - **Phase 3 (Testing & Securing)**: QA Tester + Cybersecurity Developer (parallel)
  - **Phase 4 (Deployment)**: DevOps Engineer (sequential gate)

---

## How to Run Workflows

Workflows rely on the shared knowledge layer `.sdlc/` created in the target project. To execute:
1. Initialize the workspace state (usually via [sdlc-orchestrator.agent.md](file:///home/crowne/Documents/Documents/VS%20Code/Awesome-VibeCoder/agents/sdlc-orchestrator.agent.md) or by asking any agent to scaffold the directory).
2. Execute the workflow files using your orchestration runner or step-by-step manually.

## Related Areas

- [Agents Overview](README.agents.md)
- [Skills Overview](README.skills.md)
- [Instructions Overview](README.instructions.md)
- [SDLC System Overview](README.sdlc-system.md)
