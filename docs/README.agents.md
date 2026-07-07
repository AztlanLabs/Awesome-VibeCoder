# Agents

This repository currently includes 38 active agent definitions in [agents/](../agents/) (with 13 deprecated agents moved to the [deprecate/agents/](../deprecate/agents/) directory). They represent a personal working set of Copilot agent modes for planning, implementation, review, architecture, research, and specialized Software Development Lifecycle (SDLC) workflows.

## Modular SDLC Agents (New)

We have introduced a set of **20 modular, standalone-first agents** designed for the Software Development Lifecycle (SDLC). Each agent is fully integrated with the **Always-On Centralized State Architecture** using the `.sdlc/` shared state directory to coordinate work across specialized roles.

### SDLC Role Agents

| Agent File | Role / Domain | Focus Areas |
| --- | --- | --- |
| [sdlc-orchestrator.agent.md](../agents/sdlc-orchestrator.agent.md) | Orchestrator | Workspace initialization, task decomposition, progress monitoring |
| [sdlc-software-architect.agent.md](../agents/sdlc-software-architect.agent.md) | Software Architect | Bounded contexts, system boundaries, ADRs, component maps |
| [sdlc-developer.agent.md](../agents/sdlc-developer.agent.md) | General Developer | SOLID clean-code implementation, code refactoring |
| [sdlc-frontend-engineer.agent.md](../agents/sdlc-frontend-engineer.agent.md) | Frontend Engineer | UI components, accessibility (WCAG 2.1 AA), state management, performance |
| [sdlc-backend-engineer.agent.md](../agents/sdlc-backend-engineer.agent.md) | Backend Engineer | Implements endpoints against the API contract, service layers, data access |
| [sdlc-fullstack-engineer.agent.md](../agents/sdlc-fullstack-engineer.agent.md) | Full Stack Engineer | Vertical slice features spanning both backend and frontend layers |
| [sdlc-ux-ui-designer.agent.md](../agents/sdlc-ux-ui-designer.agent.md) | UX/UI Designer | JTBD analysis, user journeys, wireframe flow specifications |
| [sdlc-accessibility-specialist.agent.md](../agents/sdlc-accessibility-specialist.agent.md) | Accessibility Specialist | WCAG audits, a11y requirements, remediation reports |
| [sdlc-db-architect.agent.md](../agents/sdlc-db-architect.agent.md) | DB Architect | Data modeling, schema normalization, ERDs, migration strategies |
| [sdlc-api-designer.agent.md](../agents/sdlc-api-designer.agent.md) | API Designer | API contract design, OpenAPI specs, API versioning |
| [sdlc-db-developer.agent.md](../agents/sdlc-db-developer.agent.md) | DB Developer | T-SQL / SQL optimization, stored procedures, migration scripts |
| [sdlc-cybersecurity-architect.agent.md](../agents/sdlc-cybersecurity-architect.agent.md) | Security Architect | STRIDE threat modeling, authentication, Zero Trust boundaries |
| [sdlc-cybersecurity-developer.agent.md](../agents/sdlc-cybersecurity-developer.agent.md) | Security Developer | Vulnerability remediation (OWASP), secure coding, security tests |
| [sdlc-qa-tester.agent.md](../agents/sdlc-qa-tester.agent.md) | QA Tester | Automated tests (unit, integration, E2E), quality gates |
| [sdlc-code-reviewer.agent.md](../agents/sdlc-code-reviewer.agent.md) | Code Reviewer | Code quality audits, SOLID/security findings, PR reviews |
| [sdlc-devops-engineer.agent.md](../agents/sdlc-devops-engineer.agent.md) | DevOps Engineer | CI/CD pipelines, IaC (Terraform), infrastructure configurations |
| [sdlc-technical-writer.agent.md](../agents/sdlc-technical-writer.agent.md) | Technical Writer | Developer documentation, API references, architecture docs, guides |
| [sdlc-product-manager.agent.md](../agents/sdlc-product-manager.agent.md) | Product Manager | User stories, requirements gathering, issue creation, prioritizations |
| [sdlc-responsible-ai.agent.md](../agents/sdlc-responsible-ai.agent.md) | Responsible AI | Bias checks, accessibility compliance, privacy reviews, ethics |
| [sdlc-scrum-master.agent.md](../agents/sdlc-scrum-master.agent.md) | Scrum Master | Sprint planning, agile ceremony guidance, blockers removal |

---

## Standalone & Specialist Agents

These agents cover non-SDLC or specialized workflows and remain fully active:

