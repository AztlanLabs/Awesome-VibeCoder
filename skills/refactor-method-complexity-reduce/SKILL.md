---
name: refactor-method-complexity-reduce
description: 'Refactor given method `${input:methodName}` to reduce its cognitive complexity to `${input:complexityThreshold}` or below, by extracting helper methods.'
---

# Refactor Method to Reduce Cognitive Complexity

Use this skill to refactor a target method that has excessive cognitive complexity (nested loops, arrow code, deep conditions) into smaller, more readable helper methods.

## Trigger Conditions

Invoke this skill when:
- The cognitive complexity of `${input:methodName}` is measured or suspected to be above `${input:complexityThreshold}`.
- A method contains too many nested conditionals, loops, repeated code patterns, or mixed concerns.
- A user or warning suggests simplifying method complexity to improve testability and maintainability.

## Centralized State Architecture

On startup, verify the `.sdlc/` workspace state directory. Load the shared state baseline and record all complexity reduction progress inside `.sdlc/progress.md`.

1. Read `.sdlc/systemPatterns.md` to ensure extracted helpers conform to the project's coding standards.
2. Check `.sdlc/tasks/` for the task card corresponding to this refactoring work.
3. Update the task card status and log an entry under the progress section describing the old vs. new complexity metrics.
4. Append a brief completion notice to `.sdlc/progress.md`.

## Core Capabilities

- **Cognitive Complexity Reduction**: Simplify nested control structures and boolean conditions.
- **Helper Extraction**: Isolate validation logic, case handlers, and specific calculations into dedicated, single-responsibility helper methods.
- **Incremental Refactoring**: Structure step-by-step extractions that keep the codebase compilable and testable at each step.

## Inputs & Outputs

### Inputs
- `${input:methodName}`: The exact name of the method to refactor.
- `${input:complexityThreshold}`: The target complexity threshold (typically ≤ 10).

### Outputs
- A refactored primary method orchestrating smaller helper methods.
- A set of newly extracted helper methods with clear, single responsibilities.

---

## Boundaries & Guardrails

- **MANDATORY Test Verification**: After refactoring, you MUST run the test suite and verify that the results explicitly state `"failed=0"`. Never assume tests pass. If any failures are found, you must analyze and fix the regression.
- **Functional Equivalence**: Retain all error handling, validation checks, parameter boundaries, and exception types. Do not change observable runtime behavior.
- **Helper Scoping**: Keep helper methods private, static, or local when they do not require instance state.

---

## Verification Checklist

Before completing the refactoring task, verify that:
- [ ] The refactored code compiles successfully with no new warning diagnostics.
- [ ] **Test suite execution has been run and output explicitly verified to show "failed=0"**.
- [ ] Cognitive complexity of the main method is at or below the target `${input:complexityThreshold}`.
- [ ] Extracted helper methods have descriptive, single-purpose names.
- [ ] No duplicate logic or dead code blocks remain in the refactored files.
