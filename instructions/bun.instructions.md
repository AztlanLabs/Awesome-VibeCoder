---
description: 'Bun runtime conventions — Bun.serve streaming, native APIs, bundler/test-runner usage, and performance patterns.'
applyTo: '**/*.ts, **/*.js, **/*.tsx, **/*.jsx, **/bunfig.toml'
---

# Bun Instructions

You are an expert TypeScript/JavaScript engineer building on the Bun runtime.

## Runtime APIs

- **MUST**: prefer Bun's native APIs (`Bun.serve`, `Bun.file`, `Bun.write`, `Bun.spawn`) over Node polyfills when writing new Bun-native code — they're faster and avoid the Node-compat shim overhead.
- **SHOULD**: use `Bun.env` / `process.env` (Bun supports both) consistently within a codebase rather than mixing conventions.
- **MUST**: use `Bun.password.hash`/`Bun.password.verify` (built-in, bcrypt-backed) instead of adding a separate hashing dependency for simple password-hashing needs.

## HTTP Servers & Streaming

- **MUST**: use `Bun.serve()`'s native `fetch` handler and Web Streams (`ReadableStream`) for streaming responses — don't route through an Express-compatibility layer unless migrating existing Express code.
- **SHOULD**: use `Bun.serve()`'s built-in WebSocket support (`websocket` handler in the serve config) instead of pulling in a separate `ws` dependency for simple WebSocket needs.
- **MUST**: apply backpressure on any manually-constructed `ReadableStream` (respect the controller's desired size / pause on backpressure) — an unbounded producer writing into a slow consumer's stream is a memory leak.

## Package Management

- **MUST**: commit `bun.lockb` (or the text lockfile, if configured) for reproducible installs — do not `.gitignore` the lockfile.
- **SHOULD**: use `bun install --frozen-lockfile` in CI so a drifted lockfile fails the build instead of silently resolving different versions.
- **SHOULD**: prefer Bun's built-in package manager over mixing `npm`/`yarn`/`pnpm` in the same project — mixed lockfiles are a common source of "works on my machine."

## Bundler & Build

- **SHOULD**: use `Bun.build()` (or the `bun build` CLI) for bundling application code targeting browsers/edge — configure `target: "bun"` vs `"browser"` vs `"node"` explicitly per output.
- **MUST**: mark server-only dependencies (DB drivers, secrets access) as external when bundling for a browser target — accidentally bundling them leaks server code/credentials to the client.

## Testing

- **MUST**: use `bun test` (Jest-compatible API, built in) for unit tests — no separate test runner install needed for the common case.
- **SHOULD**: use `bun:test`'s native mocking (`mock()`, `spyOn()`) rather than pulling in a separate mocking library, unless you need a feature Bun's mocks don't cover.

## Performance & Native Modules

- **SHOULD**: use `Bun.FFI` only when a genuine native-library integration is required — it bypasses Bun's safety guarantees and should be isolated behind a thin, well-tested wrapper module.
- **MUST**: benchmark before assuming Bun's speed advantage applies to your specific bottleneck — I/O-bound workloads gated by an external service won't see the runtime-level gains that CPU-bound/startup-time workloads do.

## TypeScript & Tooling

- **SHOULD**: rely on Bun's built-in TypeScript execution (no separate `ts-node`/`tsx` needed) for scripts and the dev server; use `tsc --noEmit` in CI as the type-checking gate since Bun's runtime type-strips without full type-checking.
