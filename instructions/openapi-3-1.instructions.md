---
description: 'OpenAPI 3.1 specification conventions — JSON Schema alignment, versioning, and contract-first API design.'
applyTo: '**/openapi.yaml, **/openapi.yml, **/openapi.json, **/*.openapi.yaml, **/*.openapi.json'
---

# OpenAPI 3.1 Instructions

You are an expert API designer authoring OpenAPI 3.1 specifications as the contract-first source of truth for an API.

## JSON Schema Alignment

- **MUST**: use OpenAPI 3.1's full JSON Schema 2020-12 support (`type` as an array for nullable, `prefixItems`, `const`, `if`/`then`/`else`) rather than 3.0-era workarounds (`nullable: true`) — 3.1 dropped the custom-subset restrictions 3.0 had.
- **SHOULD**: define reusable schemas under `components/schemas` and reference them (`$ref`) from every operation that shares a shape — a spec with the same object shape inlined in five places will drift the moment one gets updated and the others don't.
- **MUST**: mark every property that is actually required with the schema's `required` array — an overly-permissive schema (everything optional) produces client code that under-validates and null-checks everywhere.

## Versioning

- **MUST**: pick one versioning strategy (URL path prefix `/v1/`, a custom header, or content negotiation via `Accept`) and apply it consistently across every operation in the spec — mixing strategies within one API confuses both client generators and consumers.
- **MUST**: document deprecation explicitly with `deprecated: true` on the operation/schema plus a `Sunset` header convention described in the spec's description field — don't silently remove a field/operation without a deprecation window visible in the contract.
- **SHOULD**: keep breaking changes (removing a field, changing a type, tightening a required constraint) to a new major version; additive changes (new optional field, new endpoint) can go into the current version.

## Operations & Paths

- **MUST**: give every operation an `operationId` — client-code generators use it to name generated methods, and a spec without it produces unreadable generated method names.
- **MUST**: document every realistic response status code per operation (not just `200`), including error responses, with a schema for each — a spec that only documents the happy path is not a usable contract for error handling.
- **SHOULD**: use `parameters` with explicit `in: query`/`in: path`/`in: header` and `required`/`schema` for every input — avoid describing parameters only in the operation's free-text `description`.

## Error Responses

- **MUST**: define a single, reusable error schema (e.g. RFC 7807 `problem+json`: `type`, `title`, `status`, `detail`, `instance`) referenced from every operation's non-2xx responses — a different error shape per endpoint means every client needs per-endpoint error-handling code.
- **SHOULD**: enumerate stable, machine-readable error codes (not just HTTP status + a human message) in the error schema so clients can branch on error type without string-matching a message.

## Pagination

- **SHOULD**: document cursor-based pagination (`cursor`/`next_cursor` query/response params) as the default for list endpoints over offset-based (`page`/`limit`) — cursor pagination is stable under concurrent inserts/deletes; offset pagination is not.
- **MUST**: document the pagination response envelope's shape (items array + cursor/metadata) as a reusable schema, not ad hoc per list endpoint.

## Security

- **MUST**: declare `securitySchemes` (OAuth2, API key, bearer JWT) at the components level and reference them via `security` on operations that require auth — don't leave authentication undocumented and only described in prose elsewhere.
- **SHOULD**: scope security requirements per-operation (not just globally) when different endpoints require different scopes/roles — a global blanket security requirement hides which operations need elevated permissions.

## Validation & Tooling

- **MUST**: lint the spec in CI (Spectral, `openapi-cli validate`, or equivalent) — a spec with `$ref` errors or schema violations that only gets caught by a human reading it will drift.
- **SHOULD**: generate client/server stubs (or at least type definitions) from the spec rather than hand-writing them separately — a hand-maintained parallel type definition is a second source of truth that will desync from the spec.
