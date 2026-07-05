# Web Development Cookbook — Node.js

Focused, copy-pasteable Node.js production recipes. Each recipe ships a runnable `.ts` example under `recipe/`. These do **not** use the Copilot SDK — they are pure Node.js platform patterns.

## Recipes

- [Streaming Responses](streaming-responses.md): chunked HTTP responses with `ReadableStream`, backpressure, and disconnect cancellation.
- [Graceful Shutdown](graceful-shutdown.md): signal handling, connection draining, deadline-bounded exit, readiness probes.
- [Structured Logger](structured-logger.md): leveled JSON logger with child loggers, redaction, and async sinks.
- [Worker Threads Pool](worker-threads-pool.md): bounded `worker_threads` pool with task queue and error propagation.
- [Rate Limiter](rate-limiter.md): token-bucket + sliding-window limiter as composable `http` middleware.

## Running Examples

```bash
cd recipe
npm install
npx tsx <file>.ts
# or: npm run <recipe-id>
```

Each example is a standalone server or program — see the recipe markdown for the exact command and endpoints.

## Contributing

Add a new recipe by dropping a markdown file here and a matching `.ts` under `recipe/`. Follow repository guidance in [CONTRIBUTING.md](../../../CONTRIBUTING.md).