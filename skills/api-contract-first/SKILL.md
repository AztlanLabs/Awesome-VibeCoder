---
name: api-contract-first
description: 'OpenAPI 3.1, AsyncAPI, JSON-Schema patterns, deprecation, idempotency-key, problem+json, cursor pagination — the canonical API contract design skill consumed by API Designer and implemented against by Backend Engineer.'
---

# API Contract-First Design

Design API contracts that are complete, unambiguous, and implementable before a single line of endpoint code is written. This skill defines the canonical patterns for REST (OpenAPI 3.1), event-driven (AsyncAPI), and schema validation (JSON-Schema) — consumed by the API Designer role and implemented against by Backend Engineer.

---

## When to Use This Skill

- Designing a new API surface (REST, GraphQL, gRPC, or event-driven).
- Authoring or updating `.sdlc/contracts/api-contracts.md` or an OpenAPI 3.1 specification.
- Reviewing an API contract for completeness: error envelopes, pagination, versioning, idempotency, deprecation.
- Adding a new resource domain to an existing contract.
- Evaluating whether an endpoint design conforms to the contract-first pattern.

## Prerequisites

- The `.sdlc/` shared state directory exists (see `skills/sdlc-shared-memory/SKILL.md`).
- `architecture.md` and `techContext.md` are loaded for technology constraints.
- `db-schema.md` is loaded if the API exposes database-backed resources.

---

## Core Patterns

### 1. OpenAPI 3.1 — The Canonical REST Contract Format

Every REST API surface MUST be documented in an OpenAPI 3.1 specification. The spec is the source of truth; implementation code is derived from it, never the reverse.

#### Minimum Required Elements

```yaml
openapi: 3.1.0
info:
  title: "<Service Name>"
  version: "1.0.0"
  description: "<One-paragraph scope statement>"
  contact:
    name: "<Team>"
    email: "<team@org.com>"
servers:
  - url: https://api.example.com/v1
    description: Production
  - url: https://api-staging.example.com/v1
    description: Staging
paths:
  /<resource>:
    get:
      operationId: list<Resources>
      summary: "List all <resources>"
      description: "Returns a paginated list of <resources>. Default page size is 20."
      parameters:
        - name: cursor
          in: query
          schema: { type: string }
        - name: limit
          in: query
          schema: { type: integer, minimum: 1, maximum: 100, default: 20 }
      responses:
        "200":
          description: Paginated list
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/<Resource>Page"
        "401": { $ref: "#/components/responses/Unauthorized" }
        "429": { $ref: "#/components/responses/RateLimited" }
    post:
      operationId: create<Resource>
      summary: "Create a new <resource>"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/<Resource>Create"
      parameters:
        - name: Idempotency-Key
          in: header
          required: true
          schema: { type: string, format: uuid }
      responses:
        "201":
          description: Created
          headers:
            Location:
              schema: { type: string, format: uri }
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/<Resource>"
        "409": { $ref: "#/components/responses/Conflict" }
        "422": { $ref: "#/components/responses/UnprocessableEntity" }
  /<resource>/{id}:
    get:
      operationId: get<Resource>
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string }
      responses:
        "200":
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/<Resource>"
        "404": { $ref: "#/components/responses/NotFound" }
```

#### Components: Schemas, Responses, Parameters

Reuse is mandatory. Every response envelope, error shape, and pagination wrapper is defined once in `components/` and `$ref`'d everywhere.

