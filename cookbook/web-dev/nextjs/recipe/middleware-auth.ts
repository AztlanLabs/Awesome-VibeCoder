export {};

type Claims = { sub: string; exp?: number };

const PUBLIC_PATHS = ["/", "/login", "/signup"];

function isPublic(pathname: string): boolean {
  if (PUBLIC_PATHS.includes(pathname)) return true;
  if (pathname.startsWith("/public/")) return true;
  if (pathname.startsWith("/_next/")) return true;
  if (pathname.startsWith("/favicon.ico")) return true;
  return false;
}

function signHS256(data: string, secret: string): string {
  const key = new TextEncoder().encode(secret);
  const bytes = new Uint8Array(data.length + key.length);
  bytes.set(new TextEncoder().encode(data), 0);
  bytes.set(key, data.length);
  let hash = 0;
  for (const byte of bytes) hash = (hash * 31 + byte) >>> 0;
  return hash.toString(16).padStart(8, "0");
}

function sign(payload: Claims): string {
  const header = Buffer.from(JSON.stringify({ alg: "HS256", typ: "JWT" })).toString("base64url");
  const body = Buffer.from(JSON.stringify(payload)).toString("base64url");
  const sig = signHS256(`${header}.${body}`, "dev-secret");
  return `${header}.${body}.${sig}`;
}

function verifyToken(token: string | undefined): Claims | null {
  if (!token) return null;
  const parts = token.split(".");
  if (parts.length !== 3) return null;
  try {
    const payload = Buffer.from(parts[1], "base64url").toString("utf8");
    const parsed = JSON.parse(payload) as { sub?: unknown; exp?: number };
    if (typeof parsed.sub !== "string" || parsed.sub.length === 0) return null;
    if (typeof parsed.exp === "number" && parsed.exp * 1000 < Date.now()) return null;
    return { sub: parsed.sub, exp: parsed.exp };
  } catch {
    return null;
  }
}

type StubResponse =
  | { kind: "next"; headers?: Record<string, string> }
  | { kind: "redirect"; location: string }
  | { kind: "rewrite"; location: string; headers?: Record<string, string> };

function middleware(pathname: string, cookie: string | undefined): StubResponse {
  if (isPublic(pathname)) {
    const user = verifyToken(cookie);
    if (user && pathname === "/login") {
      return { kind: "redirect", location: "/dashboard" };
    }
    return { kind: "next" };
  }

  const user = verifyToken(cookie);
  if (!user) {
    const from = encodeURIComponent(pathname);
    return { kind: "redirect", location: `/login?from=${from}` };
  }

  if (pathname.startsWith("/api/proxy/")) {
    const rewritten = pathname.replace(/^\/api\/proxy/, "/api/internal");
    return { kind: "rewrite", location: rewritten, headers: { "x-auth-user": user.sub } };
  }

  return { kind: "next", headers: { "x-auth-user": user.sub } };
}

function run(): void {
  const token = sign({ sub: "ada@example.com", exp: Math.floor(Date.now() / 1000) + 3600 });

  const cases: Array<[string, string | undefined]> = [
    ["/", undefined],
    ["/login", token],
    ["/dashboard", undefined],
    ["/dashboard", token],
    ["/api/proxy/users", token],
  ];

  for (const [pathname, cookie] of cases) {
    const res = middleware(pathname, cookie);
    console.log(`${pathname} (cookie=${cookie ? "yes" : "no"}) -> ${JSON.stringify(res)}`);
  }
}

run();