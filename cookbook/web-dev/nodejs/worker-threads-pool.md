# Worker Threads Pool

Offload CPU-bound work to a fixed pool of `worker_threads` with a task queue, error propagation, and graceful termination.

> **Runnable example:** [recipe/worker-threads-pool.ts](recipe/worker-threads-pool.ts)
>
> ```bash
> cd recipe && npm install
> npx tsx worker-threads-pool.ts
> ```

## Example scenario

Image hashing, compression, or big parses block the event loop. You don’t want to spawn-and-await a thread per task; you want a bounded, reused pool with backpressure.

## The pool

```typescript
import { Worker } from "node:worker_threads";
import { fileURLToPath } from "node:url";

interface Task<T> {
  resolve: (v: T) => void;
  reject: (e: unknown) => void;
  payload: unknown;
}

export class WorkerPool<T = unknown> {
  private workers: Worker[] = [];
  private idle: Worker[] = [];
  private queue: Task<T>[] = [];
  private timer: NodeJS.Timeout | null = null;

  constructor(
    private readonly workerUrl: URL,
    private readonly size = 4,
  ) {
    for (let i = 0; i < size; i++) {
      const w = new Worker(fileURLToPath(workerUrl));
      this.workers.push(w);
      this.idle.push(w);
    }
  }

  run<R = T>(payload: unknown): Promise<R> {
    return new Promise<R>((resolve, reject) => {
      this.queue.push({ resolve, reject, payload } as Task<T>);
      this.pump();
    });
  }

  private pump() {
    while (this.idle.length && this.queue.length) {
      const w = this.idle.shift()!;
      const task = this.queue.shift()!;
      const onMessage = (v: T) => {
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

  async close(timeoutMs = 5000) {
    await Promise.all(this.workers.map((w) => w.terminate()));
    this.workers = [];
    this.idle = [];
    this.queue = [];
  }
}
```

## The worker

```typescript
import { parentPort } from "node:worker_threads";

parentPort?.on("message", (payload: { n: number }) => {
  let total = 0;
  for (let i = 0; i < payload.n; i++) total += i;
  parentPort?.postMessage(total);
});
```

## Best practices

1. **Bound pool size to CPU count** — `os.availableParallelism()` is a good default.
2. **Reuse workers** across tasks; `new Worker` per request leaks and stalls.
3. **Propagate errors** with `worker.once('error')` and reject the task promise.
4. **Terminate on shutdown** and attach a deadline; orphaned workers keep the process alive.
5. **Transfer `ArrayBuffer`** with the transfer list for zero-copy of large buffers.