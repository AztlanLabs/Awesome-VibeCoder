---
description: 'Deno runtime conventions — permissions model, standard library usage, and Deno Deploy edge patterns.'
applyTo: '**/*.ts, **/*.js, **/deno.json, **/deno.jsonc'
---

# Deno Instructions

You are an expert TypeScript/JavaScript engineer building on the Deno runtime.

## Permissions Model

- **MUST**: run with the narrowest permission flags the program actually needs (`--allow-net=api.example.com` over bare `--allow-net`, `--allow-read=./data` over bare `--allow-read`) — Deno's security model only protects you if you scope it.
- **SHOULD NOT**: reach for `--allow-all`/`-A` outside of local prototyping; production and CI configs should declare explicit, minimal permissions in `deno.json` (`"permissions"` in a task) or the run command.
- **MUST**: audit third-party imports for the permissions they implicitly require before granting broad `--allow-*` flags to satisfy them.

## Dependencies & Imports

- **MUST**: pin dependency versions in imports (`npm:package@1.2.3`, `jsr:@scope/pkg@^1.0.0`) — unpinned/`latest` imports make builds non-reproducible.
- **SHOULD**: prefer `jsr:` packages over `npm:` when an equivalent exists — JSR packages ship type declarations natively and are vetted for Deno compatibility.
- **SHOULD**: use an `import_map`/`deno.json` `"imports"` field to centralize dependency versions rather than repeating full specifiers at every import site.

## Standard Library & Runtime APIs

- **MUST**: prefer Deno's built-in Web APIs (`fetch`, `Deno.serve`, `URL`, `Web Streams`) over Node-compatibility shims when writing new Deno-native code — the compat layer exists for porting, not as the primary API surface.
- **SHOULD**: use `Deno.serve()` directly for HTTP servers instead of pulling in a Node-style framework, unless you need routing/middleware ergonomics a framework provides (e.g. Hono, Oak).
- **MUST**: use `Deno.env.get()` (not `process.env`) for environment variables in Deno-native code, and require `--allow-env` explicitly rather than broadening other permission flags to compensate.

## Testing & Tooling

- **MUST**: use `Deno.test()` (built-in test runner) for unit/integration tests — no separate test framework install required for the common case.
- **SHOULD**: run `deno fmt` and `deno lint` in CI; both are bundled with the runtime and require no separate toolchain.
- **SHOULD**: use `deno check` (type-checking) as a CI gate separate from `deno test`, since `deno run`/`deno test` can skip type errors depending on flags.

## Deno Deploy / Edge Patterns

- **MUST**: keep handlers stateless and avoid relying on in-memory state surviving between requests — edge deployments may cold-start or run multiple isolated instances concurrently.
- **SHOULD**: use `Deno.Kv` (or an external store) for any state that must persist or be shared across edge instances — module-level variables are not a reliable cache in a multi-instance edge deployment.
- **MUST**: keep cold-start-sensitive code paths free of large synchronous imports; lazy-load rarely-used heavy dependencies inside the handler rather than at module top-level when deploying to the edge.

## Security

- **MUST**: validate all external input (query params, headers, request bodies) — Deno's sandboxing protects the host system, not your application logic from malformed/malicious payloads.
- **SHOULD**: use `Deno.Command` (not shelling out via `Deno.run`, which is deprecated) when the program genuinely needs to invoke a subprocess, and scope `--allow-run` to the specific binary.
