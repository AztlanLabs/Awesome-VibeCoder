# Runnable Recipe Examples — Node.js

Standalone, executable TypeScript examples for each Node.js cookbook recipe. Each file runs directly with `tsx` or via npm scripts.

## Prerequisites

- Node.js 20 or later (for `availableParallelism`, `Blob`, and stable `ReadableStream` APIs).

```bash
npm install
```

## Available Recipes

| Recipe               | npm script                  | Direct command                    | Description                                |
| -------------------- | --------------------------- | --------------------------------- | ------------------------------------------ |
| Streaming Responses  | `npm run streaming-responses` | `npx tsx streaming-responses.ts` | Chunked HTTP streaming with backpressure   |
| Graceful Shutdown    | `npm run graceful-shutdown`   | `npx tsx graceful-shutdown.ts`   | Drain in-flight requests, deadline-bounded |
| Structured Logger    | `npm run structured-logger`   | `npx tsx structured-logger.ts`   | Leveled JSON logger, child loggers, redact |
| Worker Threads Pool  | `npm run worker-threads-pool` | `npx tsx worker-threads-pool.ts` | Bounded worker pool with queue             |
| Rate Limiter         | `npm run rate-limiter`        | `npx tsx rate-limiter.ts`        | Token-bucket + sliding-window middleware   |

## Running a Server

The server examples print the port on startup. Test streaming with:

```bash
curl -N http://localhost:4000/stream
```

Drive the rate limiter with a quick loop:

```bash
for i in $(seq 1 15); do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:4200/; sleep 0.1; done
```

## Learning Resources

- [Node.js Documentation](https://nodejs.org/docs/latest/api/)
- [Parent Cookbook](../README.md)