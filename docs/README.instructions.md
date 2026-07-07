# Instructions

This repository currently includes 107 root instruction files in [instructions/](../instructions/). The collection spans general engineering guidance, language-specific conventions, frontend and backend frameworks, containerization, local DevOps principles, testing, security, and documentation standards.

This page is intentionally a guide to the collection rather than a generated install catalog. The source of truth is the local [instructions/](../instructions/) directory.

## Core Themes

- General engineering: security, accessibility, performance, context management, and documentation.
- Language and framework guidance: .NET, Java, JavaScript, TypeScript, Python (incl. FastAPI/Django/Flask), Go, Rust (incl. Axum), Ruby, PHP, Swift, Kotlin, Quarkus, Spring, Next.js, Svelte, Solid, Remix, Nuxt, htmx, Deno, Bun, and more.
- Infrastructure and operations: Docker containers, Terraform, Pulumi, PostgreSQL tuning, GitHub Actions workflows, and core DevOps principles.
- API & event contracts: OpenAPI 3.1, AsyncAPI, and OpenTelemetry/otelcol instrumentation.
- Testing and review: Playwright, Pester, review styles, prompt files, Conventional Commits, and implementation workflow guidance.

## Representative Files

| Instruction | Focus |
| --- | --- |
| [a11y.instructions.md](../instructions/a11y.instructions.md) | Accessible code and UI guidance |
| [agent-safety.instructions.md](../instructions/agent-safety.instructions.md) | Safe governed agent systems |
| [context-engineering.instructions.md](../instructions/context-engineering.instructions.md) | Project structure for stronger Copilot context |
| [prompt.instructions.md](../instructions/prompt.instructions.md) | Authoring `.prompt.md` files |
| [security-and-owasp.instructions.md](../instructions/security-and-owasp.instructions.md) | Secure coding guidance grounded in OWASP |
| [self-explanatory-code-commenting.instructions.md](../instructions/self-explanatory-code-commenting.instructions.md) | Minimal useful commenting style |
| [update-docs-on-code-change.instructions.md](../instructions/update-docs-on-code-change.instructions.md) | Documentation synchronization on code changes |
| [astro.instructions.md](../instructions/astro.instructions.md) | Astro project conventions |
| [nextjs.instructions.md](../instructions/nextjs.instructions.md) | Next.js App Router guidance |
| [svelte.instructions.md](../instructions/svelte.instructions.md) | Svelte and SvelteKit patterns |
| [tailwind-v4-vite.instructions.md](../instructions/tailwind-v4-vite.instructions.md) | Tailwind v4 with Vite configuration |
| [csharp.instructions.md](../instructions/csharp.instructions.md) | General C# development guidance |
| [go.instructions.md](../instructions/go.instructions.md) | Idiomatic Go practices |
| [python-mcp-server.instructions.md](../instructions/python-mcp-server.instructions.md) | Building MCP servers in Python |
| [quarkus.instructions.md](../instructions/quarkus.instructions.md) | Quarkus application conventions |
| [springboot.instructions.md](../instructions/springboot.instructions.md) | Spring Boot base guidance |
| [containerization-docker-best-practices.instructions.md](../instructions/containerization-docker-best-practices.instructions.md) | Docker image and container best practices |
| [playwright-typescript.instructions.md](../instructions/playwright-typescript.instructions.md) | Playwright TypeScript tests |
| [spec-driven-workflow-v1.instructions.md](../instructions/spec-driven-workflow-v1.instructions.md) | Spec-driven execution workflow |
| [task-implementation.instructions.md](../instructions/task-implementation.instructions.md) | Progressive task tracking guidance |
| [taming-copilot.instructions.md](../instructions/taming-copilot.instructions.md) | Guardrails to keep Copilot changes controlled |
| [python-fastapi.instructions.md](../instructions/python-fastapi.instructions.md) | Async FastAPI conventions and dependency injection |
| [rust-web-axum.instructions.md](../instructions/rust-web-axum.instructions.md) | Axum routing, extractors, and SSE streaming |
| [terraform.instructions.md](../instructions/terraform.instructions.md) | Terraform module structure, state, and safe apply workflows |
| [postgres-tuning.instructions.md](../instructions/postgres-tuning.instructions.md) | Indexing, query planning, pooling, and autovacuum |
| [openapi-3-1.instructions.md](../instructions/openapi-3-1.instructions.md) | OpenAPI 3.1 contract-first API design |
| [otel-otelcol.instructions.md](../instructions/otel-otelcol.instructions.md) | OpenTelemetry instrumentation and Collector pipelines |
| [git-conventional-commits.instructions.md](../instructions/git-conventional-commits.instructions.md) | Conventional Commits and changelog automation |
| [github-actions-workflows.instructions.md](../instructions/github-actions-workflows.instructions.md) | GitHub Actions job structure, caching, and secrets handling |

## Directory Notes

- The root [instructions/](../instructions/) folder is the main source of truth.
- For GitHub Copilot, copy the instruction files you need into a target project's `.github/instructions/` on demand — see the [GitHub Copilot integration guide](integrations/github-copilot.md) — rather than expecting a pre-populated mirror in this repo.
- Several instruction files are broad and cross-cutting, while others target specific file patterns or frameworks.

## Browse The Full Library

Open [instructions/](../instructions/) and use file search when you need the complete set.

To add a new instruction file, see the [author-instruction recipe](recipes/author-instruction.md).
