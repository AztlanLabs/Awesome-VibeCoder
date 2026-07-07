---
description: 'OpenTelemetry instrumentation and Collector (otelcol) conventions — traces, metrics, logs, and pipeline configuration.'
applyTo: '**/*.ts, **/*.js, **/*.py, **/*.go, **/otel-collector*.yaml, **/otelcol*.yaml'
---

# OpenTelemetry & Collector Instructions

You are an expert in observability, instrumenting applications with OpenTelemetry and configuring the OpenTelemetry Collector (otelcol).

## Instrumentation

- **MUST**: use auto-instrumentation libraries for well-supported frameworks (HTTP servers/clients, DB drivers, message queues) before hand-writing spans — auto-instrumentation covers the 80% case (request spans, DB call spans) consistently across services.
- **SHOULD**: add manual spans only around business-meaningful units of work (a specific algorithm step, an external call not covered by auto-instrumentation) — spans for every function call create noise that obscures the signal in trace waterfalls.
- **MUST**: propagate W3C Trace Context (`traceparent`/`tracestate` headers) across every service-to-service call — a broken propagation link anywhere in a call chain fragments what should be one trace into disconnected orphan traces.

## Semantic Conventions

- **MUST**: use OpenTelemetry semantic convention attribute names (`http.request.method`, `db.system`, `service.name`) rather than inventing custom attribute names for concepts the spec already covers — custom names break compatibility with dashboards/alerts built against the standard conventions.
- **SHOULD**: set `service.name` and `service.version` resource attributes on every service — without them, traces/metrics from different services are indistinguishable in a shared backend.

## Traces

- **MUST**: set span status (`Ok`/`Error`) and record exceptions (`span.recordException()`) on failure paths — an unset status on a span that actually failed makes error-rate dashboards built on trace data undercounted.
- **SHOULD**: add span attributes for the specific identifiers that matter for debugging that operation (order ID, user ID — never PII/secrets) so a trace can be correlated back to the business event it represents.
- **MUST NOT**: put unbounded-cardinality values (raw user input, full request bodies, timestamps as attribute *keys*) into span attributes — the backend's cost and query performance both degrade badly with unbounded cardinality.

## Metrics

- **SHOULD**: use the RED method (Rate, Errors, Duration) for service-level metrics and USE (Utilization, Saturation, Errors) for resource-level metrics as the default metric taxonomy, rather than an ad hoc metric-naming scheme per team.
- **MUST**: use histograms (not just averages) for latency metrics — an average latency hides tail latency (p95/p99), which is usually what actually matters for user experience and SLOs.
- **SHOULD**: keep metric label/attribute cardinality bounded (avoid per-user-ID labels on a metric) — high-cardinality labels are the most common cause of metrics-backend cost blowups.

## Logs

- **MUST**: emit structured logs (JSON, or OTLP log records) with the active trace ID/span ID attached — unstructured text logs with no trace correlation can't be pivoted-to from a trace in the same investigation.
- **SHOULD**: route logs through the same OTLP pipeline as traces/metrics when using the Collector, rather than a separate uncorrelated logging pipeline, so all three signals share resource attributes and correlation IDs.

## Collector Configuration

- **MUST**: configure the Collector with distinct `receivers` → `processors` → `exporters` pipelines per signal type (traces/metrics/logs) — a misconfigured single pipeline mixing signal types silently drops or mishandles data.
- **SHOULD**: use the `batch` processor (batches spans/metrics before export) and a `memory_limiter` processor (protects the Collector from OOM under load) in every production pipeline — running without them means a traffic spike can crash the Collector itself.
- **MUST**: apply the `tail_sampling` or `probabilistic_sampling` processor deliberately (not send 100% of traces to the backend by default) for high-traffic services — un-sampled full trace volume is usually both a cost problem and a backend-performance problem at scale.
- **SHOULD**: keep the Collector config in version control and deploy it the same way as application code (not a manually-edited config on a long-lived instance) — pipeline changes need the same review/rollback discipline as code changes.

## SLOs & Error Budgets

- **MUST**: define SLOs against instrumented metrics (not just uptime) — availability and correctness are different failure modes, and an SLO should specify which one it's protecting.
- **SHOULD**: alert on error-budget burn rate (fast burn = page now, slow burn = ticket) rather than a single static threshold — a static "5xx rate > 1%" alert either pages too often on noise or misses a slow, sustained degradation.