| Agent | Focus |
| --- | --- |
| [Beast.agent.md](../agents/Beast.agent.md) | Context-first autonomous coding workflow |
| [CoderBeast.agent.md](../agents/CoderBeast.agent.md) | Prompt-driven autonomous coding workflow |
| [context-researcher.agent.md](../agents/context-researcher.agent.md) | Investigates code, bugs, and issues, producing an evidence-backed research file before implementation |
| [ExpertCoder.agent.md](../agents/ExpertCoder.agent.md) | Hybrid prompt-driven autonomous coding and planning workflow |
| [gpt-5-beast-mode.agent.md](../agents/gpt-5-beast-mode.agent.md) | Beast Mode 2.0 autonomous troubleshooting and tool execution |
| [planning-agent.agent.md](../agents/planning-agent.agent.md) | Planning-only entry point for specs, architecture, and plans |
| [PromptFileAuthor.agent.md](../agents/PromptFileAuthor.agent.md) | Creates, sanitizes, and maintains `.prompt.md` files |
| [RepositoryPathAuditor.agent.md](../agents/RepositoryPathAuditor.agent.md) | Scans workspace and builds technical path indexes |
| [agent-governance-reviewer.agent.md](../agents/agent-governance-reviewer.agent.md) | Agent safety and governance review |
| [expert-react-frontend-engineer.agent.md](../agents/expert-react-frontend-engineer.agent.md) | Focused React UI implementation alternative |
| [scientific-paper-research.agent.md](../agents/scientific-paper-research.agent.md) | Literature review and scientific research |
| [simple-app-idea-generator.agent.md](../agents/simple-app-idea-generator.agent.md) | Interactive application brainstorming and refinement |
| [search-ai-optimization-expert.agent.md](../agents/search-ai-optimization-expert.agent.md) | SEO, AEO, and GEO search optimization guidance |
| [electron-angular-native.agent.md](../agents/electron-angular-native.agent.md) | Code reviewer for Electron, Angular, and native stacks |
| [modernization.agent.md](../agents/modernization.agent.md) | Human-in-the-loop legacy project modernization planner |
| [refine-issue.agent.md](../agents/refine-issue.agent.md) | Requirement and GitHub issue refinement |
| [web-design-system-engineer.agent.md](../agents/web-design-system-engineer.agent.md) | Design tokens, component primitives, theming, accessibility primitives |
| [web-performance-engineer.agent.md](../agents/web-performance-engineer.agent.md) | Core Web Vitals and asset budgets — profile, remediate, enforce in CI |

---

## Retired & Deprecated Agents

To avoid naming confusion and duplicate capabilities, the following legacy agents have been deprecated in favor of the new modular SDLC agents:

| Deprecated Agent | Superseded By |
| --- | --- |
| [principal-software-engineer.agent.md](../deprecate/agents/principal-software-engineer.agent.md) | `sdlc-software-architect` + `sdlc-developer` |
| [se-security-reviewer.agent.md](../deprecate/agents/se-security-reviewer.agent.md) | `sdlc-cybersecurity-architect` + `sdlc-cybersecurity-developer` |
| [se-ux-ui-designer.agent.md](../deprecate/agents/se-ux-ui-designer.agent.md) | `sdlc-ux-ui-designer` |
| [se-technical-writer.agent.md](../deprecate/agents/se-technical-writer.agent.md) | `sdlc-technical-writer` |
| [se-product-manager-advisor.agent.md](../deprecate/agents/se-product-manager-advisor.agent.md) | `sdlc-product-manager` |
| [se-responsible-ai-code.agent.md](../deprecate/agents/se-responsible-ai-code.agent.md) | `sdlc-responsible-ai` |
| [ms-sql-dba.agent.md](../deprecate/agents/ms-sql-dba.agent.md) | `sdlc-db-architect` + `sdlc-db-developer` |
| [software-engineer-agent-v1.agent.md](../deprecate/agents/software-engineer-agent-v1.agent.md) | `sdlc-developer` + `sdlc-fullstack-engineer` |
| [context-architect.agent.md](../deprecate/agents/context-architect.agent.md) | `sdlc-software-architect` |
| [CoderBeast-Implementation-Plan.agent.md](../deprecate/agents/CoderBeast-Implementation-Plan.agent.md) | [planning-agent.agent.md](../agents/planning-agent.agent.md) |
| [implementation-plan.agent.md](../deprecate/agents/implementation-plan.agent.md) | [planning-agent.agent.md](../agents/planning-agent.agent.md) |
| [prompt-builder.agent.md](../deprecate/agents/prompt-builder.agent.md) | [PromptFileAuthor.agent.md](../agents/PromptFileAuthor.agent.md) |
| [prompt-engineer.agent.md](../deprecate/agents/prompt-engineer.agent.md) | [PromptFileAuthor.agent.md](../agents/PromptFileAuthor.agent.md) |

*Deprecated agents have been moved to the [deprecate/agents/](../deprecate/agents/) directory. They contain warning headers indicating their replacement files and should not be used for new projects.*

---

## Skill Loading & Composition

The modular agents automatically load their matching skill (from [skills/](../skills/)) and always load [sdlc-shared-memory](../skills/sdlc-shared-memory/SKILL.md) to manage centralized context synchronization.

For more details on orchestration, see the [SDLC System Overview](README.sdlc-system.md) or the [Workflows Documentation](README.workflows.md).

To add a new agent, see the [author-agent recipe](recipes/author-agent.md).
