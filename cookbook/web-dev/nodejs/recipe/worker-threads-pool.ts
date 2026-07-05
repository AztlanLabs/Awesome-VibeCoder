import { Worker } from "node:worker_threads";
import { availableParallelism } from "node:os";

interface Task {
  resolve: (v: number) => void;
  reject: (e: unknown) => void;
  payload: unknown;
}

export class WorkerPool {
  private workers: Worker[] = [];
  private idle: Worker[] = [];
  private queue: Task[] = [];

  constructor(workerUrl: URL, size = Math.min(4, availableParallelism())) {
    for (let i = 0; i < size; i++) {
      const w = new Worker(fileURLToPath(workerUrl));
      this.workers.push(w);
      this.idle.push(w);
    }
  }

  run(payload: unknown): Promise<number> {
    return new Promise<number>((resolve, reject) => {
      this.queue.push({ resolve, reject, payload });
      this.pump();
    });
  }

  private pump(): void {
    while (this.idle.length && this.queue.length) {
      const w = this.idle.shift()!;
      const task = this.queue.shift()!;
      const onMessage = (v: number) => {
        w.off("error", onError);
        this.idle.push(w);
        task.resolve(v);
        this.pump();
      };
      const onError = (e: unknown) => {
        w.off("message", onMessage);
        task.reject(e);
      };
      w.once("message", onMessage);
      w.once("error", onError);
      w.postMessage(task.payload);
    }
  }

  async close(): Promise<void> {
    await Promise.all(this.workers.map((w) => w.terminate()));
    this.workers = [];
    this.idle = [];
    this.queue = [];
  }
}

// Inline worker via Blob URL so the recipe is a single file
const workerScript = `
import { parentPort } from "node:worker_threads";
parentPort.on("message", (payload) => {
  let total = 0;
  for (let i = 0; i < payload.n; i++) total += i;
  parentPort.postMessage(total);
});
`;
const blob = new Blob([workerScript], { type: "text/javascript" });
const blobUrl = URL.createObjectURL(blob) as unknown as URL;

async function main() {
  const pool = new WorkerPool(blobUrl, 3);
  const tasks = Array.from({ length: 6 }, (_, i) => pool.run({ n: 50_000_000 + i * 1000 }));
  const results = await Promise.all(tasks);
  console.log("results:", results);
  await pool.close();
  URL.revokeObjectURL(blobUrl.href);
}

void main();