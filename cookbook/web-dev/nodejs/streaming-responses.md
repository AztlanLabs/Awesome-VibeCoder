# Streaming HTTP Responses

Flush chunks to the wire as work completes — keep users in the loop and let clients start rendering before the full payload is ready.

> **Runnable example:** [recipe/streaming-responses.ts](recipe/streaming-responses.ts)
>
> ```bash
> cd recipe && npm install
> npx tsx streaming-responses.ts
> ```

## Example scenario

You generate a long report or pull from many upstream services. Buffering the whole thing and sending one `200 OK` is slow and hides progress. You want backpressure-aware streaming with `Transfer-Encoding: chunked`.

## Minimal chunked server

```typescript
import { createServer } from "node:http";

const server = createServer((req, res) => {
  res.writeHead(200, {
    "Content-Type": "text/plain; charset=utf-8",
    "Transfer-Encoding": "chunked",
    "Cache-Control": "no-transform",
  });

  let i = 0;
  const timer = setInterval(() => {
    if (i >= 5) {
      clearInterval(timer);
      res.end("done\n");
      return;
    }
    const ok = res.write(`chunk ${i}\n`);
    if (!ok) {
      res.once("drain", () => res.write(`resumed ${i}\n`));
    }
    i++;
  }, 200);
});

server.listen(3000);
```

## Streaming a `ReadableStream`

```typescript
import { createServer } from "node:http";

const stream = new ReadableStream({
  start(controller) {
    for (let i = 0; i < 3; i++) {
      controller.enqueue(new TextEncoder().encode(`item ${i}\n`));
    }
    controller.close();
  },
});

const server = createServer((req, res) => {
  res.writeHead(200, { "Content-Type": "text/plain" });
  for await (const chunk of stream) res.write(chunk);
  res.end();
});

server.listen(3001);
```

## Backpressure & cancellation

- Use the boolean return of `res.write()` and the `drain` event — it’s the only correct backpressure signal.
- Wire `req` close to an `AbortController` so producers stop generating after the client disconnects:

```typescript
const ac = new AbortController();
req.on("close", () => ac.abort());
```

## Best practices

1. **Never buffer large payloads** — chunk and flush incrementally.
2. **Honor `res.write()`’s boolean** and wait for `drain`.
3. **Listen for `req.on("close")`** to cancel upstream work and avoid orphaned connections.
4. **Set `Cache-Control: no-transform`** so intermediaries don’t buffer your stream.
5. **Pair with `Content-Type` hints** that a client can progressively parse (NDJSON, SSE).