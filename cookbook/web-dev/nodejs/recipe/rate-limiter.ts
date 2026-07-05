import { createServer, type IncomingMessage, type ServerResponse } from "node:http";

interface Bucket {
  tokens: number;
  last: number;
}

export function tokenBucket(capacity: number, refillPerSec: number) {
  const store = new Map<string, Bucket>();
  return (key: string): boolean => {
    const now = Date.now();
    const b = store.get(key) ?? { tokens: capacity, last: now };
    b.tokens = Math.min(capacity, b.tokens + (now - b.last) * (refillPerSec / 1000));
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

export function rateLimit(opts: {
  capacity: number;
  refillPerSec: number;
  max: number;
  windowMs: number;
}) {
  const bucket = tokenBucket(opts.capacity, opts.refillPerSec);
  const window = slidingWindow(opts.max, opts.windowMs);
  return (req: IncomingMessage, res: ServerResponse): boolean => {
    const key = (req.socket.remoteAddress ?? "anon") + ":" + (req.url ?? "");
    if (!bucket(key) || !window(key)) {
      res.writeHead(429, { "Retry-After": "1" }).end("rate limit exceeded\n");
      return false;
    }
    return true;
  };
}

const PORT = Number(process.env.PORT ?? 4200);
const limiter = rateLimit({ capacity: 5, refillPerSec: 2, max: 10, windowMs: 10_000 });

createServer((req, res) => {
  if (!limiter(req, res)) return;
  res.writeHead(200, { "Content-Type": "text/plain" }).end("ok\n");
}).listen(PORT, () => {
  console.log(`rate-limiter listening on http://localhost:${PORT}`);
  console.log("try:");
  console.log(`  for i in $(seq 1 15); do curl -s -o /dev/null -w "%{http_code}\\n" http://localhost:${PORT}/; sleep 0.1; done`);
});