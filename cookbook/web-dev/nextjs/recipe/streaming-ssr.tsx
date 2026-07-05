import { Suspense, type ReactNode } from "react";

type ActivityItem = { id: string; text: string; ts: number };

async function fetchActivity(): Promise<ActivityItem[]> {
  await new Promise((resolve) => setTimeout(resolve, 200));
  const now = Date.now();
  return [
    { id: "1", text: "Pushed to main", ts: now - 1000 },
    { id: "2", text: "Opened PR #42", ts: now - 60000 },
    { id: "3", text: "Commented on issue #7", ts: now - 120000 },
  ];
}

async function ActivityFeed(): Promise<ReactNode> {
  const items = await fetchActivity();
  return (
    <ul>
      {items.map((item) => (
        <li key={item.id}>
          <time dateTime={new Date(item.ts).toISOString()}>
            {new Date(item.ts).toLocaleTimeString()}
          </time>
          {" — "}
          {item.text}
        </li>
      ))}
    </ul>
  );
}

function LoadingFallback(): ReactNode {
  return <div aria-busy="true">Loading activity…</div>;
}

function DashboardPage(): ReactNode {
  return (
    <main>
      <h1>Dashboard</h1>
      <p>Quick overview of your account.</p>
      <Suspense fallback={<LoadingFallback />}>
        <ActivityFeed />
      </Suspense>
    </main>
  );
}

const CHUNKS: string[] = [];

function emit(label: string, chunk: string): void {
  CHUNKS.push(`<!-- ${label} -->\n${chunk}`);
  console.log(`[flush] ${label}:\n${chunk.trimEnd()}\n`);
}

type Resolved<T> = { pending: false; value: T };
type Pending = { pending: true };
type Status<T> = Resolved<T> | Pending;

function isPending<T>(s: Status<T>): s is Pending {
  return s.pending;
}

async function renderStream(): Promise<void> {
  console.log("--- streaming start (shell + fallback) ---");
  emit("shell", "<main><h1>Dashboard</h1><p>Quick overview of your account.</p>");
  emit("fallback", '<div aria-busy="true">Loading activity…</div>');

  const feed: Status<ReactNode> = await { pending: true } as Status<ReactNode>;
  if (isPending(feed)) {
    const resolved = await fetchActivity();
    const list = (
      <ul>
        {resolved.map((item) => (
          <li key={item.id}>
            <time dateTime={new Date(item.ts).toISOString()}>
              {new Date(item.ts).toLocaleTimeString()}
            </time>
            {" — "}
            {item.text}
          </li>
        ))}
      </ul>
    );
    emit("feed-chunk", renderToString(list));
  }

  console.log("--- stream closed ---");
  console.log(`total flushed chunks: ${CHUNKS.length}`);
}

function renderToString(node: ReactNode): string {
  if (typeof node === "string") return node;
  if (typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(renderToString).join("");
  if (node != null && typeof node === "object" && "type" in node) {
    return renderElement(node as { type: unknown; props: Record<string, unknown> });
  }
  return "";
}

function renderElement(el: { type: unknown; props: Record<string, unknown> }): string {
  const { type, props } = el;
  const children = renderToString(props.children as ReactNode);
  if (typeof type === "function") {
    const fn = type as (p: Record<string, unknown>) => ReactNode;
    return renderToString(fn(props));
  }
  const tag = String(type);
  const attrs = Object.entries(props)
    .filter(([k, v]) => k !== "children" && typeof v !== "function" && v !== false && v != null)
    .map(([k, v]) => ` ${k}="${String(v).replace(/"/g, "&quot;")}"`)
    .join("");
  return `<${tag}${attrs}>${children}</${tag}>`;
}

void DashboardPage;

renderStream().catch((error) => {
  console.error(error);
  process.exit(1);
});