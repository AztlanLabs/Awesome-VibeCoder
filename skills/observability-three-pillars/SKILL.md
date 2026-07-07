---
name: observability-three-pillars
description: 'OTLP/JSON structured logs, RED/USE metrics, distributed tracing (W3C Trace Context), SLO/SLI/error-budget, RUM vs LAB telemetry — the canonical observability skill consumed by DevOps Engineer and Backend Engineer.'
---

# Observability — Three Pillars

## When to Use This Skill

Use when the task involves:

- Designing or instrumenting structured logging (OTLP/JSON)
- Defining RED (Rate, Errors, Duration) or USE (Utilization, Saturation, Errors) metrics
- Implementing distributed tracing with W3C Trace Context propagation
- Setting SLOs, SLIs, and error budgets
- Choosing between Real User Monitoring (RUM) and synthetic/LAB monitoring
- Wiring OpenTelemetry collectors, exporters, or SDKs
- Auditing an existing observability stack for gaps

## Centralized State Architecture

This skill is read-only advisory — it does not write to `.sdlc/`. The consuming agent (DevOps Engineer, Backend Engineer) writes observability configuration to real project paths (e.g. `otel-collector-config.yaml`, `infra/monitoring/`, application code) and records the artifact paths + validation result in `.sdlc/memory.md`.

## Core Patterns

### 1. Structured Logging — OTLP/JSON

Every log record MUST be structured (JSON) and carry the following minimum fields:

```json
{
  "timestamp": "2025-01-15T10:32:00.123Z",
  "severity": "ERROR",
  "message": "Payment authorization failed for order abc-123",
  "service.name": "payment-gateway",
  "service.version": "2.4.1",
  "service.instance.id": "pgw-4f8a2b",
  "trace.id": "0af7651916cd43dd8448eb211c80319c",
  "span.id": "b7ad6b7169203331",
  "resource": {
    "order.id": "abc-123",
    "payment.method": "credit_card",
    "gateway.response_code": "DECLINED"
  }
}
```

**Rules:**

- `severity` MUST be one of: TRACE, DEBUG, INFO, WARN, ERROR, FATAL — aligned with OpenTelemetry severity levels.
- `trace.id` and `span.id` MUST be present on every log record emitted inside a traced context. Use W3C Trace Context hex-encoded 32-character (trace) and 16-character (span) identifiers.
- `resource` is a free-form object carrying domain-specific context (order id, user id, tenant id, etc.). Never put PII or secrets in log records.
- Logs MUST be emitted via OTLP (gRPC or HTTP/protobuf) to an OpenTelemetry collector, NOT written to local files in production.
- Use `service.name` + `service.version` + `service.instance.id` as the OTel `Resource` attributes — these are set once at SDK initialization, not per-record.

**Anti-patterns:**

- Unstructured `printf`-style logs: `log.info("User " + userId + " logged in")`
- Logging stack traces as the message field — put the exception detail in `resource.exception` and keep `message` human-readable.
- Logging request/response bodies without redaction.

### 2. Metrics — RED and USE

**RED** (Rate, Errors, Duration) — for **service-level** monitoring of every endpoint/operation:

| Dimension | Definition | Instrument | Example |
| --- | --- | --- | --- |
| Rate | Requests per second | Counter | `http.server.requests{method=GET, route=/api/orders}` |
| Errors | Failed requests per second | Counter | `http.server.errors{method=POST, route=/api/checkout, error=timeout}` |
| Duration | Latency distribution | Histogram | `http.server.duration_ms{method=GET, route=/api/orders}` — p50, p95, p99 buckets |

**USE** (Utilization, Saturation, Errors) — for **resource-level** monitoring of every infrastructure component:

| Dimension | Definition | Instrument | Example |
| --- | --- | --- | --- |
| Utilization | % of resource capacity consumed | Gauge | `cpu.utilization{host=web-01}` — target < 70% |
| Saturation | Queue depth / backlog | Gauge | `db.connection_pool.waiting{pool=main}` — target < 5 |
| Errors | Resource-level faults | Counter | `disk.io_errors{device=nvme0n1}` — target 0 |

**Rules:**

- Every HTTP endpoint MUST export RED metrics. Use the OpenTelemetry HTTP semantic conventions (`http.server.request.duration`, `http.server.active_requests`).
- Every infrastructure component (DB pool, message queue, cache, disk) MUST export USE metrics.
- Histogram buckets MUST include the SLO target latency as an explicit bucket boundary.
- Counters MUST be monotonic (never reset). Use `_total` suffix convention.
- Metrics MUST be exported via OTLP to a collector; the collector fans out to Prometheus, CloudWatch, Datadog, etc.

### 3. Distributed Tracing — W3C Trace Context

Every service MUST propagate the W3C Trace Context headers:

| Header | Format | Example |
| --- | --- | --- |
| `traceparent` | `00-{trace-id}-{parent-span-id}-{trace-flags}` | `00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01` |
| `tracestate` | Vendor-specific key=value pairs | `dd=s:2;o:high_priority` |

**Rules:**

- `trace-id` is 32 hex chars (16 bytes), `parent-span-id` is 16 hex chars (8 bytes), `trace-flags` is 2 hex chars (sampled=01, not-sampled=00).
- Every inbound request that carries a `traceparent` MUST continue the trace; never start a new trace when one is already present.
- Every outbound HTTP call, gRPC call, and message queue publish MUST inject `traceparent`.
- Spans MUST carry: `name` (low-cardinality, e.g. `POST /api/checkout`), `kind` (CLIENT, SERVER, PRODUCER, CONSUMER, INTERNAL), `status` (OK or ERROR), and at least one `attribute` identifying the operation.
- Span names MUST be low-cardinality — use the route pattern (`/api/orders/:id`), NOT the concrete URL (`/api/orders/abc-123`).
- Errors MUST set span status to ERROR and attach an `exception.message` and `exception.type` event.

