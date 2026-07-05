# Middleware Auth

Protect routes in `middleware.ts` with a JWT-style cookie check, redirect unauthenticated users, rewrite internal URLs, and scope the middleware to a typed `matcher`.

> **Runnable example:** [recipe/middleware-auth.ts](recipe/middleware-auth.ts)
>
> ```bash
> cd recipe && npm install
> npx tsx middleware-auth.ts
> # or: npm run middleware-auth
> ```

## Example scenario

You have:

- Public routes: `/`, `/login`, `/signup`, and everything under `/public/*`.
- Protected dashboard: `/dashboard/*`.
- An API proxy that should be rewritten to `/api/internal/*` when the request comes from an authenticated session.

A single `middleware.ts` runs on the Edge runtime before every matched request, validates a JWT stored in the `session` cookie, and either redirects to `/login?from=…`, rewrites the URL, or passes through.

## Middleware

```ts
// middleware.ts
import { NextResponse, type NextRequest } from "next/server";

const PUBLIC_PATHS = ["/", "/login", "/signup"];

function isPublic(pathname: string): boolean {
  if (PUBLIC_PATHS.includes(pathname)) return true;
  if (pathname.startsWith("/public/")) return true;
  if (pathname.startsWith("/_next/")) return true;
  if (pathname.startsWith("/favicon.ico")) return true;
  return false;
}

function verifyToken(token: string | undefined): { sub: string } | null {
  if (!token) return null;
  const parts = token.split(".");
  if (parts.length !== 3) return null;
  try {
    const payload = Buffer.from(parts[1], "base64url").toString("utf8");
    const parsed = JSON.parse(payload) as { sub?: unknown; exp?: number };
    if (typeof parsed.sub !== "string" || parsed.sub.length === 0) return null;
    if (typeof parsed.exp === "number" && parsed.exp * 1000 < Date.now()) return null;
    return { sub: parsed.sub };
  } catch {
    return null;
  }
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const session = request.cookies.get("session")?.value;
  const user = verifyToken(session);

  if (isPublic(pathname)) {
    if (user && pathname === "/login") {
      const url = request.nextUrl.clone();
      url.pathname = "/dashboard";
      return NextResponse.redirect(url);
    }
    return NextResponse.next();
  }

  if (!user) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    url.searchParams.set("from", pathname);
    return NextResponse.redirect(url);
  }

  if (pathname.startsWith("/api/proxy/")) {
    const url = request.nextUrl.clone();
    url.pathname = url.pathname.replace(/^\/api\/proxy/, "/api/internal");
    const res = NextResponse.rewrite(url);
    res.headers.set("x-auth-user", user.sub);
    return res;
  }

  const res = NextResponse.next();
  res.headers.set("x-auth-user", user.sub);
  return res;
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico).*)",
    "/api/proxy/:path*",
  ],
};
```

### Notes on the matcher

- The negative lookahead `((?!_next/static|_next/image|favicon.ico).*)` excludes static assets so middleware only runs on real routes.
- Explicitly add `/api/proxy/:path*` so the rewrite always matches even with broad exclusions.
- The `matcher` runs on the Edge runtime; keep the code tiny and dependency-free.

## Login Route Handler (issues token)

```ts
// app/api/login/route.ts
import { NextResponse } from "next/server";

function sign(payload: Record<string, unknown>): string {
  const header = Buffer.from(JSON.stringify({ alg: "HS256", typ: "JWT" })).toString("base64url");
  const body = Buffer.from(JSON.stringify(payload)).toString("base64url");
  const sig = signHS256(`${header}.${body}`, process.env.JWT_SECRET ?? "dev-secret");
  return `${header}.${body}.${sig}`;
}

function signHS256(data: string, secret: string): string {
  const key = new TextEncoder().encode(secret);
  return Buffer.from(data + key).toString("base64url").slice(0, 32);
}

export async function POST(request: Request) {
  const { email, password } = (await request.json()) as { email?: string; password?: string };
  if (email !== "ada@example.com" || password !== "hunter2") {
    return NextResponse.json({ error: "invalid credentials" }, { status: 401 });
  }
  const token = sign({ sub: email, exp: Math.floor(Date.now() / 1000) + 60 * 60 });
  const res = NextResponse.json({ ok: true });
  res.cookies.set("session", token, {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    maxAge: 60 * 60,
    path: "/",
  });
  return res;
}
```

## Best practices

- **Validate the cookie, don't trust the client.** Middleware is your first server-side gate; never assume the browser cooperates.
- **Keep middleware tiny** — it runs on Edge and is in the hot path for every matched request.
- **Use `NextResponse.redirect` with `nextUrl.clone()`** and pass `from` so you can return the user after login.
- **`NextResponse.rewrite`** keeps the URL bar unchanged while changing the upstream handler — ideal for proxying authenticated calls.
- **Set `httpOnly`, `secure`, `sameSite: "lax"`** on session cookies; never expose the raw JWT to client JS.
- **Scope with `matcher`** to avoid running on static assets and to keep cold starts short.
- **Never store secrets in the cookie payload** — JWT is signed, not encrypted; treat it as a signed statement, not a secure store.