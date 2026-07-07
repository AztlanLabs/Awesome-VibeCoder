---
description: 'Terraform conventions for infrastructure as code — module structure, state management, and safe apply workflows.'
applyTo: '**/*.tf, **/*.tfvars'
---

# Terraform Instructions

You are an expert DevOps engineer authoring Terraform infrastructure as code.

## State Management

- **MUST**: use a remote backend (S3+DynamoDB, Terraform Cloud, GCS, Azure Storage) with locking enabled — local state files are not safe for any team of more than one person and risk concurrent-apply corruption.
- **MUST NOT**: commit `.tfstate`/`.tfstate.backup` files to version control — they routinely contain secrets (passwords, keys) in plaintext resource attributes.
- **SHOULD**: separate state per environment (dev/staging/prod) via distinct backend keys/workspaces — one shared state file across environments means one bad `apply` can take down all of them.

## Module Structure

- **MUST**: organize reusable infrastructure as modules with explicit `variables.tf` (typed, with descriptions) and `outputs.tf` — a module with untyped `any` variables and no description is undocumented by construction.
- **SHOULD**: keep root modules thin (compose child modules + environment-specific variable values) — push reusable logic down into modules rather than duplicating resource blocks across environments.
- **MUST**: pin module sources to a version/tag (`?ref=v1.2.3`), not a floating branch (`?ref=main`) — an unpinned module source means `terraform init` can pull different code without any diff in your repo.

## Providers & Versions

- **MUST**: pin provider version constraints in `required_providers` (`~> 5.0`, not unconstrained) and commit `.terraform.lock.hcl` — unpinned providers can introduce breaking changes on a routine `init`.
- **SHOULD**: pin the Terraform CLI version itself (`required_version` in the `terraform` block, or a `.terraform-version` file for tfenv) so contributors and CI use the same binary version.

## Plan/Apply Workflow

- **MUST**: run `terraform plan` and have a human (or a required PR check) review the diff before any `apply` against a shared/production environment — never `apply -auto-approve` against prod from a local machine.
- **MUST**: treat any plan showing a resource **replacement** (destroy + create) on a stateful resource (database, volume) as a stop-and-review signal, not something to wave through — replacement means data loss unless a `prevent_destroy`/migration path is in place.
- **SHOULD**: use `terraform plan -out=tfplan` and apply that exact saved plan (`terraform apply tfplan`) in CI, so what was reviewed is exactly what gets applied — re-running `plan` implicitly before `apply` can pick up drift between review and execution.

## Secrets & Sensitive Values

- **MUST**: mark sensitive variables/outputs with `sensitive = true` so they're redacted from CLI output and plan/apply logs.
- **MUST NOT**: hardcode secrets (API keys, passwords) as literal values in `.tf`/`.tfvars` files — source them from a secrets manager (Vault, AWS Secrets Manager, SSM Parameter Store) via a data source instead.

## Safety & Blast Radius

- **SHOULD**: add `prevent_destroy = true` (via `lifecycle`) to resources where accidental deletion is catastrophic (production databases, KMS keys).
- **MUST**: scope IAM/service-account credentials used by CI's Terraform runs to the minimum permissions needed for the resources that stack actually manages — a CI credential with account-wide admin turns any Terraform bug into an account-wide incident.

## Testing & Validation

- **MUST**: run `terraform validate` and `terraform fmt -check` in CI on every PR — catches syntax errors and style drift before a human review cycle.
- **SHOULD**: use `terraform-compliance`, `checkov`, or `tflint` in CI to catch policy violations (public S3 buckets, open security groups) before apply, not after an incident.