**Sampling rules:**

- Head-based sampling: decision made at trace root, propagated via `trace-flags`.
- Default sampling rate: 100% for errors, 10% for success (configurable per-service).
- Tail-based sampling: collector retains all spans for a window (e.g. 30s) and keeps only traces that contain an ERROR span or exceed the latency SLO.

### 4. SLO / SLI / Error Budget

**Definitions:**

- **SLI** (Service Level Indicator): A measured metric. Example: "99.3% of GET /api/orders requests complete in < 300ms over the trailing 28 days."
- **SLO** (Service Level Objective): The target for an SLI. Example: "99.5% of GET /api/orders requests complete in < 300ms."
- **Error Budget**: The allowed gap between SLO and perfection (100%). Example: 100% - 99.5% = 0.5% error budget = ~3.6 hours/month of allowed degradation.

**Rules:**

- Every user-facing endpoint MUST have an availability SLO (success rate) and a latency SLO (p95 or p99).
- SLOs MUST be measured over a rolling window (28 days is standard; 7 days for fast-iteration services).
- Error budget burn rate alerts: fast burn (2% of budget consumed in 1 hour → page), slow burn (5% of budget consumed in 6 hours → ticket).
- When error budget is exhausted, feature releases MUST freeze until the budget recovers or the SLO is reset.
- SLOs MUST be documented in `.sdlc/contracts/api-contracts.md` alongside the API specification.

**Burn rate alert thresholds:**

| Burn Rate | Budget Consumed | Time Window | Alert Severity |
| --- | --- | --- | --- |
| 14.4x | 2% | 1 hour | Critical (page) |
| 6x | 5% | 6 hours | Warning (ticket) |
| 1x | 10% | 3 days | Info (dashboard) |

### 5. RUM vs LAB (Synthetic Monitoring)

| Dimension | RUM (Real User Monitoring) | LAB (Synthetic / Lighthouse) |
| --- | --- | --- |
| Data source | Real user browsers in production | Controlled lab environment |
| Measures | LCP, INP, CLS, TTFB from real devices/networks | Simulated LCP, TBT, CLS on emulated device |
| Strengths | Reflects actual user experience; captures long-tail | Reproducible; no PII concerns; CI-integratable |
| Weaknesses | Noisy; requires enough traffic for statistical significance | Doesn't capture real-world network/devices; misses long-tail |
| Tooling | Web Vitals JS library → OTLP; commercial RUM (Datadog RUM, New Relic Browser) | Lighthouse CI, PageSpeed Insights API, WebPageTest |

**Rules:**

- RUM and LAB are complementary, not alternatives. Use both.
- LAB scores gate PRs in CI (Lighthouse CI assertions on LCP < 2.5s, TBT < 200ms, CLS < 0.1).
- RUM data feeds the SLO dashboard — the SLO is measured from RUM, not LAB.
- Core Web Vitals MUST be exported from the browser via `web-vitals` library to an OTLP collector endpoint (`/v1/traces`).

### 6. OpenTelemetry Collector Topology

The standard deployment topology:

```
Application SDK (OTLP exporter)
        │
        ▼
OpenTelemetry Collector (agent mode, per-host sidecar or DaemonSet)
        │
        ▼
OpenTelemetry Collector (gateway mode, cluster-level aggregation)
        │
        ├──► Prometheus (metrics)
        ├──► Jaeger/Tempo (traces)
        ├──► Loki/Elasticsearch (logs)
        └──► Alertmanager → PagerDuty/Slack (alerts)
```

**Rules:**

- Agent collector does tail sampling and attribute redaction (strip PII from spans/logs).
- Gateway collector does aggregation and fan-out to backends.
- Never send telemetry directly from application SDKs to vendor backends — always route through at least one collector.
- Collector config MUST be version-controlled in the project repository.

## Indicators of Done

| Indicator | Evidence |
| --- | --- |
| Structured logs emitted | Every log record is JSON with `timestamp`, `severity`, `message`, `service.name`, `trace.id`, `span.id` |
| RED metrics exported | Every HTTP endpoint has Rate, Errors, Duration counters/histograms visible in metrics backend |
| USE metrics exported | Every infrastructure component has Utilization, Saturation, Errors gauges/counters |
| Trace context propagated | `traceparent` header present on all inter-service HTTP/gRPC calls |
| SLOs defined | Every user-facing endpoint has availability + latency SLO documented in `.sdlc/contracts/api-contracts.md` |
| Error budget alerts configured | Burn rate alerts at 14.4x (critical), 6x (warning), 1x (info) thresholds |
| RUM + LAB both active | Web Vitals exported to OTLP AND Lighthouse CI assertions in CI pipeline |
| Collector config version-controlled | `otel-collector-config.yaml` committed to repository |

## Boundaries

**Do:**

- Use OTLP as the universal telemetry protocol — logs, metrics, and traces all over OTLP.
- Propagate W3C Trace Context on every inter-service call.
- Define SLOs for every user-facing endpoint before launch.
- Use RED for services, USE for resources — never mix the models.
- Version-control all observability configuration (collector configs, alert rules, dashboards as code).

**Do Not Do:**

- Do not log PII, secrets, or credentials in telemetry data.
- Do not use unstructured `printf`-style logging in production services.
- Do not skip trace propagation — a broken trace is worse than no trace.
- Do not set SLOs without error budget alerting — an unenforced SLO is a wish.
- Do not rely on LAB data alone for SLO measurement — SLOs must be measured from RUM.
- Do not send telemetry directly from SDKs to vendor backends — always route through a collector.