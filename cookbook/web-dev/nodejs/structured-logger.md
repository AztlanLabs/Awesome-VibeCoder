# Structured Logger

A leveled JSON logger with child context, redaction, and pluggable async sinks — the smallest thing you can ship before reaching for `pino`.

> **Runnable example:** [recipe/structured-logger.ts](recipe/structured-logger.ts)
>
> ```bash
> cd recipe && npm install
> npx tsx structured-logger.ts
> ```

## Example scenario

You need logs you can grep and aggregate: stable JSON shape, per-request child bindings (request id, user id), secrets redacted, non-blocking writes to stdout/files.

## The logger

```typescript
type Level = "debug" | "info" | "warn" | "error";
const ORDER: Record<Level, number> = { debug: 10, info: 20, warn: 30, error: 40 };

export interface Logger {
  child(bindings: Record<string, unknown>): Logger;
  debug(msg: string, data?: Record<string, unknown>): void;
  info(msg: string, data?: Record<string, unknown>): void;
  warn(msg: string, data?: Record<string, unknown>): void;
  error(msg: string, data?: Record<string, unknown>): void;
}

export function createLogger(
  base: Record<string, unknown> = {},
  minLevel: Level = "info",
  sink: (line: string) => void = (l) => process.stdout.write(l),
): Logger {
  const redact = (o: Record<string, unknown>): Record<string, unknown> => {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(o)) {
      if (/password|token|secret|cookie/i.test(k)) out[k] = "[REDACTED]";
      else out[k] = v;
    }
    return out;
  };

  const emit = (level: Level, msg: string, data?: Record<string, unknown>) => {
    if (ORDER[level] < ORDER[minLevel]) return;
    sink(JSON.stringify({ time: Date.now(), level, msg, ...base, ...(data ? redact(data) : {}) }) + "\n");
  };

  return {
    child: (bindings) => createLogger({ ...base, ...bindings }, minLevel, sink),
    debug: (m, d) => emit("debug", m, d),
    info: (m, d) => emit("info", m, d),
    warn: (m, d) => emit("warn", m, d),
    error: (m, d) => emit("error", m, d),
  };
}
```

## Async, non-blocking sinks

Use a buffered async sink so a slow destination never blocks your hot path:

```typescript
export function asyncFileSink(stream: NodeJS.WriteStream) {
  let pending: string[] = [];
  let flushing = false;
  const flush = async () => {
    if (flushing) return;
    flushing = true;
    while (pending.length) {
      const batch = pending.join("");
      pending = [];
      await new Promise<void>((r) => stream.write(batch, () => r()));
    }
    flushing = false;
  };
  return (line: string) => {
    pending.push(line);
    void flush();
  };
}
```

## Usage with child bindings

```typescript
const log = createLogger({ service: "billing" });
const reqLog = log.child({ requestId: "req_42" });
reqLog.info("charge started", { userId: "u_1", password: "should-not-leak" });
```

## Best practices

1. **One JSON object per line** — never pretty-print in production.
2. **Log `time` as epoch millis or ISO**; pick one and stay consistent.
3. **Redact at the edge** — never trust upstream to scrub secrets.
4. **Child loggers over manual spreading** — preserve request id chains.
5. **Async sinks must not throw** — wrap with `try/catch` and emit a fallback `console.error`.