---
description: 'Modern Swift and SwiftUI conventions for iOS/macOS native apps — concurrency, state management, testing, and App Store readiness.'
applyTo: '**/*.swift'
---

# Swift & SwiftUI Instructions

You are an expert Swift engineer building native Apple-platform apps with modern Swift (6.x) and SwiftUI.

## Language & Concurrency

- **MUST**: use Swift's structured concurrency (`async`/`await`, `Task`, `TaskGroup`) for asynchronous work. Avoid completion-handler APIs in new code — they don't compose and can't be cancelled cleanly.
- **MUST**: mark shared mutable state `@MainActor` or isolate it behind an `actor`. Data races are compile-time errors under Swift 6 strict concurrency — do not silence them with `@unchecked Sendable` unless you've proven the type is actually safe.
- **SHOULD**: prefer `struct` over `class` for models; use `class` only when reference semantics or identity are required.
- **MUST**: propagate errors with `throws`/`try` rather than optional-returning "soft failure" APIs — callers need to distinguish "not found" from "failed."

## SwiftUI Architecture

- **MUST**: keep views declarative and side-effect-free; push side effects (networking, persistence) into an `@Observable` model or a dedicated service, not the view body.
- **SHOULD**: use `@Observable` (Observation framework) for view models instead of `ObservableObject`/`@Published` in new code — it tracks only the properties actually read by a given view, avoiding over-invalidation.
- **MUST**: use `NavigationStack`/`NavigationSplitView` with typed, value-based navigation (`navigationDestination(for:)`) — never `NavigationView` (deprecated) or view-identity-based navigation hacks.
- **SHOULD**: extract subviews when a `body` exceeds ~40 lines or nests more than 3 levels of modifiers; large bodies slow SwiftUI's diffing and hurt compile times.

## State Management

- **MUST**: use `@State` for view-local value-type state, `@Bindable`/`@Binding` to share mutable references down the tree, and `@Environment` for app-wide dependencies (never a singleton accessed directly from a view).
- **SHOULD NOT**: store SwiftUI view state in a singleton or global — it breaks previews, testability, and multi-window/scene support.

## Persistence & Data

- **SHOULD**: use SwiftData for new persistence needs; fall back to Core Data only when you need capabilities SwiftData doesn't yet cover.
- **MUST**: perform Core Data / SwiftData writes off the main thread for anything beyond trivial single-object edits; large batch operations must not block the UI.

## Testing

- **MUST**: use Swift Testing (`@Test`, `#expect`) for new test code over XCTest — it supports parameterized tests and async tests natively.
- **MUST**: test view models and services directly (they're plain Swift types); use `ViewInspector` or snapshot testing only for view-level assertions, not business logic.
- **SHOULD**: keep networking testable by injecting a protocol-typed client, not calling `URLSession.shared` directly from a model.

## App Store & Distribution

- **MUST**: request runtime permissions (camera, location, notifications, etc.) with a clear, localized `Info.plist` usage-description string — App Review rejects vague ones.
- **SHOULD**: adopt Swift's `Sendable` conformance checks and fix warnings before submission; concurrency bugs that pass locally can still crash under real device thermal/scheduling pressure.
- **MUST**: support Dynamic Type and VoiceOver for any user-facing text and interactive control — this is an App Store accessibility guideline, not optional polish.
