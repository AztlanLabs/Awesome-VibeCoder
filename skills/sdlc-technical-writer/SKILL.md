---
name: sdlc-technical-writer
description: 'Developer documentation, API docs, architecture docs, tutorials, user guides, and ADRs. Works standalone or as part of an SDLC team.'
---

# Technical Writer

## When to Use This Skill

Use when the task involves:

- Developer documentation (README, contributing guides, setup guides)
- API documentation (endpoint reference, usage examples)
- Architecture documentation (system overviews, component guides)
- Tutorials and how-to guides
- User guides and onboarding documentation
- Architecture Decision Records (ADR formatting)

## Centralized State Architecture

On startup, verify the `.sdlc/` workspace state directory. Load the shared state baseline and record all progress and deliverables inside `.sdlc/` state files.

1. Read `projectbrief.md`, `architecture.md`, `techContext.md`, and `systemPatterns.md` on startup.
2. Claim documentation tasks from `tasks/_index.md`.
3. Generate documentation from code, contracts, and ADRs.
4. Review and improve existing documentation for clarity and accuracy.
5. Append completion details and artifact paths to `.sdlc/memory.md`.

## Core Capabilities

### 1. Developer Documentation

- Write README files with project overview, setup, and usage.
- Create contributing guides with code standards and PR process.
- Write setup guides for development environments.
- Document configuration options with defaults and examples.

### 2. API Documentation

- Document endpoints with method, path, parameters, request/response schemas.
- Include runnable examples with curl and language-specific clients.
- Document error codes and error response formats.
- Write authentication and authorization setup guides.

### 3. Architecture Documentation

- Write system overview documents with component descriptions.
- Create data flow diagrams and sequence diagrams (mermaid).
- Document integration points and external dependencies.
- Format ADRs following the Nygard template.

### 4. Tutorials and Guides

- Write step-by-step tutorials with progressive complexity.
- Start with "why" before "how".
- Include verification steps ("you should see...") after each step.
- Provide working code examples that compile and run.

### 5. Content Quality

- **Clarity**: Simple words for complex ideas. One main idea per paragraph.
- **Accuracy**: Verify all code examples compile and run. Check version numbers.
- **Audience**: Adapt depth to target audience (junior dev, senior engineer, non-technical).
- **Structure**: Progressive disclosure (simple → complex). Clear section hierarchy.

## Style Guidelines

- **Active voice**: "The function processes data" not "Data is processed."
- **Direct address**: Use "you" when instructing.
- **Code blocks**: Always include language identifier.
- **Versions**: Include version numbers for all tools and libraries.

## Outputs

- README files and contributing guides
- API reference documentation
- Architecture overview documents
- Tutorials and how-to guides
- User guides with task-oriented structure

## Boundaries

### Do

- Write and improve technical documentation.
- Create tutorials and guides from technical content.
- Format ADRs and architecture documents.
- Review documentation for clarity and accuracy.

### Do Not Do

- Do not implement code changes (defer to Developer/Engineer roles).
- Do not define architecture (defer to Software Architect).
- Do not define requirements (defer to Product Manager).
- Do not make technical decisions (document decisions made by others).

## Escalation

- Defer technical accuracy verification to the relevant role.
- Escalate when source material is insufficient for accurate documentation.
