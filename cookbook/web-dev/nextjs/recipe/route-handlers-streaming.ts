export {};

const encoder = new TextEncoder();

type StreamEvent = { id: number; message: string };

async function* produceEvents(signal: AbortSignal, max = 20): AsyncGenerator<StreamEvent> {
  let id = 0;
  while (!signal.aborted) {
    await new Promise((resolve) => setTimeout(resolve, 25));
    id += 1;
    yield { id, message: `event-${id}` };
    if (id >= max) break;
  }
}

function sseFrame(event: StreamEvent): Uint8Array {
  const payload = `id: ${event.id}\nevent: message\ndata: ${JSON.stringify(event)}\n\n`;
  return encoder.encode(payload);
}

function streamingResponse(abort: AbortController, max = 20): Response {
  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      try {
        for await (const event of produceEvents(abort.signal, max)) {
          if (abort.signal.aborted) break;
          while (controller.desiredSize !== null && controller.desiredSize <= 0) {
            await new Promise((resolve) => setTimeout(resolve, 5));
            if (abort.signal.aborted) break;
          }
          controller.enqueue(sseFrame(event));
        }
      } catch (error) {
        controller.error(error instanceof Error ? error : new Error(String(error)));
        return;
      } finally {
        controller.close();
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

async function consume(response: Response, consumerAbort: AbortController): Promise<void> {
  if (response.body === null) throw new Error("no body");
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let received = 0;
  let disconnectAfter = 8;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const text = decoder.decode(value, { stream: true });
      received += 1;
      console.log(`[#${received}] -> ${text.split("\n")[0]}`);
      if (received >= disconnectAfter) {
        console.log(`[consumer] disconnecting after ${disconnectAfter} chunks to test AbortController`);
        consumerAbort.abort(new Error("client closed the tab"));
        reader.cancel("client disconnect").catch(() => {});
        break;
      }
    }
  } finally {
    reader.releaseLock();
  }
}

async function run(): Promise<void> {
  const serverAbort = new AbortController();
  const consumerAbort = new AbortController();
  consumerAbort.signal.addEventListener("abort", () => serverAbort.abort(), { once: true });

  const response = streamingResponse(serverAbort, 50);
  await consume(response, consumerAbort);
  console.log("stream session complete (server should have stopped producing)");
}

void sseFrame;
run().catch((error) => {
  console.error(error);
  process.exit(1);
});