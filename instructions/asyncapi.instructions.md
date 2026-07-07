---
description: 'AsyncAPI specification conventions for event-driven and message-based APIs — channels, messages, and schema reuse.'
applyTo: '**/asyncapi.yaml, **/asyncapi.yml, **/asyncapi.json, **/*.asyncapi.yaml'
---

# AsyncAPI Instructions

You are an expert API designer authoring AsyncAPI specifications as the contract-first source of truth for an event-driven/message-based system.

## Channels & Operations

- **MUST**: model each logical topic/queue as a `channel`, and each direction of communication on it (`send`/`receive` in AsyncAPI 3.x, `publish`/`subscribe` in 2.x) as a separate `operation` — a spec that only lists channels without operations doesn't document who produces vs. who consumes.
- **SHOULD**: name channels after the domain event/resource, not the transport detail (`order.created`, not `kafka-topic-7`) — the spec should read as a domain contract, not an infrastructure inventory.
- **MUST**: document the channel's `address`/topic-naming pattern explicitly, including any templated segments (`user.{userId}.notifications`), with the parameter defined in `parameters`.

## Messages & Payloads

- **MUST**: define reusable message schemas under `components/messages` / `components/schemas` and reference them from every channel that uses that message shape — event schemas duplicated inline across channels will drift.
- **MUST**: version message payloads explicitly (a `schemaVersion`/`version` field in the payload, or a versioned schema name) since consumers of an event stream may be running older code than the producer at any given time — unlike a request/response API, you can't assume synchronized deploys.
- **SHOULD**: include message `headers` schemas (correlation ID, trace context, content-type) separately from the payload schema, so cross-cutting metadata isn't mixed into the domain payload's shape.

## Schema Evolution & Compatibility

- **MUST**: treat new event schema versions as additive-only within a compatibility window (new optional fields) — removing or retyping a field breaks any consumer still running against the old schema, and consumers deploy independently of producers.
- **SHOULD**: document the compatibility guarantee explicitly in the spec's `info.description` (e.g. "backward compatible for 90 days after a field is deprecated") so consumer teams know how long they have to migrate.
- **MUST**: register a schema registry (Confluent Schema Registry, AWS Glue Schema Registry, or equivalent) as the enforcement mechanism if the transport is Kafka/similar — the AsyncAPI spec documents the contract, but only a registry enforces it at produce-time.

## Bindings

- **MUST**: use protocol-specific `bindings` (`kafka`, `amqp`, `mqtt`, `websockets`) to document transport-level details (partition key, exchange type, QoS) rather than leaving them as prose — bindings are what let AsyncAPI-aware tooling generate real producer/consumer code.
- **SHOULD**: document the partition/routing key derivation for Kafka/AMQP channels explicitly — consumers relying on ordering guarantees need to know what determines partition assignment.

## Error & Dead-Letter Handling

- **SHOULD**: document the dead-letter channel/topic (if one exists) as its own channel in the spec, including the message envelope it carries (original message + failure reason + retry count) — an undocumented DLQ is invisible to new team members debugging a message-loss incident.
- **MUST**: specify retry/redelivery semantics (at-least-once vs. exactly-once, max retry count) in the channel description — consumers need to know whether to design for idempotent processing.

## Security

- **MUST**: declare `securitySchemes` for broker authentication (SASL, mTLS, API key) at the `components` level, referenced per-server — don't leave broker auth undocumented and configured only in deployment scripts.

## Validation & Tooling

- **MUST**: lint the spec in CI (`@asyncapi/cli validate`, Spectral with the AsyncAPI ruleset) so schema errors are caught before consumers are built against a broken contract.
- **SHOULD**: generate consumer/producer boilerplate (or at least payload types) from the spec rather than hand-maintaining a parallel type definition per service.
