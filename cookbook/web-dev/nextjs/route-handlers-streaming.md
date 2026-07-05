# Route Handlers Streaming

Return a streaming `Response` body from a `route.ts` Route Handler — Server-Sent Events for browser consumption and NDJSON for machines — with real backpressure handling and a clean `AbortController` shutdown when the client disconnects.

> **Runnable example:** [recipe/route-handlers-streaming.ts](recipe/route-handlers-streaming.ts)
>
> ```bash
> cd recipe && npm install
> npx tsx route-handlers-streaming.ts
> # or: npm run route-handlers-streaming
> ```

## Example scenario

You expose `GET /api/events` which streams log lines from a queue as SSE. The producer is bursty; the consumer may be on a slow mobile link; the user may close the tab mid-stream. You must:

- Push backpressure up to the producer when the client can't keep up.
- Stop producing the instant the client disconnects.
- Use only Web-platform primitives (`Response`, `ReadableStream`, `AbortController`, `TransformStream`).

## Route Handler: SSE

```ts
// app/api/events/route.ts
import type { NextRequest } from "next/server";

type Event = { id: number; message: string };

const encoder = new TextEncoder();

async function* produceEvents(signal: AbortSignal): AsyncGenerator<Event> {
  let id = 0;
  while (!signal.aborted) {
    await new Promise((resolve) => setTimeout(resolve, 250));
    id += 1;
    yield { id, message: `event-${id}` };
    if (id >= 20) break;
  }
}

function sseFrame(event: Event): Uint8Array {
  const payload = `id: ${event.id}\nevent: message\ndata: ${JSON.stringify(event)}\n\n`;
  return encoder.encode(payload);
}

export async function GET(request: NextRequest): Promise<Response> {
  const abort = new AbortController();
  request.signal.addEventListener("abort", () => abort.abort(), { once: true });

  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      const writer = (chunk: Uint8Array) => controller.enqueue(chunk);
      try {
        for await (const event of produceEvents(abort.signal)) {
          if (abort.signal.aborted) break;
          // scheduler.yield keeps the stream coöperative and lets chunks flush.
          while (controller.desiredSize !== null && controller.desiredSize <= 0) {
            await new Promise((resolve) => setTimeout(resolve, 10));
            if (abort.signal.aborted) break;
          }
          writer(sseFrame(event));
        }
      } catch (error) {
        controller.error(error instanceof Error ? error : new Error(String(error)));
        return;
      } finally {
        if (!controller.byobRequest) controller.close();
      }
    },
    cancel(reason) {
      abort.abort(reason);
    },
  });

  return new Response(stream, {
    headers: {
      "content-type": "text/event-stream",
      "cache-control": "no-cache, no-transform",
      connection: "keep-alive",
    },
  });
}
```

## Variation: NDJSON (for machines)

Swap the framing for newline-delimited JSON:

```ts
function ndjsonFrame(event: Event): Uint8Array {
  return encoder.encode(JSON.stringify(event) + "\n");
}
// header: "content-type": "application/x-ndjson", "cache-control": "no-cache"
```

## Backpressure

`controller.desiredSize` reflects how many chunks the consumer's queue will accept. When it drops to `0` or below, the stream is **applying backpressure** — we pause the producer instead of buffering unbounded memory. In the snippet above we wait for `desiredSize > 0` before pushing the next frame.

For a high-fanout producer, wrap with a `TransformStream` and pipe the source through it:

```ts
const backpressure = new TransformStream<Uint8Array, Uint8Array>({
  transform(chunk, controller) {
    // optionally batch / coalesce here
    controller.enqueue(chunk);
  },
});
const piped = stream.pipeThrough(backpressure);
return new Response(piped, { headers });
```

## Disconnect handling

- `request.signal` is aborted by the runtime when the TCP connection drops — listen once and call `abort.abort()`.
- `ReadableStream.cancel(reason)` fires when the consumer (the user agent) cancels — also call `abort.abort(reason)`.
- In `finally`, the producer's `for await … of` loop exits cleanly because the next `signal.aborted` check interrupts it.

## Best practices

- **Honor `controller.desiredSize`** for real backpressure; do not blindly `enqueue` and assume buffering is free.
- **Listen to `request.signal`** in addition to `stream.cancel` so producers stop generating work on disconnect.
- **Use a single `AbortController`** to coordinate producers, then have `request.signal` and `stream.cancel` both call `abort`.
- **Set `cache-control: no-cache, no-transform`** so intermediaries do not try to compress / buffer your stream.
- **Prefer `ReadableStream` over `Response.json()` or accumulating buffers** for any response that grows over time.
- **SSE for browsers, NDJSON for services**: SSE handles reconnection with `Last-Event-ID`; NDJSON is simpler to parse on the server side.