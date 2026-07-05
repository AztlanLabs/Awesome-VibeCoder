# Graceful Shutdown

Drain in-flight requests, close resources, and bound a hard-exit deadline — so deploys and crashes alike leave no client hanging.

> **Runnable example:** [recipe/graceful-shutdown.ts](recipe/graceful-shutdown.ts)
>
> ```bash
> cd recipe && npm install
> npx tsx graceful-shutdown.ts
> ```

## Example scenario

You run behind a load balancer. On `SIGTERM` you must stop accepting new connections, let existing requests finish, and then exit — within a deadline — before the orchestrator force-kills you.

## Tracking connections

```typescript
import { createServer, Server, IncomingMessage, ServerResponse } from "node:http";

const connections = new Set<IncomingMessage | ServerResponse>();
const server = createServer((req, res) => {
  connections.add(req);
  connections.add(res);
  res.on("close", () => {
    connections.delete(req);
    connections.delete(res);
  });
  res.end("ok");
});
```

## The shutdown sequence

```typescript
let shuttingDown = false;

async function shutdown(server: Server, deadlineMs = 8000) {
  if (shuttingDown) return;
  shuttingDown = true;

  server.close();
  for (const c of connections) {
    const res = (c as ServerResponse);
    if (typeof res.end === "function") res.setHeader("Connection", "close");
  }

  const force = setTimeout(() => process.exit(1), deadlineMs);
  force.unref();

  await new Promise<void>((resolve) => server.on("close", () => resolve()));
  clearTimeout(force);
  process.exit(0);
}

process.on("SIGTERM", () => void shutdown(server));
process.on("SIGINT", () => void shutdown(server));
```

## Health check participation

Make your readiness probe reflect shutdown state so traffic stops routing to you immediately:

```typescript
createServer((req, res) => {
  if (req.url === "/ready") {
    res.writeHead(shuttingDown ? 503 : 200).end();
    return;
  }
  res.writeHead(404).end();
}).listen(3001);
```

## Best practices

1. **Set `Connection: close`** on active responses so clients don’t reuse the dying socket.
2. **Pick a deadline shorter than the orchestrator’s kill grace** (typ. 10–30s).
3. **Close idle keep-alives** quickly; long-polling sockets need explicit handling.
4. **Idempotent shutdown** — guard with a boolean so double `SIGINT` never double-closes.
5. **Log the drain**: how many connections, how long until `close`, did you hit the deadline.