```yaml
components:
  schemas:
    <Resource>:
      type: object
      required: [id, createdAt]
      properties:
        id: { type: string, format: uuid }
        createdAt: { type: string, format: date-time }
        updatedAt: { type: string, format: date-time }
    <Resource>Create:
      type: object
      required: [name]
      properties:
        name: { type: string, minLength: 1, maxLength: 255 }
    <Resource>Page:
      type: object
      required: [data, pagination]
      properties:
        data:
          type: array
          items: { $ref: "#/components/schemas/<Resource>" }
        pagination:
          $ref: "#/components/schemas/CursorPagination"
    CursorPagination:
      type: object
      required: [nextCursor, hasMore]
      properties:
        nextCursor: { type: string, nullable: true }
        hasMore: { type: boolean }
        total: { type: integer, nullable: true, description: "Total count when available; may be omitted for large datasets" }
    ProblemResponse:
      type: object
      required: [type, title, status, detail, instance, traceId]
      properties:
        type: { type: string, format: uri, description: "URI to the problem type definition" }
        title: { type: string, description: "Human-readable summary" }
        status: { type: integer, description: "HTTP status code" }
        detail: { type: string, description: "Human-readable explanation" }
        instance: { type: string, format: uri, description: "URI to this specific occurrence" }
        traceId: { type: string, description: "Distributed trace ID for debugging" }
        errors:
          type: array
          items:
            type: object
            properties:
              field: { type: string }
              issue: { type: string }
              code: { type: string }
    DeprecationNotice:
      type: object
      required: [deprecated, sunsetDate, migrationGuide]
      properties:
        deprecated: { type: boolean, const: true }
        sunsetDate: { type: string, format: date, description: "ISO 8601 date when this endpoint will be removed" }
        migrationGuide: { type: string, format: uri, description: "Link to migration documentation" }
        successor: { type: string, format: uri, description: "Link to the replacement endpoint" }

  responses:
    Unauthorized:
      description: Missing or invalid credentials
      content:
        application/problem+json:
          schema: { $ref: "#/components/schemas/ProblemResponse" }
    NotFound:
      description: Resource not found
      content:
        application/problem+json:
          schema: { $ref: "#/components/schemas/ProblemResponse" }
    Conflict:
      description: Resource conflict (e.g., duplicate)
      content:
        application/problem+json:
          schema: { $ref: "#/components/schemas/ProblemResponse" }
    UnprocessableEntity:
      description: Validation failure
      content:
        application/problem+json:
          schema: { $ref: "#/components/schemas/ProblemResponse" }
    RateLimited:
      description: Too many requests
      headers:
        Retry-After:
          schema: { type: integer }
      content:
        application/problem+json:
          schema: { $ref: "#/components/schemas/ProblemResponse" }
```

---

### 2. Problem+JSON (RFC 9457) — The Canonical Error Envelope

Every error response MUST use the `application/problem+json` media type and conform to RFC 9457 (formerly RFC 7807). Do not invent per-endpoint error shapes.

#### Required Fields

| Field | Type | Meaning |
|-------|------|---------|
| `type` | URI | Stable URI identifying the problem category (e.g., `https://api.example.com/problems/validation-failed`) |
| `title` | string | Human-readable summary, stable across occurrences of this type |
| `status` | integer | The HTTP status code of this response |
| `detail` | string | Human-readable explanation specific to *this* occurrence |
| `instance` | URI | Optional URI identifying this specific error occurrence (can be `urn:uuid:<traceId>`) |
| `traceId` | string | Distributed trace ID for correlating with logs and spans |

#### Extension: Validation Errors

When `status` is 422, add an `errors` array with per-field detail:

```json
{
  "type": "https://api.example.com/problems/validation-failed",
  "title": "Validation Failed",
  "status": 422,
  "detail": "The request body contains invalid fields.",
  "instance": "urn:uuid:abc-123",
  "traceId": "abc-123",
  "errors": [
    { "field": "email", "issue": "Must be a valid email address", "code": "INVALID_FORMAT" },
    { "field": "age", "issue": "Must be >= 0", "code": "OUT_OF_RANGE" }
  ]
}
```

#### Problem Type Catalog

Define a stable set of problem types for the API surface:

