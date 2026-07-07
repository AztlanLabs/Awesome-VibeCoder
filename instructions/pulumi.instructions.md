---
description: 'Pulumi conventions for infrastructure as code in general-purpose languages — stack/project structure, state, and secrets.'
applyTo: '**/*.ts, **/*.py, **/*.go, **/Pulumi.yaml, **/Pulumi.*.yaml'
---

# Pulumi Instructions

You are an expert DevOps engineer authoring infrastructure as code with Pulumi.

## Project & Stack Structure

- **MUST**: use one Pulumi stack per environment (dev/staging/prod) within a project rather than branching resource logic on an if/else for environment inside a single stack — stacks give you isolated state and config, use them for that isolation.
- **SHOULD**: factor reusable infrastructure into Pulumi **component resources** (a class extending `ComponentResource`) rather than copy-pasting the same group of resources across projects — this is Pulumi's equivalent of a Terraform module and gets you a single logical node in the resource graph.
- **MUST**: keep environment-specific values in stack config (`Pulumi.<stack>.yaml`, via `pulumi config set`) — not hardcoded or branched in program logic.

## State Management

- **MUST**: use a managed backend (Pulumi Cloud) or a self-hosted one (S3, GCS, Azure Blob) with encryption — never a local-only backend for anything beyond individual experimentation.
- **MUST NOT**: hand-edit stack state; use `pulumi state`/`pulumi import`/`pulumi refresh` commands for any state surgery — manual JSON edits to exported state routinely desync it from reality.
- **SHOULD**: run `pulumi refresh` before a `pulumi up` when drift is suspected (manual console changes, another process) so the plan reflects real infrastructure, not stale state.

## Secrets

- **MUST**: use `pulumi config set --secret` for sensitive values — Pulumi encrypts these at rest in the stack config and redacts them from CLI output/logs; a plain `config set` does not.
- **MUST NOT**: pass secrets as plain string literals in program code — read them via `pulumi.Config().requireSecret(...)` (or the language equivalent) so they flow through Pulumi's secret-tracking and get marked secret on any resource output that includes them.

## Type Safety & Language Idioms

- **SHOULD**: lean on the host language's type system (TypeScript interfaces, Python dataclasses, Go structs) for resource inputs — this is Pulumi's main advantage over HCL: use it, don't write stringly-typed config that throws away the benefit.
- **MUST**: use `pulumi.Output<T>`/`Output.apply()` (or the language equivalent) to derive values from resource outputs — never assume a resource's output value is available synchronously at program-authoring time; it's only resolved during the actual deployment.

## Preview/Update Workflow

- **MUST**: run `pulumi preview` and require review before `pulumi up` against any shared/production stack — treat preview output with the same scrutiny as a Terraform plan diff.
- **MUST**: treat any preview showing a resource **replacement** on a stateful resource (database, persistent volume) as a stop-and-review signal — Pulumi's replace-vs-update distinction has the same data-loss risk as Terraform's.
- **SHOULD**: use `--diff` on `pulumi preview`/`pulumi up` in CI output so reviewers see property-level changes, not just resource-level "update" summaries.

## Safety & Blast Radius

- **SHOULD**: apply `protect: true` on resources where accidental deletion is catastrophic (production databases, critical buckets) — Pulumi will refuse to delete a protected resource until the option is explicitly removed.
- **MUST**: scope the cloud credentials used by CI's Pulumi runs to the minimum permissions the stack actually needs.

## Testing

- **SHOULD**: use Pulumi's unit-testing mode (mocking resource creation) to assert on resource configuration (e.g. "this S3 bucket must not be public") without provisioning real infrastructure.
- **MUST**: run policy-as-code checks (Pulumi CrossGuard, or an equivalent OPA/Sentinel-style policy pack) in CI for compliance-sensitive resources (public network exposure, encryption-at-rest) before `pulumi up` against production.
