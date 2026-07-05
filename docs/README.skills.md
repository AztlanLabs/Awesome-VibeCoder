# Skills

This repository currently includes 42 root skills in [skills/](../skills/). Each skill is a task-focused folder anchored by a `SKILL.md` file and, when needed, bundled templates, examples, or workflow notes.

## Modular SDLC Skills (New)

We have added **17 modular, standalone-first skills** for key roles in the Software Development Lifecycle (SDLC). These skills define the expert knowledge, Trigger Conditions, inputs, outputs, and Dual-Mode behavior for each role.

### SDLC Skills Catalog

| Skill Folder | Domain / Purpose | Key Focus Areas |
| --- | --- | --- |
| [sdlc-shared-memory](../skills/sdlc-shared-memory/SKILL.md) | Shared Workspace State | Core `.sdlc/` read/write protocol, task claiming, handoffs, ADR updates |
| [sdlc-software-architect](../skills/sdlc-software-architect/SKILL.md) | Software Architecture | Component mappings, bounded contexts, pattern definitions, ADRs |
| [sdlc-developer](../skills/sdlc-developer/SKILL.md) | Code Implementation | Clean code (SOLID), refactoring, inline documentation, debugging |
| [sdlc-frontend-engineer](../skills/sdlc-frontend-engineer/SKILL.md) | Frontend Development | UI design translation, accessibility (WCAG 2.1 AA), state, rendering |
| [sdlc-backend-engineer](../skills/sdlc-backend-engineer/SKILL.md) | Backend Services | REST/GraphQL APIs, service architectures, errors, pagination |
| [sdlc-fullstack-engineer](../skills/sdlc-fullstack-engineer/SKILL.md) | Full Stack Delivery | Integration of UI and API layers, vertical feature slices |
| [sdlc-ux-ui-designer](../skills/sdlc-ux-ui-designer/SKILL.md) | UX Research & Journeys | Jobs-to-be-Done analysis, journey maps, Figma specifications |
| [sdlc-db-architect](../skills/sdlc-db-architect/SKILL.md) | Database Modeling | Entity relationships (ERD), schemas normalization, sharding, indexes |
| [sdlc-db-developer](../skills/sdlc-db-developer/SKILL.md) | Database Programming | Complex queries, stored procedures, migration scripts, optimization |
| [sdlc-cybersecurity-architect](../skills/sdlc-cybersecurity-architect/SKILL.md) | Security Policy & Design | STRIDE/DREAD threat models, Zero Trust boundaries, compliance |
| [sdlc-cybersecurity-developer](../skills/sdlc-cybersecurity-developer/SKILL.md) | Security Development | OWASP vulnerability fixing, secure input/output, security tests |
| [sdlc-qa-tester](../skills/sdlc-qa-tester/SKILL.md) | Quality Engineering | Test pyramid strategy, unit/integration/E2E code, quality gates |
| [sdlc-devops-engineer](../skills/sdlc-devops-engineer/SKILL.md) | DevOps & Infrastructure | CI/CD pipeline automation, IaC templates, alerts/monitoring |
| [sdlc-technical-writer](../skills/sdlc-technical-writer/SKILL.md) | Tech Documentation | API references, developer docs, user manuals, README guides |
| [sdlc-product-manager](../skills/sdlc-product-manager/SKILL.md) | Product Backlog Management | Requirements discovery, user stories, issues, task prioritization |
| [sdlc-responsible-ai](../skills/sdlc-responsible-ai/SKILL.md) | Responsible AI Review | Bias mitigation, accessibility reviews, ethical guardrails, privacy |
| [sdlc-scrum-master](../skills/sdlc-scrum-master/SKILL.md) | Agile Delivery | Sprint ceremonies coaching, impediment removal, velocity tracking |

---

## Standalone Specialist Skills

These skills remain active for general prompt engineering, planning, refactoring, and code analysis:

| Skill | Purpose |
| --- | --- |
| [ai-prompt-engineering-safety-review](../skills/ai-prompt-engineering-safety-review/SKILL.md) | Review prompts for safety, bias, security, and effectiveness |
| [architecture-option-evaluator](../skills/architecture-option-evaluator/SKILL.md) | Evaluate architecture options, trade-offs, and consolidation decisions |
| [context-map](../skills/context-map/SKILL.md) | Build a map of relevant files before making changes |
| [context-researcher](../skills/context-researcher/SKILL.md) | Investigate code, bugs, or issues and produce an evidence-backed research file with root causes and exact files/lines |
| [formal-specification-writer](../skills/formal-specification-writer/SKILL.md) | Write structured, machine-readable specifications and requirements |
| [implementation-plan-generator](../skills/implementation-plan-generator/SKILL.md) | Generate deterministic human and AI-executable implementation plans |
| [planning-quality-gate](../skills/planning-quality-gate/SKILL.md) | Validate planning artifacts for ambiguity, overlap, and missing verification |
| [premium-frontend-ui](../skills/premium-frontend-ui/SKILL.md) | Craft high-end frontend UI and interaction work |
| [prompt-builder](../skills/prompt-builder/SKILL.md) | Create production-ready `.prompt.md` files through structured discovery |
| [prompt-maintainer](../skills/prompt-maintainer/SKILL.md) | Improve an existing prompt after it has been used |
| [prompt-markdown-sanitizer](../skills/prompt-markdown-sanitizer/SKILL.md) | Remove contradictions and ambiguity from prompt markdown |
| [readme-blueprint-generator](../skills/readme-blueprint-generator/SKILL.md) | Generate a comprehensive repository README blueprint |
| [refactor](../skills/refactor/SKILL.md) | Perform behavior-preserving code refactors |
| [refactor-method-complexity-reduce](../skills/refactor-method-complexity-reduce/SKILL.md) | Lower method complexity by extracting helpers |
| [refactor-plan](../skills/refactor-plan/SKILL.md) | Plan a multi-file refactor with sequencing and rollback thinking |
| [remember](../skills/remember/SKILL.md) | Turn lessons learned into reusable memory instructions |
| [technical-overview-maintainer](../skills/technical-overview-maintainer/SKILL.md) | Maintain a single implementation overview document for code changes |
| [technical-path-indexer](../skills/technical-path-indexer/SKILL.md) | Scan repository paths, routes, references, and companion-file links to emit weighted technical path indexes |
| [web-coder](../skills/web-coder/SKILL.md) | Apply deep web platform knowledge across frontend and backend work |
| [web-design-reviewer](../skills/web-design-reviewer/SKILL.md) | Inspect and fix design and layout issues visually |
| [web-design-system](../skills/web-design-system/SKILL.md) | Design tokens (color/space/type/radius/shadow/motion), tiered model, theming, primitive APIs, Figma sync, versioning |
| [web-accessibility-audit](../skills/web-accessibility-audit/SKILL.md) | WCAG 2.2 AA/AAA audits with automated + manual passes and a remediation report |
| [web-performance-budget](../skills/web-performance-budget/SKILL.md) | Core Web Vitals (LCP/INP/CLS/TTFB/TBT) and asset budgets enforced across the build pipeline |
| [what-context-needed](../skills/what-context-needed/SKILL.md) | Ask what files are needed before answering a codebase question |

---

## Directory Notes

- The root [skills/](../skills/) folder is the main collection.
- Mirrored copies also exist under [.github/skills/](../.github/skills/) for customization-library layouts.
- Skills are designed to be standalone-first. You can copy a single skill directory to your project and reference its markdown in your own custom agents.

## Browse The Collection

Open [skills/](../skills/) for the full set.
