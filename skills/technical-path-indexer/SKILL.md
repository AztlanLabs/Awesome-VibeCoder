---
name: technical-path-indexer
description: Scan repository paths, extract routes and cross-file links, and emit deterministic technical path indexes. Use when an agent needs deterministic path intelligence before auditing, planning, or rendering a technical path document.
---

# Technical Path Indexer

Use this skill to scan a repository and emit a deterministic technical path index. This skill stays passive and stateless. It does not write architecture guidance, implementation plans, or general documentation.

## Trigger

Invoke this skill when an agent or user needs repository evidence for:

- important folders and files
- runtime routes or path declarations
- imports, references, or cross-file links
- companion-file relationships such as markup-to-code-behind or script-to-style pairs
- weighted file and path rankings that show indexing relevance

Keep the name `technical-path-indexer`. It is already specific, action-based, and semantically distinct.

## In-Scope Indexing Behavior

- Scan repository folders and normalize the file inventory.
- Extract runtime paths and route declarations from repository evidence.
- Trace file-to-file references such as imports, markdown links, manifest references, and explicit path literals.
- Detect repository-evident companion-file conventions such as `*.aspx` to `*.aspx.cs`, `*.razor` to `*.razor.cs`, `*.xaml` to `*.xaml.cs`, and same-stem script, style, markup, or test companions.
- Emit structured indexing output that another agent can consume.

## Adjacent But Still Index-Derived Behavior

- Compare a fresh index to an existing baseline when the invoking agent supplies one.
- Batch large repositories path by path so the agent can scan, extract, and emit findings incrementally.
- Mark missing repository evidence as `Needs confirmation` when the structured scan output is incomplete and manual validation is required.

## Out-of-Scope Behavior

- Do not generate implementation plans, architecture summaries, or generic documentation.
- Do not choose execution modes for an agent.
- Do not rewrite or own `.github/Documentation/<normalized-project-name>_technical_paths.md` as a primary responsibility.
- Do not modify product code.
- Do not guess route ownership, path purpose, or linkage intent.

The existing Repository Path Auditor agent already owns mode selection, canonical markdown output, and selective document updates. No sibling split is required for those responsibilities.

## Inputs

- Project root, or the project root explicitly provided by the user.
- Optional scoped audit targets: one or more folders, files, or code paths the user wants indexed deeply.
- Optional baseline findings or canonical document content supplied by the invoking agent for comparison.
- Companion Python toolkit in `skills/technical-path-indexer/python/`, when the workspace exposes the root skill collection.

## Outputs

- Structured, evidence-backed indexing findings with these sections:
   - repository root and scan scope
   - path batches
   - normalized file inventory with only file path, language, and size
   - directory or path batches
   - routes and runtime path declarations
   - linked-file groups
   - skipped file paths
- The current CLI contract does not emit standalone `references`, `file_scores`, `path_scores`, or `unresolved` sections.
- Optional stale-versus-current comparison findings when a baseline is supplied.

## Python Toolkit

The bundled Python indexers provide the mechanics this skill can rely on:

- `python/repository.py` — discover paths, normalize file records, and classify entrypoints or config files.
- `python/routes.py` — extract repository routes with framework-specific filesystem heuristics and content-based route patterns.
- `python/references.py` — trace imports, markdown links, manifest references, explicit file-path literals, and unresolved local references for validation workflows.
- `python/linked_files.py` — detect explicit companion-file conventions and same-stem related files.
- `python/scoring.py` — optional helper module for evidence-based weighting experiments; it is not part of the current emitted CLI contract.
- `python/pipeline.py` — orchestrate scoped batches, compose structured results, and surface skipped outputs in the current CLI contract.
- `python/cli.py` — run the pipeline from the command line with explicit scope and batch controls.

## What To Extract

Prioritize high-signal repository evidence:

1. Project entrypoints: app bootstrap, main programs, top-level routes, public exports.
2. Structural folders: API, UI, backend, shared libraries, config, tests, scripts, docs.
3. Route and runtime path definitions: controllers, routers, pages, endpoints, CLI commands, filesystem routes.
4. Cross-file relationships: imports, exports, config usage, test-to-source linkage, prompt-to-skill linkage, explicit path references.
5. Companion-file patterns: code-behind pairs, script-style pairs, script-markup pairs, lockfile companions, and other repository-evident same-stem links.

## Link Patterns This Skill Indexes

Index these relationship classes when repository evidence or explicit pattern rules support them:

