# ISR On-Demand

Keep pages fast with static rendering, but invalidate specific paths or cache tags on demand via `revalidatePath` and `revalidateTag` — from a Route Handler **and** a Server Action — while pre-rendering known dynamic params with `generateStaticParams`.

> **Runnable example:** [recipe/isr-on-demand.ts](recipe/isr-on-demand.ts)
>
> ```bash
> cd recipe && npm install
> npx tsx isr-on-demand.ts
> # or: npm run isr-on-demand
> ```

## Example scenario

A product catalog at `/products/[slug]`. Pages should be statically generated at build time, revalidated every 60 seconds in the background (stale-while-revalidate), and **immediately** refreshed when a webhook fires or an admin presses a "Republish" button.

## Static page

```tsx
// app/products/[slug]/page.tsx
import { notFound } from "next/navigation";

type Product = { id: string; name: string; price: number; updatedAt: number };

async function getProduct(slug: string): Promise<Product> {
  const res = await fetch(`https://api.example.com/products/${slug}`, {
    next: { revalidate: 60, tags: [`product:${slug}`, "products"] },
  });
  if (!res.ok) notFound();
  return (await res.json()) as Product;
}

export async function generateStaticParams(): Promise<Array<{ slug: string }>> {
  const res = await fetch("https://api.example.com/products", { cache: "no-store" });
  const items = (await res.json()) as Array<{ slug: string }>;
  return items.slice(0, 20);
}

// Default export forces ISR: a static page that can be revalidated.
export const dynamicParams = true;

export default async function ProductPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const product = await getProduct(slug);
  return (
    <article>
      <h1>{product.name}</h1>
      <p>Price: ${product.price.toFixed(2)}</p>
      <p>Last updated: {new Date(product.updatedAt).toISOString()}</p>
    </article>
  );
}
```

Key bits:

- `next: { revalidate: 60 }` — serve a cached version for 60s, then refresh in the background.
- `next: { tags: [...] }` — associate the fetch with cache tags for `revalidateTag`.
- `generateStaticParams` — pre-render known slugs at build time.
- `dynamicParams = true` — unknown slugs still render on demand instead of 404 (and become ISR too).
- `params` is a **Promise** in Next.js 16 — always `await` it.

## Route Handler: webhook-triggered revalidation

```ts
// app/api/webhooks/products/route.ts
import { revalidatePath, revalidateTag } from "next/cache";
import { NextResponse } from "next/server";

export async function POST(request: Request): Promise<Response> {
  const body = (await request.json()) as { type?: "product" | "all"; slug?: string };
  const secret = request.headers.get("x-webhook-secret");
  if (secret !== process.env.WEBHOOK_SECRET) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  if (body.type === "product" && body.slug) {
    revalidateTag(`product:${body.slug}`);
    revalidatePath(`/products/${body.slug}`);
    return NextResponse.json({ ok: true, revalidated: body.slug });
  }

  revalidateTag("products");
  revalidatePath("/products", "layout");
  return NextResponse.json({ ok: true, revalidated: "all" });
}
```

## Server Action: admin "republish" button

```ts
// app/products/revalidate.ts
"use server";
import { revalidatePath, revalidateTag } from "next/cache";
import { redirect } from "next/navigation";

export async function republishProduct(slug: string): Promise<void> {
  revalidateTag(`product:${slug}`);
  revalidatePath(`/products/${slug}`);
  redirect(`/products/${slug}`);
}
```

```tsx
// app/products/[slug]/RepublishButton.tsx
"use client";
import { useTransition } from "react";
import { republishProduct } from "../../products/revalidate";

export function RepublishButton({ slug }: { slug: string }) {
  const [pending, startTransition] = useTransition();
  return (
    <button
      type="button"
      disabled={pending}
      onClick={() => startTransition(() => { void republishProduct(slug); })}
    >
      {pending ? "Republishing…" : "Republish"}
    </button>
  );
}
```

## When to use which API

| API                              | Use when…                                                                                |
| -------------------------------- | ---------------------------------------------------------------------------------------- |
| `next: { revalidate: N }`        | You accept eventual consistency; refresh in the background every `N` seconds.          |
| `revalidatePath(path)`           | You know the exact path; refresh after a mutation on that route.                         |
| `revalidatePath(path, "layout")` | All routes under that path segment share state and should all refresh together.         |
| `revalidateTag(tag)`             | Multiple routes share upstream data; one webhook should refresh all of them.            |

In Next.js 16 prefer **Cache Components** (`use cache` + `cacheTag`/`cacheLife`) for new code, with `revalidateTag(tag, "max")` for stale-while-revalidate behavior. `revalidateTag` with a single argument is legacy.

## Best practices

- **Tag every cacheable fetch** so a webhook can refresh many routes at once.
- **Pre-render common params** with `generateStaticParams`; let `dynamicParams` handle the long tail.
- **Always `await params`** in Next.js 16 — it is a Promise.
- **Guard webhooks** with a secret header; never accept unauthenticated revalidation requests.
- **Prefer `revalidateTag` over `revalidatePath`** when many routes share upstream data — fewer cache invalidations.
- **Don't accumulate many short revalidate windows**: pick one sensible window per data source; use tags for immediate invalidation.
- **In Next.js 16 prefer Cache Components** (`cacheComponents: true` + `use cache`) for new code, and pair with `revalidateTag(tag, "max")` for stale-while-revalidate.