| Type URI | Title | Default Status | Retryable? |
|----------|-------|----------------|------------|
| `.../problems/validation-failed` | Validation Failed | 422 | No |
| `.../problems/not-found` | Not Found | 404 | No |
| `.../problems/conflict` | Conflict | 409 | No (unless idempotency replay) |
| `.../problems/unauthorized` | Unauthorized | 401 | No |
| `.../problems/forbidden` | Forbidden | 403 | No |
| `.../problems/rate-limited` | Rate Limited | 429 | Yes (after Retry-After) |
| `.../problems/internal-error` | Internal Server Error | 500 | Yes (exponential backoff) |
| `.../problems/service-unavailable` | Service Unavailable | 503 | Yes (after Retry-After) |
| `.../problems/gateway-timeout` | Gateway Timeout | 504 | Yes (exponential backoff) |

---

### 3. Cursor Pagination — The Default for List Endpoints

Cursor-based pagination is the default for every list endpoint. Offset/limit is accepted only for simple, small, stable datasets where cursor maintenance is disproportionate.

#### Request Parameters

| Parameter | Type | Required | Default | Max | Description |
|-----------|------|----------|---------|-----|-------------|
| `cursor` | string (opaque) | No | — | — | Opaque cursor from `pagination.nextCursor` of a previous response. Omit for the first page. |
| `limit` | integer | No | 20 | 100 | Maximum items to return. |

#### Response Envelope

```json
{
  "data": [ /* items */ ],
  "pagination": {
    "nextCursor": "eyJpZCI6ImQzNTM...",
    "hasMore": true,
    "total": 1247
  }
}
```

| Field | Type | Meaning |
|-------|------|---------|
| `nextCursor` | string \| null | Opaque cursor for the next page. `null` when on the last page. |
| `hasMore` | boolean | `true` if more pages exist beyond this one. |
| `total` | integer \| null | Total count when cheaply available. Omit (`null`) for large datasets where `COUNT(*)` is expensive. |

#### Cursor Construction Rules

- Cursors are **opaque** to clients — never expose internal IDs, offsets, or sort keys.
- Encode the cursor as base64url (no padding) of a deterministic JSON payload: `{"id": "<last-item-id>", "v": 1}`.
- Version the payload (`v`) so cursor encoding can evolve without breaking existing cursors.
- Cursors are stable under data insertion: a cursor fetched before new rows were inserted still returns the correct next page (no skipped or duplicated items).

#### When Offset/Limit Is Acceptable

- The dataset is small (< 1000 items) and stable.
- The UI requires page-number navigation (e.g., "Page 3 of 47").
- Full `COUNT(*)` is cheap (indexed, no complex filters).

If offset/limit is used, declare it explicitly in the contract and note the trade-off.

---

### 4. Idempotency Keys — Safe Retry for Every Mutating Endpoint

Every `POST`, `PUT`, `PATCH`, and `DELETE` endpoint MUST support idempotency keys.

#### Mechanism

| Element | Specification |
|---------|---------------|
| Header | `Idempotency-Key: <uuid>` |
| Client responsibility | Generate a fresh UUID for each *new* request; reuse the same UUID when retrying a request whose outcome is unknown. |
| Server responsibility | Store (key → response) for completed requests. On replay, return the stored response (same status, same body, same headers) without re-executing. |
| Storage duration | At least 24 hours after the original request completed. |
| Key scope | Per resource domain (a key for `POST /users` does not collide with `POST /orders`). |
| Conflict (409) | If two concurrent requests arrive with the same key and the first is still in-flight, return `409 Conflict` with a problem+json body instructing the client to retry after the first completes. |

#### OpenAPI Declaration

```yaml
parameters:
  - name: Idempotency-Key
    in: header
    required: true
    schema:
      type: string
      format: uuid
    description: "Client-generated UUID. Reuse when retrying a request whose outcome is unknown."
```

---

### 5. Deprecation — Sunset with Notice

Every API change that removes or breaks existing behavior MUST follow the deprecation lifecycle.

#### Lifecycle Stages

