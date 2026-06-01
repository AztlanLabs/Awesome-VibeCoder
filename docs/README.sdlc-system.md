# SDLC Multi-Agent System

A modular, standalone-first AI system for the Software Development Lifecycle. Every agent and skill works independently out of the box. Multi-agent collaboration is an optional enhancement.

## Quick Start

### Run Individually (Single-Agent Run)

You can run any `sdlc-*.agent.md` file individually. On startup, the agent will automatically initialize the `.sdlc/` shared state directory if it is missing, load the project baseline, perform its task, and write all logs and deliverables directly back to `.sdlc/`.

### Run Collaboratively (Multi-Agent Workflows)

Run multiple agents in sequence or in parallel (see [Workflows](../workflows/)). Because they all read and write to the same `.sdlc/` directory, they share context automatically and pick up right where the previous agent left off.

### Use the Orchestrator (Full Coordination)

For large projects, use the optional orchestrator:

1. Activate `sdlc-orchestrator.agent.md`
2. Describe your project goal
3. The orchestrator initializes `.sdlc/`, creates tasks, and recommends which agents to run.

## Architecture

### Always-On Centralized State Architecture

Every SDLC agent and skill operates within a unified, file-based shared state plane. Stateless execution is completely eliminated, ensuring a consistent and version-controlled project baseline.

| Startup Directory State | Behavioral Execution | Primary Output Destination |
|---|---|---|
| Missing `.sdlc/` folder | Automatically initialized with standard templates | `.sdlc/` files & chronicle appends to `.sdlc/memory.md` |
| Existing `.sdlc/` folder | Baseline loaded automatically for context awareness | `.sdlc/` files & chronicle appends to `.sdlc/memory.md` |

### Shared Knowledge Layer (`.sdlc/`)

When team mode is active, agents collaborate through a file-based shared state:

```text
.sdlc/
├── projectbrief.md              # Goals, scope, constraints
├── architecture.md              # System architecture, components
├── techContext.md                # Tech stack, dependencies
├── activeContext.md              # Current focus (append-only)
├── progress.md                   # Status tracking (append-only)
├── systemPatterns.md            # Conventions, coding standards
├── tasks/                        # Task files with lifecycle tracking
├── decisions/                    # Architecture Decision Records
├── contracts/                    # Cross-role agreements (API, DB, security, test)
├── handoffs/                     # Agent-to-agent work transfers
└── memory.md                     # Cross-session context
```

## Role Catalog

### 16 Specialized Roles

