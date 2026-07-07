---
description: 'Idiomatic Kotlin conventions for JVM/Android development — coroutines, null-safety, and modern language features.'
applyTo: '**/*.kt, **/*.kts'
---

# Kotlin Instructions

You are an expert Kotlin engineer working across JVM backend and Android codebases.

## Null Safety & Types

- **MUST**: model absence with Kotlin's nullable types (`T?`), never a sentinel value (`-1`, empty string) standing in for "missing." Use `?.`, `?:`, and smart-casts instead of manual null checks.
- **SHOULD NOT**: use `!!` outside of tests or genuinely-impossible-to-be-null invariants proven by the type system a line above — it converts a compile-time safety net into a runtime crash.
- **SHOULD**: prefer `data class` for value-like types — it gives you `equals`/`hashCode`/`copy`/`toString` for free and signals immutability intent.

## Coroutines & Concurrency

- **MUST**: launch coroutines from a scope tied to a lifecycle (`viewModelScope`, `lifecycleScope`, or a structured `coroutineScope {}` you own) — never `GlobalScope.launch`, which leaks and can't be cancelled.
- **MUST**: use `Dispatchers.IO` for blocking I/O, `Dispatchers.Default` for CPU-bound work, and the platform main dispatcher only for UI updates — never block the main dispatcher with synchronous I/O.
- **SHOULD**: model concurrent state with `StateFlow`/`SharedFlow` rather than exposing a mutable `LiveData`/`var` across a class boundary; collectors should see a read-only stream.
- **MUST**: handle `CancellationException` correctly — never swallow it in a broad `catch (e: Exception)`; re-throw it so structured concurrency can propagate cancellation.

## Language Idioms

- **SHOULD**: use `sealed class`/`sealed interface` for closed sets of states (e.g. `Result<T>`-style success/error/loading) so `when` expressions are exhaustive and the compiler catches missing branches.
- **SHOULD**: prefer extension functions over utility classes with static methods — they read at the call site and don't require importing a helper class.
- **MUST**: use `val` by default; only use `var` when reassignment is actually required by the algorithm.
- **SHOULD**: use scope functions (`let`, `run`, `apply`, `also`, `with`) purposefully — `apply`/`also` for side effects on the receiver, `let`/`run` for null-safe transforms — not as a style tic.

## Android-Specific (when applicable)

- **MUST**: hoist state out of Composables into a `ViewModel` exposing `StateFlow`; Composables should be stateless renderers of that state.
- **MUST**: use Hilt (or manual constructor injection) for dependency graphs — avoid `object` singletons for anything that needs to be swapped in tests.
- **SHOULD**: use `remember`/`derivedStateOf` deliberately in Compose to avoid recomputing expensive values on every recomposition.

## Testing

- **MUST**: test coroutine code with `runTest` and a `TestDispatcher`, not real delays — real `delay()` calls make test suites slow and flaky.
- **SHOULD**: use MockK (or Mockito-Kotlin) for mocking; prefer fakes over mocks for value-heavy collaborators to keep tests resilient to refactors.

## Build & Interop

- **SHOULD**: annotate public Kotlin APIs consumed from Java with `@JvmStatic`/`@JvmOverloads`/`@JvmName` where interop ergonomics matter.
- **MUST**: keep `build.gradle.kts` dependency versions centralized (version catalogs / `libs.versions.toml`) rather than hardcoded per-module strings.