| Stage | Duration | Client Visible | Behavior |
|-------|----------|----------------|----------|
| **Announce** | Day 0 | `Deprecation: true` header + `Sunset` header on responses | Endpoint works normally. |
| **Warn** | Announce + 30d minimum | `Deprecation` + `Sunset` headers + warning-level log on each call | Endpoint works normally; clients are expected to migrate. |
| **Sunset** | After Sunset date | `410 Gone` or `404 Not Found` | Endpoint removed. |

#### HTTP Headers

```http
Deprecation: true
Sunset: Sat, 31 Dec 2025 23:59:59 GMT
Link: <https://api.example.com/v2/users>; rel="successor-version"
Link: <https://docs.example.com/migration/users-v1-to-v2>; rel="deprecation"
```

#### OpenAPI Declaration

Add the `DeprecationNotice` schema (from §1) to every deprecated endpoint's response descriptions, and mark the operation:

```yaml
get:
  operationId: listUsersV1
  deprecated: true
  description: |
    **DEPRECATED**: This endpoint will be removed on 2025-12-31.
    Migrate to `GET /v2/users`. See [migration guide](https://docs.example.com/migration/users-v1-to-v2).
  responses:
    "200":
      headers:
        Deprecation:
          schema: { type: boolean, const: true }
        Sunset:
          schema: { type: string, format: http-date }
        Link:
          schema: { type: string }
```

---

### 6. API Versioning

Every API surface MUST declare a versioning strategy before the first endpoint is designed.

| Strategy | Mechanism | When to Use |
|----------|-----------|-------------|
| **URI path** | `/v1/resource`, `/v2/resource` | Default. Most explicit, easiest to route and document. |
| **Header** | `Accept-Version: v1` or `API-Version: 2024-01-01` | When URI cleanliness is paramount. Harder to discover. |
| **Content negotiation** | `Accept: application/vnd.example.v1+json` | When the same resource has multiple representations. Rare. |

#### Versioning Rules

- **Major version bump** (v1 → v2): breaking changes — removed fields, changed types, removed endpoints, changed auth.
- **Minor addition** (within v1): additive changes only — new optional fields, new endpoints, new enum values. No breaking changes within a major version.
- **Date-based versions** (`2024-01-01`): preferred for header-based versioning; the date is the API's release date, not an expiration date.

---

### 7. AsyncAPI — Event-Driven Contracts

When the system includes event-driven surfaces (message queues, webhooks, WebSockets, SSE), document them in AsyncAPI 3.0.

#### Minimum Required Elements

```yaml
asyncapi: 3.0.0
info:
  title: "<Service> Events"
  version: "1.0.0"
servers:
  production:
    host: kafka://broker.example.com:9092
    protocol: kafka
channels:
  user.created:
    address: user.created
    messages:
      userCreated:
        payload:
          $ref: "#/components/schemas/UserCreatedEvent"
operations:
  publishUserCreated:
    action: send
    channel:
      $ref: "#/channels/user.created"
components:
  schemas:
    UserCreatedEvent:
      type: object
      required: [id, type, version, timestamp, data]
      properties:
        id: { type: string, format: uuid, description: "Unique event ID (idempotency key)" }
        type: { type: string, const: "user.created" }
        version: { type: string, const: "1.0" }
        timestamp: { type: string, format: date-time }
        data:
          type: object
          required: [userId, email]
          properties:
            userId: { type: string, format: uuid }
            email: { type: string, format: email }
```

#### Event Envelope Rules

- Every event carries `id` (unique event ID = idempotency key), `type` (event name), `version` (schema version), and `timestamp`.
- Event schemas are versioned independently of API versions.
- Events are immutable — never change an existing event schema; create a new version and publish both during migration.

---

### 8. JSON-Schema — Request/Response Validation

Every request body and response body in the OpenAPI spec MUST have a JSON-Schema (2020-12 or draft-07) that is strict enough to reject invalid data but permissive enough to allow forward-compatible extensions.

