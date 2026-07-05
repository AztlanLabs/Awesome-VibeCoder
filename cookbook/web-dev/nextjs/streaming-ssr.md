# Streaming SSR

Stream a Server Component tree to the browser using `Suspense` boundaries and `loading.tsx` so users see the shell immediately while slow data fetches resolve in the background.

> **Runnable example:** [recipe/streaming-ssr.tsx](recipe/streaming-ssr.tsx)
>
> ```bash
> cd recipe && npm install
> npx tsx streaming-ssr.tsx
> # or: npm run streaming-ssr
> ```

## Example scenario

A dashboard page renders a header (fast) and a "Latest activity" feed that comes from a slow database call (~1.5s). You want the shell to paint right away and the feed to stream in once it is ready, instead of waiting for the whole page to be ready.

## Page with `Suspense`

```tsx
// app/dashboard/page.tsx
import { Suspense } from "react";
import { ActivityFeed } from "./ActivityFeed";

export default function DashboardPage() {
  return (
    <main>
      <h1>Dashboard</h1>
      <p>Quick overview of your account.</p>
      <Suspense fallback={<div aria-busy="true">Loading activity…</div>}>
        <ActivityFeed />
      </Suspense>
    </main>
  );
}
```

## Slow Server Component

```tsx
// app/dashboard/ActivityFeed.tsx
import { unstable_noStore as noStore } from "next/cache";

// Slow upstream; we deliberately don't cache at the data layer.
async function fetchActivity(): Promise<Array<{ id: string; text: string; ts: number }>> {
  await new Promise((resolve) => setTimeout(resolve, 1500));
  const now = Date.now();
  return [
    { id: "1", text: "Pushed to main", ts: now - 1000 },
    { id: "2", text: "Opened PR #42", ts: now - 60000 },
    { id: "3", text: "Commented on issue #7", ts: now - 120000 },
  ];
}

export async function ActivityFeed() {
  noStore();
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
```

## `loading.tsx` fallback

A file placed alongside `page.tsx` covers the **whole route** while it streams. Per-segment `Suspense` (as above) is preferred because it lets independent pieces resolve at their own pace.

```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return (
    <main aria-busy="true">
      <h1>Dashboard</h1>
      <p>Loading…</p>
    </main>
  );
}
```

## Partial HTML flush (what actually happens)

Next.js renders the page shell first and emits `<script>`s that swap the fallback element once the suspended chunk resolves. The browser:

1. Receives and paints the shell + `Suspense` fallback immediately.
2. Keeps the connection open; as `ActivityFeed` resolves, Next.js streams the new chunk and React swaps the fallback out without crashing client JS.

This is why you should **put `Suspense` around the slowest async subtree**, not the whole page — otherwise nothing paints until everything is ready.

## Client-only UI inside the shell

If your shell needs interactivity (e.g. a theme toggle), move just that piece into a `'use client'` component and import it directly in the Server Component:

```tsx
// app/dashboard/ThemeToggle.tsx
"use client";
import { useState } from "react";
export function ThemeToggle() {
  const [dark, setDark] = useState(false);
  return <button onClick={() => setDark((v) => !v)}>{dark ? "🌙" : "☀️"}</button>;
}

// Shell (Server Component):
import { ThemeToggle } from "./ThemeToggle";
<Suspense fallback={<p>Loading activity…</p>}><ActivityFeed /></Suspense>
<ThemeToggle />
```

> **Do not use `next/dynamic` with `{ ssr: false }` inside a Server Component.** Import the Client Component directly as shown above.

## Best practices

- **Wrap the slowest subtree in `Suspense`, not the whole page**, so the shell paints instantly.
- **Use `loading.tsx` only for coarse, whole-route fallbacks**; prefer explicit `<Suspense>` for fine-grained streaming.
- **Call `unstable_noStore()` (or set dynamic `fetch` options) on data that must be fresh**; otherwise Next.js may cache the slow fetch and defeat the streaming demo in production builds.
- **Keep async children thin** — each `await` is a stream boundary; avoid one giant async component.
- **Never `next/dynamic({ ssr: false })` in a Server Component.** Move interactive UI into a `'use client'` file and import it directly.
- **Test the streaming behavior in `next dev` and a production build** — `next dev` does not always flush chunks the same way.