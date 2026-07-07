# Bug Triage Workflow

Triage a reported bug from intake to verified fix, with the minimum roles needed to (1) confirm the root cause, (2) produce a safe patch, (3) verify the fix, and (4) ship it. This is a **short, incident-style** workflow — it is not a substitute for the full SDLC sequential workflow.

## When to Use

- A user, QA, monitoring, or a customer files a bug report.
- A regression appears after a deploy and you need a tight, evidence-gated fix loop.
- A non-trivial defect enters the backlog and needs a triage owner before being scheduled.

Skip this workflow for trivial typos, single-line config changes, or cosmetic fixes — those go straight to **Developer** and then **QA Tester**.

## Prerequisites

- A bug report in `.sdlc/tasks/` (or a new task created during intake) with: summary, reproduction steps, expected vs actual, severity, environment.
- The `.sdlc/` workspace initialized (via `sdlc-orchestrator` or any SDLC agent's first-run scaffold).
- Access to the running system (logs, traces, or a reproducible test environment).

## Role Sequence

> **Context Researcher → Cybersecurity Architect (if security) → Developer → QA Tester → DevOps Engineer**

| Step | Agent | Goal | Gate (must be true to advance) |
|---|---|---|---|
| 1 | **Context Researcher** | Produce an evidence-backed root-cause analysis: what changed, where, why, exact files/lines. | `.sdlc/tasks/<bug-id>.md` has a "Root Cause" section with file paths, line numbers, and the failing command/log excerpt. |
| 2 | **Cybersecurity Architect** *(only if the bug touches auth, secrets, PII, payments, public input, or a known CVE class)* | Threat-model the affected surface; define security constraints the fix must satisfy. | A short security note appended to the task with the threat class and required controls (e.g. "no new public endpoint", "must rotate key X"). Skip otherwise. |
| 3 | **Developer** | Implement the fix in the source tree; add or update a failing test that reproduces the bug. | A real build + test run cited in `.sdlc/progress.md` (e.g. `npm test — 1 failed, 2 passed → 3 passed after fix`). No `COMPLETED` without a command output. |
| 4 | **QA Tester** | Verify the fix, exercise the original repro, run regression suite, confirm no collateral damage. | The original repro is green; regression suite passes; coverage did not drop below the project threshold. Evidence in `.sdlc/progress.md`. |
| 5 | **DevOps Engineer** | Ship the fix — merge, deploy, monitor the canary, confirm the error-rate / SLO metrics recover. | Deployment pipeline run cited; canary metrics (error rate, latency, saturation) are within budget; rollback plan recorded. |

## Detailed Steps

### 1. Context Researcher — Root Cause

- Read the bug report and any attached logs, traces, screenshots, or repro steps.
- Read `.sdlc/architecture.md`, `.sdlc/contracts/api-contracts.md`, `.sdlc/memory.md`, and the most recent `.sdlc/decisions/` to understand the surrounding context.
- Use the [`context-researcher`](../skills/context-researcher/SKILL.md) skill to produce a structured investigation.
- **Output**: a "Root Cause" section in the bug task file with:
  - The exact file(s) and line(s) implicated.
  - The commit/PR that introduced the defect (if known).
  - The failing command, log excerpt, or stack trace that proves the cause.
  - A short list of plausible contributing factors (kept terse — one bullet per factor).

> **If the root cause is not reproducible in step 1, stop and ask the reporter for a more detailed repro.** Do not proceed to a fix on speculation.

### 2. Cybersecurity Architect — Security Gate (conditional)

Run this step **only if** the bug falls into one of these classes:

- Authentication, authorization, or session handling.
- Secret, token, key, or credential exposure.
- PII, payment, or regulated-data handling.
- Public-facing input validation (XSS, SQLi, SSRF, path traversal, deserialization).
- Known CVE class or vulnerable dependency.

Otherwise, **skip to step 3**.

- Threat-model the affected surface using STRIDE.
- **Output**: a "Security Constraints" section in the bug task file listing the controls the fix must satisfy. The constraints become acceptance criteria for steps 3 and 4.

### 3. Developer — Fix

- Read the root-cause section, the security constraints (if any), and the API/data contracts.
- Implement the fix in the project's source tree — do not just describe it.
- Add or update a **failing test first** that reproduces the bug, then make it pass.
- Run the project's build, lint, and test commands. Cite the real output in `.sdlc/progress.md`.
- **Output**: a "Fix" section in the bug task with the changed files, the test added, and the build/test output.

> **Definition of Done (step 3)**: a real command output showing the failing test → passing test transition; no `TODO` left behind; no unrelated files modified.

### 4. QA Tester — Verify

- Run the original repro from the bug report — must be green.
- Run the full regression suite relevant to the affected area.
- Check for collateral damage: the fix must not break adjacent tests, must not regress performance budgets, must not violate the security constraints from step 2.
- **Output**: a "Verification" section in the bug task with the commands run, pass/fail counts, and any caveats.

> **If verification fails, return to step 3** with a new failing-test note. Do not mark the task complete.

### 5. DevOps Engineer — Ship

- Merge the fix (or open the PR if the team requires review).
- Trigger the deploy pipeline to a canary / staging environment first.
- Monitor the canary for the metrics most likely to regress (error rate, p99 latency, saturation).
- Promote to production only when canary metrics are within budget.
- Record the deploy timestamp, the metrics observed, and the rollback plan in `.sdlc/progress.md`.

> **Definition of Done (step 5)**: production metrics for the affected surface are within SLO budget; rollback plan is recorded and rehearsed; the original bug is verified fixed in production (e.g. via a synthetic probe or a closed alert).

## Definition of Done (workflow-level)

The bug is considered triaged and resolved when **all five** conditions hold:

1. Root cause is documented in the task with file paths + line numbers.
2. (If security-relevant) security constraints are recorded and satisfied.
3. A real build + test command output is cited in `.sdlc/progress.md` showing the failing → passing transition.
4. QA verification ran the full relevant regression suite — green, evidence cited.
5. The fix is deployed and production metrics confirm the defect is closed.

## Customization

- **Skip step 2** for non-security bugs (default).
- **Insert a step between 3 and 4** for a Code Reviewer review if the project policy requires it.
- **Insert a step between 4 and 5** for a Responsible AI review if the bug touches a model-driven or accessibility-sensitive surface.
- **Loop steps 3 → 4** as many times as needed; never skip the verification step.

## Related

- [`workflows/sdlc-sequential.workflow.md`](sdlc-sequential.workflow.md) — for full-feature delivery (not bug-fix).
- [`workflows/sdlc-parallel.workflow.md`](sdlc-parallel.workflow.md) — for parallel workstreams.
- [`agents/context-researcher.agent.md`](../agents/context-researcher.agent.md) — root-cause analysis agent.
- [`skills/context-researcher/SKILL.md`](../skills/context-researcher/SKILL.md) — context research skill.
