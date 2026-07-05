# Token-Bucket Rate Limiter

A `Map`-backed token-bucket + sliding-window limiter exposed as composable `http` middleware.

> **Runnable example:** [recipe/rate-limiter.ts](recipe/rate-limiter.ts)
>
> ```bash
> cd recipe && npm install
> npx tsx rate-limiter.ts
> ```

## Example scenario

You expose a JSON API and need to throttle per-IP requests — burst-tolerant (token bucket) plus a hard sliding window ceiling to stop sustained abuse.

## Token bucket

```typescript
interface Bucket {
  tokens: number;
  last: number;
}

export function tokenBucket(capacity: number, refillPerMs: number) {
  const store = new Map<string, Bucket>();
  return (key: string): boolean => {
    const now = Date.now();
    const b = store.get(key) ?? { tokens: capacity, last: now };
    b.tokens = Math.min(capacity, b.tokens + (now - b.last) * refillPerMs);
    b.last = now;
    if (b.tokens < 1) {
      store.set(key, b);
      return false;
    }
    b.tokens -= 1;
    store.set(key, b);
    return true;
  };
}
```

## Sliding window ceiling

```typescript
export function slidingWindow(max: number, windowMs: number) {
  const store = new Map<string, number[]>();
  return (key: string): boolean => {
    const now = Date.now();
    const arr = (store.get(key) ?? []).filter((t) => t > now - windowMs);
    if (arr.length >= max) {
      store.set(key, arr);
      return false;
    }
    arr.push(now);
    store.set(key, arr);
    return true;
  };
}
```

## Composed middleware

```typescript
import type { IncomingMessage, ServerResponse } from "node:http";

export function rateLimit(opts: { capacity: number; refillPerSec: number; max: number; windowMs: number }) {
  const bucket = tokenBucket(opts.capacity, opts.refillPerSec / 1000);
  const window = slidingWindow(opts.max, opts.windowMs);
  return (req: IncomingMessage, res: ServerResponse): boolean => {
    const key = (req.socket.remoteAddress ?? "anon") + ":" + (req.url ?? "");
    if (!bucket(key) || !window(key)) {
      res.writeHead(429, { "Retry-After": "1" }).end("rate limit exceeded");
      return false;
    }
    return true;
  };
}
```

## Best practices

1. **Identify by a stable key** — IP alone breaks behind NAT; pair with auth id when possible.
2. **Return `Retry-After`** so well-behaved clients back off.
3. **Bound the `Map`** with eviction or a TTL sweep — unbounded stores leak memory.
4. **Compose two algorithms** — token bucket for burst parity, sliding window for a hard cap.
5. **Offload to Redis** only when you exceed a single process; `Map` beats it on latency.