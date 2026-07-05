---
name: context-researcher
description: 'Investigate code, bugs, GitHub issues, error traces, or any topic the user names, gather evidence across the repository (exact files, line ranges, git history, related tests, dependencies, prior art), and produce a structured research file that pinpoints root causes, where changes must go, and open risks. Use when the user asks to research, investigate, analyze, root-cause, or "look into" something before writing code, or explicitly requests a research/investigation report.'
---

# Context Researcher

Use this skill to run an evidence-based investigation of a piece of code, a bug, a GitHub issue, an error message, or any topic the user names, and to produce a standalone **research file** that other agents or humans can act on directly. This skill only researches and documents evidence — it never edits product code and never implements the fix it points to.

## Trigger Conditions

Invoke this skill when:

- The user asks to "research", "investigate", "look into", "root-cause", "figure out", or "analyze" a bug, error, issue, or unfamiliar area of the code before any fix is written.
- The user pastes an error message, stack trace, failing test output, or GitHub issue and wants to know what is going on and where it comes from.
- The user references a GitHub issue/PR number or URL and wants a structured breakdown.
- A task is too ambiguous or too large to safely implement without first mapping evidence, root cause, and exact edit points.

## Centralized State Architecture (Optional)

If a `.sdlc/` workspace state directory exists, read `.sdlc/activeContext.md` first to avoid duplicating an investigation already in progress, and append a one-line pointer to the produced research file at the end of `.sdlc/activeContext.md` using the append-only pattern after saving it. Skip this entirely when `.sdlc/` is absent — this skill works standalone in any repository and never requires `.sdlc/` to function.

## Core Capabilities

- Reproduce or explain the reported issue from evidence (logs, stack traces, failing tests, error messages) rather than assumption.
- Trace root cause across files, functions, and call sites using search and read tools, not guesses.
- Pin every finding to a concrete `path#Lstart-Lend` reference confirmed by actually reading that file.
- Trace relevant history via `git log` / `git blame` when it changes the diagnosis (for example, a recent regression).
- Identify every file and exact line range a subsequent fix or feature would need to touch, without writing the fix itself.
- Surface related tests, callers, and dependents that could be impacted by a future change.
- Cross-reference related GitHub issues/PRs and prior art in the repository (similar past fixes, existing conventions to mirror).
- Flag unknowns explicitly instead of filling gaps with speculation.

## Inputs

- `${input:topic}` — the code area, bug report, error message, GitHub issue/PR reference, or free-form question to research.
- Optional: a stack trace, log snippet, failing test name, or reproduction steps.
- Optional: a scope hint (folder, package, or service) to bound the investigation.

## Outputs

Write a single research file to:

```text
.github/Documentation/research/<YYYY-MM-DD>-<kebab-case-slug>.research.md
```

using this structure:

```markdown
# Research: <Title>

## Summary
One-paragraph, plain-English answer to the research question.

## Question / Problem Statement
What was asked, plus reproduction steps or the exact error/stack trace if applicable.

## Investigation Log
Ordered bullet list of what was inspected and why (files read, searches run, commands executed).

## Root Cause (or Current Understanding)
Evidence-backed explanation. State "Needs confirmation" explicitly if not fully proven.

## Affected Files & Lines
| File | Lines | Why it's relevant | Suggested change (not implemented) |
|---|---|---|---|

## Related Code & Tests
- Callers / dependents of the affected code.
- Existing tests that already cover this area.
- Similar past fixes or conventions in the repo worth mirroring.

## Related Issues / PRs / External References
Links plus a one-line note on why each is relevant.

## Risks & Unknowns
Explicit list of what is uncertain, needs confirmation, or has edge cases not yet verified.

## Recommended Next Steps
Ordered, actionable recommendations for what to change and where — not a diff or implementation.
```

## Workflow

1. Restate the research target as one concrete question or reproduction scenario.
2. If a GitHub issue/PR/URL was given, fetch and read it before searching the repository.
3. Search the repository broadly first (keyword and semantic search), then narrow to the exact files involved.
4. Read every file that looks relevant and confirm exact line ranges — never estimate a line number.
5. When a stack trace, failing test, or repro steps exist, use them to trace the actual call path through the code.
6. Use `git log` / `git blame` when recent history changes the diagnosis (for example, a suspected regression).
7. Identify dependents, callers, and existing tests that touch the affected area.
8. Cross-reference related issues/PRs and existing repository conventions or prior fixes.
9. Assemble findings into the research file using the output contract above, saved at `.github/Documentation/research/<date>-<slug>.research.md`.
10. Report the file path and a concise summary back to the requester.

## Do Not

- Do not modify, create, or delete any product/source/test file — only the research file itself.
- Do not implement the fix, refactor, or feature. Only document where and what should change.
- Do not guess line numbers or file paths; verify every reference by reading the file in this session.
- Do not fabricate GitHub issues, commits, authors, or history.
- Do not create a second research file for the same investigation — update the existing one in place when the user asks for follow-up on the same topic.

## Verification Check

Before finishing, confirm all of the following:

- [ ] Every "Affected Files & Lines" entry cites a real path and line range confirmed by reading the file.
- [ ] The root cause is evidence-backed, or explicitly marked "Needs confirmation".
- [ ] Related tests and dependents were actually searched for, not assumed absent.
- [ ] No product code was modified.
- [ ] The research file was saved at `.github/Documentation/research/` and its path was reported back.
