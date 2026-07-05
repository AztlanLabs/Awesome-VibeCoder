import { createServer, type Server, type ServerResponse } from "node:http";

const PORT = Number(process.env.PORT ?? 4100);
const connections = new Set<ServerResponse>();
let shuttingDown = false;

const server: Server = createServer((_, res) => {
  if (shuttingDown) {
    res.writeHead(503).end("shutting down");
    return;
  }
  connections.add(res);
  res.on("close", () => connections.delete(res));
  res.writeHead(200).end("ok");
});

server.listen(PORT, () => {
  console.log(`graceful-shutdown listening on http://localhost:${PORT}`);
});

const probe = createServer((req, res) => {
  if (req.url === "/ready") {
    res.writeHead(shuttingDown ? 503 : 200).end();
    return;
  }
  res.writeHead(404).end();
});
probe.listen(PORT + 1);

async function shutdown(): Promise<void> {
  if (shuttingDown) return;
  shuttingDown = true;
  console.log("SIGTERM received — draining");

  server.close();
  probe.close();
  server.removeAllListeners();
  for (const res of connections) {
    res.setHeader("Connection", "close");
  }

  const force = setTimeout(() => {
    console.error("drain deadline hit — force exiting");
    process.exit(1);
  }, 5000);
  force.unref();

  await new Promise<void>((resolve) => server.on("close", () => resolve()));
  clearTimeout(force);
  console.log(`drained. in-flight at exit: ${connections.size}`);
  process.exit(0);
}

process.on("SIGTERM", () => void shutdown());
process.on("SIGINT", () => void shutdown());