- `*.aspx` with `*.aspx.cs`, `*.aspx.vb`, or `*.designer.cs`
- `*.razor` with `*.razor.cs` or `*.razor.css`
- `*.xaml` or `*.axaml` with `*.xaml.cs`, `*.xaml.vb`, or `*.axaml.cs`
- same-stem script files with style, markup, test, spec, or story companions such as `Component.tsx` with `Component.css` or `Component.test.tsx`
- configuration-to-runtime companions such as `package.json` with lockfiles or `Dockerfile` with compose files when both exist in repository evidence
- markdown or manifest path references that explicitly link one repository file to another

## Framework-Specific Route Heuristics

Split filesystem routing by framework instead of using a single generic folder rule:

- Next.js app router files such as `app/**/page.*` and `app/**/route.*`
- Next.js pages router files such as `pages/**/*.tsx` and `pages/api/**/*.ts`
- SvelteKit route files such as `src/routes/**/+page.*` and `src/routes/**/+server.*`

Treat framework support files such as `layout`, `loading`, `error`, `not-found`, `_app`, and `_document` as skipped evidence, not route owners.

## Large-Repository Batch Rules

When the repository contains multiple deployable applications, packages, or bounded contexts, index the repository in deterministic batches instead of flattening the whole tree at once.

Batch in this order:

1. Scan the main paths first and build a tree-style map of the repository root.
2. Select the first high-signal path batch.
3. Read the files inside that batch and extract only the evidence needed to explain what each file is, what it does, what it links to, and which developer questions it can answer.
4. Emit findings for that batch before moving to the next path batch.
5. Repeat until all required batches are complete.

If a category is absent, say so explicitly instead of inventing placeholders.

## Anti-Redundancy Rules

- Do not enumerate every file in large repetitive folders.
- Read representative files when a folder clearly follows a stable pattern.
- Prefer grouped summaries such as `controllers/*.ts` or `pages/*` when they communicate the pattern better than raw inventories.
- Expand to file-level detail only when a file is an entrypoint, defines a route, owns configuration, acts as a pattern reference, or has strong linkage centrality.

## Workflow

1. Determine the project root and optional audit scope.
2. Run a tree-first scan of the top-level repository paths.
3. Normalize the file inventory for the current scope.
4. Extract routes and runtime path declarations from the current batch.
5. Extract file-to-file references from the current batch.
6. Detect companion-file links supported by repository evidence or explicit pattern rules.
7. Compute evidence-based file and path weights for the current batch.
8. Emit structured findings for the current batch.
9. Repeat steps 4 through 8 for the next required batch until the scoped scan is complete.
10. If a baseline is supplied, compare the fresh findings to that baseline and report the delta without guessing.

## Do NOT

- Do not modify product code.
- Do not create architecture summaries, implementation plans, or generic repository guides.
- Do not invent path purposes, route ownership, or linkages that are not supported by repository evidence.
- Do not widen a user-scoped audit into unrelated project areas unless the relationship is required to explain the requested scope.
- Do not claim a file relationship unless a repository edge or explicit pattern rule supports it.

## Structured Output Shape

Emit results in a machine-readable shape the invoking agent can consume. The representation can be JSON or an equivalent structured object, but it must contain these sections:

- `root`
- `scope`
- `batches`
- `files`
- `directories`
- `routes`
- `linked_files`
- `skipped_files`

## Recomendations For New Agents
This is an example of how a new agent could invoke this skill:
Run with next args:
```bash
PS D:\Carlos Corona\Documents\VS Code\Awesome-VibeCoder> Set-Location "d:\Carlos Corona\Documents\VS Code\Awesome-VibeCoder"; python .github/skills/technical-path-indexer/python/cli.py . --pretty --output .github/Documentation/_tmp_technical_index.json; Test-Path .github/Documentation/_tmp_technical_index.json
```

Providing the path to the repository root, optional scope, and output location for the structured findings. The agent can then consume the emitted JSON to inform its next steps in auditing, planning, or documentation.
Giving where the output is stored allows the agent to read it back in for comparison, delta reporting, or as evidence for downstream tasks.

## Application Rules

- The invoking agent decides whether findings stay as structured data, become a delta report, or are rendered into canonical markdown.
- Preserve unchanged evidence when a comparison baseline is supplied.
- Mark uncertain areas as `Needs confirmation` instead of guessing.
- For large multi-project repositories, prefer project-level path batches over file-by-file dumps.

## Verification Check

Before finishing, confirm all of the following:

- The skill remained passive, stateless, and indexing-only.
- Scope stayed centered on any user-provided target paths or files.
- Every emitted route, reference, or linked-file relationship is backed by repository evidence or an explicit pattern rule.
- Findings were derived from observable repository evidence such as entrypoints, routes, companion-file links, and directory structure.
- Repetitive folders were summarized by pattern unless a file-level reference was required.
- Uncertain areas are marked explicitly instead of guessed.
- No product code or unrelated documentation files were modified.