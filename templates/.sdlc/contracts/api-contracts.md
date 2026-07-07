# API Contracts

> Owned by API Designer. Consumed unchanged by Backend Engineer, Frontend Engineer, Full Stack Engineer, and QA Tester. See `skills/api-contract-first/SKILL.md`.

## Versioning

- <e.g. URL-prefixed `/api/v1/...`, or content-negotiated>

## Endpoints

### `<METHOD> <path>`

- **Description**: <what it does>
- **Request**: <schema>
- **Response**: <schema>
- **Errors**: <stable error codes + problem+json shape>
- **Idempotency**: <idempotency-key behavior for non-safe methods>
- **Pagination**: <cursor-based convention, if a list endpoint>

## Changelog

| Date | Change | Author |
|---|---|---|
