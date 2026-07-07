---
description: 'Conventional Commits specification — commit message structure, types, breaking-change footers, and changelog/semver automation.'
applyTo: '**/.gitmessage, **/COMMIT_EDITMSG, **/CHANGELOG.md'
---

# Conventional Commits Instructions

You are an expert in disciplined commit history, following the Conventional Commits specification.

## Commit Structure

- **MUST**: format every commit as `<type>[optional scope]: <description>` on the first line — this is what makes commit history machine-parseable for changelog generation and semver bumps.
- **MUST**: keep the first line ≤ 72 characters and written in the imperative mood ("add", "fix", "remove" — not "added"/"fixes") — matches the convention Git itself uses for its own commit messages.
- **SHOULD**: add a blank line, then a longer body explaining **why** the change was made when the "what" isn't obvious from the diff — the type+description states what changed; the body should carry the rationale.

## Types

- **MUST**: use `feat` only for commits that add a new feature (triggers a MINOR semver bump) and `fix` only for commits that fix a bug (triggers a PATCH bump) — misusing these types breaks automated semver/changelog tooling that keys off them.
- **SHOULD**: use the other standard types for everything else: `docs` (documentation only), `style` (formatting, no logic change), `refactor` (neither fixes a bug nor adds a feature), `perf` (performance improvement), `test` (adding/correcting tests), `build` (build system/dependencies), `ci` (CI configuration), `chore` (maintenance with no production code change).
- **MUST NOT**: use `feat`/`fix` for commits that only touch tests, docs, or CI config — that miscategorizes the change for anyone generating a changelog or deciding the next version bump from commit types.

## Scope

- **SHOULD**: add a parenthetical scope naming the affected module/component (`feat(auth): add refresh-token rotation`) when the repo has clearly separable areas — omit it for changes that are genuinely repo-wide.
- **MUST**: keep scope names consistent across the repo's history (pick a fixed vocabulary — e.g. actual directory/package names) rather than inventing a new scope name per commit for the same area.

## Breaking Changes

- **MUST**: mark a breaking change either with `!` after the type/scope (`feat(api)!: remove deprecated v1 endpoints`) or a `BREAKING CHANGE:` footer (or both) — this is the one signal automated tooling uses to trigger a MAJOR version bump; a breaking change without this marker will ship as a MINOR/PATCH release and surprise consumers.
- **MUST**: describe what breaks and the migration path in the `BREAKING CHANGE:` footer body — a bare `!` with no explanation leaves downstream consumers to reverse-engineer the break from a diff.

## Footers

- **SHOULD**: reference the issue/ticket the commit addresses in a footer (`Refs: #123`, `Closes: #123`) rather than only in the PR description — commit-level references survive squash-merges and rebases better than PR metadata does.
- **MUST**: use one footer token per line, `Token: value` or `Token #value` format, per the spec — free-form footer text breaks automated parsers looking for specific tokens.

## Automation

- **SHOULD**: wire a commit-lint check (`commitlint` + `@commitlint/config-conventional`) into CI or a pre-commit/pre-push hook so malformed commits are caught before merge, not discovered when changelog generation breaks.
- **SHOULD**: generate `CHANGELOG.md` entries and the next semver version from commit history (`semantic-release`, `standard-version`, or equivalent) rather than hand-writing both — hand-written changelogs drift from actual commit history over time.
- **MUST NOT**: squash-merge a PR's commits into a single non-conventional message if the repo relies on per-commit conventional format for changelog generation — either enforce conventional format on the squashed message, or generate the changelog from PR titles instead, consistently.

## Reverts

- **MUST**: use `revert: <description of the original commit>` with a footer referencing the original commit's SHA — this keeps revert commits linkable to what they undo, both for humans and automated tooling.
