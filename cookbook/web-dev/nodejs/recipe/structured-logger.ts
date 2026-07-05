type Level = "debug" | "info" | "warn" | "error";
const ORDER: Record<Level, number> = { debug: 10, info: 20, warn: 30, error: 40 };

export interface Logger {
  child(bindings: Record<string, unknown>): Logger;
  debug(msg: string, data?: Record<string, unknown>): void;
  info(msg: string, data?: Record<string, unknown>): void;
  warn(msg: string, data?: Record<string, unknown>): void;
  error(msg: string, data?: Record<string, unknown>): void;
}

const SECRET = /password|token|secret|cookie|authorization/i;

function redact(o: Record<string, unknown>): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(o)) {
    out[k] = SECRET.test(k) ? "[REDACTED]" : v;
  }
  return out;
}

export function createLogger(
  base: Record<string, unknown> = {},
  minLevel: Level = "info",
  sink: (line: string) => void = (l) => process.stdout.write(l),
): Logger {
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

const log = createLogger({ service: "demo" });
const reqLog = log.child({ requestId: "req_42" });

reqLog.info("charge started", { userId: "u_1", password: "should-not-leak" });
reqLog.warn("slow upstream", { latencyMs: 1200 });
reqLog.error("payment failed", { code: "CARD_DECLINED" });
log.debug("below threshold — skipped");

console.log("\n--- min level: debug ---");
createLogger({}, "debug").debug("now visible", { x: 1 });