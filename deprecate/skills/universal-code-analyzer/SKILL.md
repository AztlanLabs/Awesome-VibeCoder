---
name: universal-code-analyzer
description: Generate a deterministic repository code map with directory-level and file-level signals. Use when an agent or user needs to find where classes, functions, imports, or local file links live before opening full files, especially in medium or large codebases.
---

# Universal Code Analyzer [DEPRECATED]

> [!WARNING]
> This skill is deprecated and has been moved to the deprecation path.
> It is superseded by [technical-path-indexer](file:///home/crowne/Documents/Documents/VS%20Code/Awesome-VibeCoder/skills/technical-path-indexer/SKILL.md).

Use this skill to scan a repository and emit a compact JSON map that narrows file discovery before deeper code reading. This skill stays passive and stateless. It does not answer implementation questions by itself; it creates the evidence map another agent can use.

## Trigger

Invoke this skill when an agent or user needs repository evidence for:

- where a feature, class, function, or module lives
- which directories are relevant before opening files
- how local source files connect through imports or relative path links
- a first-pass code map before targeted file reads
- large codebases where reading everything would waste context

Keep the name `universal-code-analyzer`. It is action-based and specific enough for automatic discovery.

## In-Scope Behavior

- Scan source-bearing files in a repository.
- Extract directory summaries that show which folders contain relevant code.
- Extract file-level signals such as imports, class-like objects, functions, and local file links.
- Emit deterministic JSON that can be consumed by an agent before it opens source files.

## Out-of-Scope Behavior

- Do not guess architecture or business logic from the map alone.
- Do not read the whole repository when the map already narrows the target files.
- Do not modify product code outside this skill's own toolkit.
- Do not treat the map as the final answer to a user question.

## Inputs

- Repository root path.
- Optional output path for the generated JSON.
- Bundled Python CLI in `./python/main.py`.

## Outputs

The generated JSON must contain:

- `root` - absolute repository root that was scanned
- `directories` - directory-level file counts, extensions, languages, and child folders
- `files` - file-level analysis keyed by repository-relative path

Each file record can contain:

- `extension`
- `language`
- `libraries_used`
- `classes_objects`
- `functions_methods`
- `linked_files`
- `read_error`

## Python Toolkit

- `python/main.py` - scans the repository and writes the JSON code map.

## Standard Workflow

1. Run the analyzer against the repository root.
2. Read the generated JSON.
3. Identify the smallest relevant set of files and directories.
4. Open only those specific files for full reasoning.
5. Form the final answer from the actual files read after the map step.

## Recommended Command

```powershell
Set-Location "d:\Carlos Corona\Documents\VS Code\Awesome-VibeCoder"
python .github/skills/universal-code-analyzer/python/main.py . --output .github/Documentation/_tmp_repo_map.json
```

## Suggested Agent Instruction

Use this policy when wiring the skill into an agent workflow:

> When a user asks a question about a large codebase, run the Universal Code Analyzer first. Read the resulting JSON to understand the relevant directories, classes, functions, and file links. Do not guess where code lives. Use the map to select the exact files you need, then read only those files to answer the question.

## Do NOT

- Do not skip the code-map step for large or unfamiliar repositories.
- Do not answer from the JSON alone when source inspection is still required.
- Do not broaden a focused question into a full-repository read unless the JSON proves the dependency chain requires it.
- Do not invent file ownership, call paths, or runtime behavior that the map does not show.

## Verification Check

Before finishing, confirm all of the following:

- The analyzer created a JSON file successfully.
- The JSON contains both `directories` and `files` sections.
- The chosen follow-up files were selected from repository evidence in the map.
- Any final reasoning was based on the mapped files that were actually opened, not guessed locations.