#### Validation Rules

- **Required fields**: mark every field the server unconditionally needs as `required`.
- **Read-only fields**: fields the server sets (`id`, `createdAt`, `updatedAt`) appear in response schemas but NOT in request schemas.
- **Write-only fields**: fields the client sends but the server never returns (`password`, `secret`) appear in request schemas but NOT in response schemas.
- **Nullable vs optional**: `nullable: true` means `null` is a valid value; omitting from `required` means the field can be absent. These are different.
- **String formats**: use `format: email`, `format: uri`, `format: uuid`, `format: date-time`, `format: date` wherever applicable.
- **Ranges**: `minimum`, `maximum`, `minLength`, `maxLength`, `minItems`, `maxItems` on every numeric, string, and array field.
- **Enums**: prefer string enums over integer enums (readable in logs).
- **Additional properties**: set `additionalProperties: false` on request schemas to reject unknown fields (strict by default).

---

## Contract Structure in `.sdlc/`

The API Designer owns `.sdlc/contracts/api-contracts.md`. The file is organized per resource domain:

```markdown
## [Resource Domain]
- **Base path**: `/v1/<resource>`
- **Style**: REST | GraphQL | gRPC
- **AuthN**: [bearer token | API key | session cookie]
- **Rate limit**: [requests per window]

### Endpoints
| Method | Path | Summary | Request Body | Response | Errors |
|---|---|---|---|---|---|

### Data Models
| Model | Fields | Constraints | Example |
|---|---|---|---|

### Error Codes
| Code | HTTP Status | Meaning | Retryable? |
|---|---|---|---|

### Changelog
| Date | Change | Version |
|---|---|---|
```

Accompanying OpenAPI 3.1 YAML files live at `.sdlc/contracts/api-openapi.yaml` (or per-domain files).

---

## Indicators of Done

| Indicator | Target |
|-----------|--------|
| OpenAPI 3.1 spec | Every REST surface has a valid, `$ref`-clean OpenAPI 3.1 specification |
| Problem+JSON | Every error response uses `application/problem+json` with `type`, `title`, `status`, `detail`, `traceId` |
| Cursor pagination | Every list endpoint declares cursor pagination with `nextCursor`, `hasMore` |
| Idempotency keys | Every mutating endpoint declares `Idempotency-Key` header |
| Deprecation lifecycle | Every deprecated endpoint carries `Deprecation` + `Sunset` headers and a migration guide link |
| Versioning | Every API surface declares a version strategy (URI path, header, or content negotiation) |
| JSON-Schema strictness | Every request schema has `additionalProperties: false`, `required` fields, and format/range constraints |
| AsyncAPI (if event-driven) | Every event channel has a schema with `id`, `type`, `version`, `timestamp` envelope |
| Contract completeness | Every resource domain has endpoints, data models, error codes, and a changelog |

## Boundaries

### Do

- Design the API contract before implementation begins — contract-first, never code-first.
- Use OpenAPI 3.1 as the canonical REST contract format.
- Use RFC 9457 `application/problem+json` for every error response.
- Default to cursor pagination for list endpoints.
- Require `Idempotency-Key` on every mutating endpoint.
- Follow the deprecation lifecycle (Announce → Warn → Sunset) for every breaking change.
- Version every API surface from day one.
- Set `additionalProperties: false` on request schemas.
- Use `$ref` for all reusable components (schemas, responses, parameters, examples).

### Do Not Do

- Do not implement API endpoints or backend code (defer to Backend Engineer).
- Do not design the API contract after implementation has started.
- Do not invent per-endpoint error shapes — use the canonical problem+json envelope.
- Do not expose internal IDs, offsets, or sort keys in pagination cursors.
- Do not skip idempotency keys on mutating endpoints.
- Do not remove or break an endpoint without the deprecation lifecycle.
- Do not use offset/limit pagination without documenting the trade-off.
- Do not omit `additionalProperties: false` on request schemas.