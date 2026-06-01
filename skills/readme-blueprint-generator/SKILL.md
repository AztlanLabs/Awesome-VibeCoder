---
name: readme-blueprint-generator
description: 'Generate a comprehensive, developer-focused README.md for a repository by analyzing configuration-layer documentation and instructions.'
---

# README Blueprint Generator

Use this skill when you need to construct or fully rewrite a comprehensive, production-grade repository root `README.md` that acts as the single source of truth for onboarding and architectural reference.

## Trigger Conditions

Invoke this skill when:
- The user requests a new or updated root `README.md` for their repository.
- The project setup has evolved, and the master onboarding documentation needs synchronization.
- You are bootstrapping documentation for a newly structured workspace.

## Centralized State Architecture

On startup, verify the `.sdlc/` workspace state directory. Load the shared state baseline and record README updates under `.sdlc/progress.md`.

1. Read `.sdlc/projectbrief.md`, `.sdlc/architecture.md`, `.sdlc/techContext.md`, and `.sdlc/systemPatterns.md` to collect context on the active team state, technologies, and coding conventions.
2. Generate/update the root `README.md` using both the `.github/copilot/` configuration and the `.sdlc/` project baseline files to ensure complete synchronization.
3. If new directories, technologies, or configuration settings are detected, update the corresponding fields in `.sdlc/techContext.md`.
4. Append a status log entry to `.sdlc/progress.md`.

## Core Capabilities

- **Documentation Scanning**: Parse specialized project configuration contexts, specifically reading from the `.github/copilot/` directory and `.github/copilot-instructions.md` (when present).
- **Architecture Synthesis**: Translate abstract diagrams or high-level architecture descriptions into clear, structured markdown narratives (and optional mermaid diagrams).
- **Onboarding Structuring**: Build developer-focused installation, configuration, testing, and contribution guides matched directly to the repository's stack.
- **Standards Cataloging**: Enforce clean representations of the coding conventions and branching workflows defined by the repository's rules.

## Inputs & Outputs

### Inputs
- Files inside the `.github/copilot/` directory (e.g. `Architecture`, `Code_Exemplars`, `Coding_Standards`, `Project_Folder_Structure`, `Technology_Stack`, `Unit_Tests`, `Workflow_Analysis`).
- The `.github/copilot-instructions.md` or `.github/copilot/copilot-instructions.md` configuration file.
- Workspace root search results.

### Outputs
A structured markdown root `README.md` containing:
1. **Project Name & Description**: Concise summary of purpose and business/user context.
2. **Technology Stack**: Structured table or list of languages, runtimes, frameworks, and their versions.
3. **Project Architecture**: High-level map of components, bounded contexts, and dependency relationships (with mermaid diagrams).
4. **Getting Started**: Ordered checklist for prerequisites, installation, environment configuration, and running the application.
5. **Project Structure**: Concise directory hierarchy map with relative explanations.
6. **Key Features**: List of functional capabilities with descriptions.
7. **Development Workflow**: Branching conventions, code review steps, and CI/CD triggers.
8. **Coding Standards**: Summary of style guides, naming conventions, and linting rules.
9. **Testing Guidelines**: Instructions for writing, running, and validating tests (unit, integration, E2E).
10. **Contributing**: Access patterns, exemplars references, and governance gates.
11. **License**: Licensing terms.

---

## Boundaries & Guardrails

- **No Placeholder Links**: You MUST NOT generate empty or broken markdown links. Use relative repository paths (e.g., `[Coding Standards](file:///.github/copilot/Coding_Standards)`) or valid external URLs.
- **Accurate Technology Scope**: You WILL ONLY list technologies and frameworks that are actively detected in the workspace or explicitly defined in the input documentation. Never hallucinate tools or frameworks.
- **Preserve Command Validity**: Ensure all installation and test execution commands are verified against the technology stack files (e.g. `package.json` for npm, `cargo.toml` for rust).

---

## Verification Checklist

Before emitting the finalized `README.md` content, verify that:
- [ ] Every section in the output structure is populated with evidence-backed project context.
- [ ] Folder structure diagrams match the actual active directories in the workspace.
- [ ] Command lists are fully runnable and correct for the detected operating environments.
- [ ] Links to other documentation files schemes are correct and clickable.