| Role | Agent | Skill | Domain |
|---|---|---|---|
| Software Architect | [sdlc-software-architect](../agents/sdlc-software-architect.agent.md) | [SKILL](../skills/sdlc-software-architect/SKILL.md) | System design, ADRs, tech evaluation |
| Developer | [sdlc-developer](../agents/sdlc-developer.agent.md) | [SKILL](../skills/sdlc-developer/SKILL.md) | Clean code, SOLID, design patterns |
| Frontend Engineer | [sdlc-frontend-engineer](../agents/sdlc-frontend-engineer.agent.md) | [SKILL](../skills/sdlc-frontend-engineer/SKILL.md) | UI components, accessibility, performance |
| Backend Engineer | [sdlc-backend-engineer](../agents/sdlc-backend-engineer.agent.md) | [SKILL](../skills/sdlc-backend-engineer/SKILL.md) | APIs, services, data access |
| Full Stack Engineer | [sdlc-fullstack-engineer](../agents/sdlc-fullstack-engineer.agent.md) | [SKILL](../skills/sdlc-fullstack-engineer/SKILL.md) | End-to-end feature delivery |
| UX/UI Designer | [sdlc-ux-ui-designer](../agents/sdlc-ux-ui-designer.agent.md) | [SKILL](../skills/sdlc-ux-ui-designer/SKILL.md) | JTBD, journey maps, flow specs |
| DB Architect | [sdlc-db-architect](../agents/sdlc-db-architect.agent.md) | [SKILL](../skills/sdlc-db-architect/SKILL.md) | Data modeling, schema, indexing |
| DB Developer | [sdlc-db-developer](../agents/sdlc-db-developer.agent.md) | [SKILL](../skills/sdlc-db-developer/SKILL.md) | Queries, migrations, performance |
| Cybersecurity Architect | [sdlc-cybersecurity-architect](../agents/sdlc-cybersecurity-architect.agent.md) | [SKILL](../skills/sdlc-cybersecurity-architect/SKILL.md) | Threat modeling, Zero Trust |
| Cybersecurity Developer | [sdlc-cybersecurity-developer](../agents/sdlc-cybersecurity-developer.agent.md) | [SKILL](../skills/sdlc-cybersecurity-developer/SKILL.md) | OWASP review, secure coding |
| QA Tester | [sdlc-qa-tester](../agents/sdlc-qa-tester.agent.md) | [SKILL](../skills/sdlc-qa-tester/SKILL.md) | Test strategy, automation, gates |
| DevOps Engineer | [sdlc-devops-engineer](../agents/sdlc-devops-engineer.agent.md) | [SKILL](../skills/sdlc-devops-engineer/SKILL.md) | CI/CD, IaC, monitoring |
| Technical Writer | [sdlc-technical-writer](../agents/sdlc-technical-writer.agent.md) | [SKILL](../skills/sdlc-technical-writer/SKILL.md) | Docs, tutorials, API reference |
| Product Manager | [sdlc-product-manager](../agents/sdlc-product-manager.agent.md) | [SKILL](../skills/sdlc-product-manager/SKILL.md) | Requirements, user stories, roadmap |
| Responsible AI | [sdlc-responsible-ai](../agents/sdlc-responsible-ai.agent.md) | [SKILL](../skills/sdlc-responsible-ai/SKILL.md) | Bias, accessibility, ethics |
| Scrum Master | [sdlc-scrum-master](../agents/sdlc-scrum-master.agent.md) | [SKILL](../skills/sdlc-scrum-master/SKILL.md) | Sprint planning, agile coaching |

### Supporting Components

| Component | Path | Purpose |
|---|---|---|
| Shared Memory Skill | [SKILL](../skills/sdlc-shared-memory/SKILL.md) | `.sdlc/` state management |
| Shared Memory Instructions | [Instructions](../instructions/sdlc-shared-memory.instructions.md) | File format contracts |
| Orchestrator | [Agent](../agents/sdlc-orchestrator.agent.md) | Optional multi-agent coordinator |
| Sequential Workflow | [Workflow](../workflows/sdlc-sequential.workflow.md) | One-at-a-time execution order |
| Parallel Workflow | [Workflow](../workflows/sdlc-parallel.workflow.md) | Concurrent execution phases |

## Workflows

### Sequential (Recommended for Most Projects)

See [sdlc-sequential.workflow.md](../workflows/sdlc-sequential.workflow.md) for the full execution order.

Summary: Planning → Implementation → Quality → Delivery, one agent at a time.

### Parallel (For Large Projects)

See [sdlc-parallel.workflow.md](../workflows/sdlc-parallel.workflow.md) for concurrent execution phases.

Summary: Run non-conflicting agents simultaneously with dependency gates between phases.

## Handoff Protocol

When one agent's output feeds into another agent's input:

1. The producing agent creates a handoff file in `.sdlc/handoffs/`.
2. The consuming agent reads pending handoffs on startup.
3. The consuming agent acknowledges and completes the handoff.

See [sdlc-shared-memory SKILL](../skills/sdlc-shared-memory/SKILL.md) for the full handoff specification.

## FAQ

**Can I use just one agent?**
Yes. Every agent is fully functional when run individually. It will automatically initialize the `.sdlc/` workspace baseline at your project root and record its execution details and logs there.

**Do I need to use all 16 roles?**
No. Use only the roles relevant to your project. A simple API project might use only Backend Engineer + QA Tester.

**Can I run agents in any order?**
Yes. The sequential workflow is a recommendation, not a requirement. You control the sequence.

**What if I want to use an agent without the SDLC prefix?**
The `sdlc-*` agents are designed for multi-agent collaboration. The repository also has standalone agents (some now deprecated) for individual use.

**How do agents share information?**
Through the `.sdlc/` directory. Each agent reads shared state on startup and writes its results back. The shared memory skill defines file ownership and concurrency rules.
