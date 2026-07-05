export {};

type Entry<T> = { value: T; tags: string[]; expiresAt: number };

class IsrCache<T> {
  private store = new Map<string, Entry<T>>();
  private subscribers = new Map<string, Array<(key: string) => void>>();

  set(key: string, value: T, tags: string[], ttlMs: number): void {
    this.store.set(key, { value, tags, expiresAt: Date.now() + ttlMs });
    for (const cb of this.subscribers.get(key) ?? []) cb(key);
  }

  get(key: string): Entry<T> | undefined {
    const entry = this.store.get(key);
    if (!entry) return undefined;
    if (Date.now() > entry.expiresAt) {
      this.store.delete(key);
      return undefined;
    }
    return entry;
  }

  revalidateTag(tag: string, mode: "max" | "default" = "max"): number {
    let touched = 0;
    for (const [key, entry] of this.store) {
      if (entry.tags.includes(tag)) {
        this.store.delete(key);
        touched += 1;
        for (const cb of this.subscribers.get(key) ?? []) cb(key);
      }
    }
    console.log(`revalidateTag(${tag}, ${mode}) -> invalidated ${touched} entries`);
    return touched;
  }

  revalidatePath(path: string): number {
    const existed = this.store.delete(path);
    for (const cb of this.subscribers.get(path) ?? []) cb(path);
    console.log(`revalidatePath(${path}) -> ${existed ? "invalidated" : "miss"}`);
    return existed ? 1 : 0;
  }

  observe(key: string, cb: (key: string) => void): () => void {
    const list = this.subscribers.get(key) ?? [];
    list.push(cb);
    this.subscribers.set(key, list);
    return () => {
      const next = (this.subscribers.get(key) ?? []).filter((fn) => fn !== cb);
      if (next.length === 0) this.subscribers.delete(key);
      else this.subscribers.set(key, next);
    };
  }

  size(): number {
    return this.store.size;
  }
}

type Product = { id: string; name: string; price: number; updatedAt: number };

async function fetchProduct(slug: string): Promise<Product> {
  await new Promise((resolve) => setTimeout(resolve, 50));
  return { id: slug, name: `Widget ${slug}`, price: 9.99, updatedAt: Date.now() };
}

async function isrFetch(cache: IsrCache<Product>, slug: string): Promise<Product> {
  const entry = cache.get(`/products/${slug}`);
  if (entry) {
    console.log(`[stale] served cached ${slug} (age ${Date.now() - entry.value.updatedAt}ms)`);
    if (Date.now() > entry.expiresAt - 1) {
      fetchProduct(slug).then((fresh) => cache.set(`/products/${slug}`, fresh, [`product:${slug}`, "products"], 1000));
    }
    return entry.value;
  }
  const product = await fetchProduct(slug);
  cache.set(`/products/${slug}`, product, [`product:${slug}`, "products"], 1000);
  return product;
}

async function webhook(cache: IsrCache<Product>, slug: string): Promise<void> {
  cache.revalidateTag(`product:${slug}`, "max");
  cache.revalidatePath(`/products/${slug}`);
}

async function run(): Promise<void> {
  const cache = new IsrCache<Product>();

  console.log("building static params: [a, b, c]");
  for (const slug of ["a", "b", "c"]) {
    await isrFetch(cache, slug);
  }
  console.log(`cache size after build: ${cache.size()}`);

  console.log("\nrequest #1 for /products/a (cached):");
  await isrFetch(cache, "a");

  console.log("\nwebhook fires for product a:");
  await webhook(cache, "a");

  let refetched = false;
  const unobserve = cache.observe("/products/a", () => { refetched = true; });
  console.log("request #2 for /products/a (post-invalidation -> fresh fetch):");
  await isrFetch(cache, "a");
  console.log(`observer fired: ${refetched}`);

  console.log("\nrevalidateTag('products', 'max') -> refresh everything:");
  cache.revalidateTag("products", "max");
  console.log(`cache size after global revalidation: ${cache.size()}`);

  unobserve();
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});