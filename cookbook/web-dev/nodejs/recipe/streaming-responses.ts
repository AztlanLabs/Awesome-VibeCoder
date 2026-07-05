import { createServer } from "node:http";

const PORT = Number(process.env.PORT ?? 4000);

const server = createServer((req, res) => {
  if (req.url !== "/stream") {
    res.writeHead(404).end("not found");
    return;
  }

  const ac = new AbortController();
  req.on("close", () => ac.abort());

  res.writeHead(200, {
    "Content-Type": "text/plain; charset=utf-8",
    "Transfer-Encoding": "chunked",
    "Cache-Control": "no-transform",
  });

  let i = 0;
  const timer = setInterval(() => {
    if (ac.signal.aborted) {
      clearInterval(timer);
      return;
    }
    if (i >= 5) {
      clearInterval(timer);
      res.end("done\n");
      return;
    }
    const ok = res.write(`chunk ${i}\n`);
    if (!ok) res.once("drain", () => res.write(`resumed ${i}\n`));
    i++;
  }, 200);
});

server.listen(PORT, () => {
  console.log(`streaming-responses listening on http://localhost:${PORT}/stream`);
  console.log("test with:  curl -N http://localhost:%s/stream", PORT);
});