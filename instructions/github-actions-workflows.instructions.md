---
description: 'GitHub Actions workflow conventions — job structure, caching, secrets handling, and reusable workflows.'
applyTo: '**/.github/workflows/*.yml, **/.github/workflows/*.yaml'
---

# GitHub Actions Workflow Instructions

You are an expert DevOps engineer authoring GitHub Actions CI/CD workflows.

## Triggers & Scoping

- **MUST**: scope `on:` triggers precisely (`pull_request: { branches: [main] }`, `push: { paths: [...] }`) rather than running every workflow on every push to every branch — an unscoped trigger wastes CI minutes and slows feedback with irrelevant runs.
- **SHOULD**: use `paths`/`paths-ignore` filters so a docs-only or unrelated-directory change doesn't trigger an expensive build/test/deploy pipeline.
- **MUST**: use `concurrency` groups (keyed on branch/PR) with `cancel-in-progress: true` for CI workflows — without it, pushing multiple commits to the same PR queues redundant runs instead of cancelling superseded ones.

## Jobs & Steps

- **SHOULD**: split independent concerns (lint, unit test, build, integration test) into separate jobs that run in parallel rather than one long sequential job — parallel jobs cut wall-clock time and isolate failures to a specific concern.
- **MUST**: pin third-party actions to a full commit SHA (`actions/checkout@<sha>`), not just a floating tag (`@v4`) — a tag can be moved by the action's maintainer (or an attacker who compromises their account) to point at different code; a SHA cannot.
- **SHOULD**: use a reusable workflow (`workflow_call`) for a pipeline shared across multiple repos/branches, rather than copy-pasting the same job definitions — a reusable workflow gets a single point of update.

## Caching & Performance

- **MUST**: cache package manager dependencies (`actions/cache`, or the built-in cache support in `setup-node`/`setup-python`/etc.) keyed on the lockfile hash — reinstalling dependencies from scratch on every run wastes minutes and adds unnecessary network dependency to CI.
- **SHOULD**: cache build outputs (compiled artifacts, Docker layers via `docker/build-push-action`'s cache options) when the build step is a significant fraction of total job time.
- **MUST**: set a `timeout-minutes` on every job — a hung job (waiting on a network call, an interactive prompt) without a timeout burns CI minutes indefinitely until someone notices and cancels it manually.

## Secrets & Permissions

- **MUST**: set the workflow/job's `permissions:` block to the minimum needed (e.g. `contents: read` for a build job) rather than relying on the default token's broader permissions — GitHub's default `GITHUB_TOKEN` permissions are broader than most jobs need.
- **MUST NOT**: echo/print secrets to logs, and be aware that a secret embedded in a constructed string (e.g. a URL with an API key) can still leak in `set -x`/debug-mode log output — use `::add-mask::` or the secret directly in an env var passed to the tool, not string-interpolated into a logged command.
- **MUST**: avoid using secrets in workflows triggered by `pull_request_target` from forks without careful review — that trigger runs with the base repo's secrets against the fork's (potentially malicious) code, a well-known supply-chain attack vector.

## Matrix Builds

- **SHOULD**: use a `strategy.matrix` for testing across multiple versions/platforms (Node versions, OS) rather than duplicating near-identical job definitions.
- **MUST**: set `fail-fast: false` when matrix legs are meant to report independently (e.g. testing against multiple Node LTS versions) — the default `fail-fast: true` cancels all other matrix legs the moment one fails, hiding whether the others would have passed.

## Artifacts & Outputs

- **SHOULD**: upload build/test artifacts (`actions/upload-artifact`) with a retention period matched to their actual usefulness (short for routine CI logs, longer for release binaries) — unbounded retention accumulates storage cost for artifacts nobody will look at.
- **MUST**: pass data between jobs via explicit `outputs`/artifacts, not by assuming shared filesystem state — each job runs on a fresh runner with no state from prior jobs unless explicitly passed.

## Deployment Workflows

- **MUST**: gate production-deploying jobs behind a GitHub Environment with required reviewers (or an equivalent manual approval step) — a workflow that auto-deploys to production on every merge to main needs an explicit, reviewed decision to be safe, not an accident of trigger configuration.
- **SHOULD**: make deploy jobs idempotent and support re-running them safely — a deploy workflow that can't be safely retried after a transient failure turns every flaky step into a manual incident.
