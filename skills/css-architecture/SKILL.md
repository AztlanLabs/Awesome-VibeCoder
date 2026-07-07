---
name: css-architecture
description: 'ITCSS/CUBE/BEM CSS layering, cascade layers (@layer), CSS Modules vs. CSS-in-JS trade-offs, and container queries — the canonical CSS-at-scale skill consumed by Frontend Engineer and Web Design System Engineer.'
---

# CSS Architecture

This skill defines how to structure CSS so it stays predictable as a codebase and team grow — the cascade is a shared global namespace, and without a deliberate layering strategy, specificity wars and dead styles accumulate silently.

A CSS codebase is not "done" because it renders correctly today — it is done when a new contributor can add a style without fighting existing specificity, and can delete a component's styles without fear of orphaned global side effects.

---

## When to Use

- Starting a new frontend project's styling foundation, or introducing structure into an unstructured/ad hoc stylesheet.
- Deciding between CSS Modules, CSS-in-JS, utility-first (Tailwind), and plain cascading CSS for a given project or component.
- Debugging a specificity conflict, an "I can't override this style" ticket, or unexplained style bleed between components.
- Introducing responsive, container-aware components (container queries) instead of viewport-only media queries.

## Prerequisites

- A build pipeline that supports the chosen approach (PostCSS/Sass for cascade layers, a bundler with CSS Modules support, or a CSS-in-JS runtime/compiler).

---

## 1. Layering Strategy — ITCSS

Inverted Triangle CSS orders rules from **least** to **most** specific, so later layers can safely override earlier ones without `!important`:

```text
1. Settings   — design tokens (colors, spacing, type scale) — no output CSS itself
2. Tools      — mixins/functions — no output CSS itself
3. Generic    — resets, box-sizing, normalize
4. Elements   — bare HTML element styles (h1, a, ul) — no classes
5. Objects    — layout-only patterns (.o-container, .o-grid) — no visual styling
6. Components — UI components (.c-card, .c-button) — the bulk of the codebase
7. Utilities  — single-purpose overrides (.u-hidden, .u-mt-4) — highest specificity, used sparingly
```

### Rules

- **Specificity must increase monotonically down the triangle** — a Components-layer rule must never need `!important` to beat a Generic-layer rule; if it does, something is misplaced.
- **Utilities are an escape hatch, not a primary authoring method** — a codebase that's 80% utility classes with no component layer has abandoned ITCSS's actual benefit (semantic, reusable component rules).

## 2. CUBE CSS (composition-first alternative)

CUBE (Composition, Utility, Block, Exception) is a lighter-weight alternative to strict ITCSS-with-BEM, better suited to teams that want less naming ceremony:

- **Composition**: layout primitives (`.stack`, `.cluster`, `.grid`) applied via composable classes, not per-component custom layout code.
- **Utility**: single-property classes for the 20% of cases that need a one-off tweak.
- **Block**: component-level styling, scoped by a single class per component root.
- **Exception**: data-attribute or modifier-scoped overrides for component state/variants (`[data-state="expanded"]`), kept visually distinct from the base Block rule.

### Rules

- **Prefer composition over per-component reinvention** — a new component should assemble existing layout primitives (stack/cluster/grid) rather than writing bespoke flex/grid rules that duplicate an existing primitive.
- **Exceptions must be visually adjacent to the rule they modify** — don't scatter a component's state-variant styles across the file; keep the base Block rule and its Exceptions together.

## 3. BEM Naming

When authoring global class names (ITCSS Components layer, or CUBE Blocks), use BEM (`Block__Element--Modifier`) so specificity stays flat (single class selectors) and relationships are readable from the name alone:

```css
.card { }
.card__title { }
.card__title--large { }
.card--featured { }
```

### Rules

- **One class, one selector** — avoid `.card .card__title` (descendant combinators re-introduce specificity coupling BEM exists to avoid); reference `.card__title` directly.
- **Modifiers are additive, not replacements** — `.card--featured` should sit alongside `.card`, both applied to the element, not used as a standalone replacement class.

## 4. Cascade Layers (`@layer`)

Native CSS cascade layers let you declare explicit layer order once, so source order and specificity within a layer stop mattering across layer boundaries:

```css
@layer reset, tokens, base, components, utilities;

@layer reset {
  * { margin: 0; padding: 0; box-sizing: border-box; }
}

@layer components {
  .card { border-radius: var(--radius-md); }
}

@layer utilities {
  .u-hidden { display: none; }
}
```

### Rules

- **Declare the full layer order once, up front** (`@layer reset, tokens, base, components, utilities;`) — an undeclared layer is implicitly ordered by first appearance, which is fragile against reordered imports.
- **Third-party CSS should be wrapped in its own layer** (`@import url(...) layer(vendor);`) below your `components` layer — this guarantees your component overrides always win without needing higher specificity or `!important`.
- **`@layer` does not replace the need for a naming convention** — layers solve cross-file ordering; BEM/CUBE still solve within-layer readability and collision avoidance.

## 5. CSS Modules vs. CSS-in-JS vs. Utility-First

| Approach | Strength | Weakness | Best fit |
|---|---|---|---|
| **CSS Modules** | Real CSS, scoped class names at build time, zero runtime cost | No dynamic-value theming without CSS variables | Component libraries, perf-sensitive apps |
| **CSS-in-JS (runtime)** | Colocated styles, dynamic props-driven styling | Runtime cost (style injection on render), larger JS bundle | Highly dynamic, prop-driven theming |
| **CSS-in-JS (compiled, e.g. vanilla-extract)** | Zero runtime cost + type-safe tokens | Build tooling complexity | Design-system-heavy apps wanting type safety |
| **Utility-first (Tailwind)** | Fast iteration, no naming decisions, small production CSS via purge | Verbose markup, harder to express complex composed states | Product teams prioritizing velocity over semantic markup |

### Rules

- **Pick one primary approach per project and apply it consistently** — mixing CSS Modules, a CSS-in-JS runtime, and hand-rolled global CSS in the same codebase multiplies the mental model a contributor needs.
- **Runtime CSS-in-JS's per-render style injection is a measurable performance cost** — profile it before choosing it for a performance-budget-constrained app (see `skills/web-performance-budget/SKILL.md`); prefer a compiled/zero-runtime variant when available.
- **Utility-first is a valid choice, not a lesser one** — the anti-pattern is inconsistency (utilities plus an uncoordinated parallel component-class system), not utility-first itself.

## 6. Container Queries

Container queries let a component respond to its **container's** size, not the viewport's — essential for genuinely reusable components that get placed in varying layout contexts (sidebar vs. main content vs. modal):

```css
.card-container {
  container-type: inline-size;
  container-name: card;
}

@container card (min-width: 400px) {
  .card { grid-template-columns: 1fr 1fr; }
}
```

### Rules

- **Use container queries for component-level responsiveness; reserve media queries for page-level/viewport-level layout decisions** — a component that only has media queries can't adapt correctly when reused in a narrow sidebar on a wide viewport.
- **Name containers when a component nests other queried containers** — an unnamed container query matches the nearest ancestor with `container-type` set, which becomes ambiguous once queried components nest.

---

## Anti-Patterns

- **`!important` as a routine override tool** — a sign the layering/specificity strategy has already broken down; fix the layer order or selector specificity instead.
- **Deeply nested selectors** (`.page .sidebar .widget .card .title`) — couples styling to DOM structure and creates unpredictable specificity; flatten to a single BEM/utility class.
- **Global resets applied inconsistently** — a reset that only some pages/components load produces "it looks different on this one page" bugs.
- **Mixing units without a system** — arbitrary `px`/`rem`/`%` per component instead of design tokens (see `skills/web-design-system/SKILL.md`) makes visual consistency impossible to audit.
- **Utility-class sprawl with no component layer** — every element styled with 15 inline utility classes and zero semantic component classes; unreadable and unmaintainable past a small project.

## Indicators of Done

| Indicator | Target |
|-----------|--------|
| Layering | The project has a documented, enforced layer order (ITCSS, CUBE, or `@layer`-based) — not ad hoc source-order dependence |
| Specificity | No routine use of `!important` outside of true, documented exceptions (e.g. overriding uncontrolled third-party markup) |
| Naming | Component/Block class names follow one consistent convention (BEM or the project's utility-class system) throughout |
| Responsiveness | Reusable components use container queries for their own layout; media queries are reserved for page-level decisions |
| Approach consistency | One primary styling approach (CSS Modules / CSS-in-JS / utility-first) is used consistently — no uncoordinated mixing |
| Token usage | Colors, spacing, and type sizes reference design tokens, not magic numbers repeated across files |

## Boundaries

### Do

- Always establish (or follow) a documented layering order before adding new global CSS.
- Always use BEM or an equivalent flat-specificity naming convention for component classes.
- Always use container queries for component-level responsive behavior.
- Always wrap third-party CSS in its own cascade layer when using `@layer`.
- Always reference design tokens for color/space/type values (see `skills/web-design-system/SKILL.md`).

### Do Not Do

- Do not reach for `!important` to resolve a specificity conflict — fix the layer/selector instead.
- Do not nest selectors more than 2 levels deep to work around a naming gap.
- Do not mix multiple competing styling approaches (CSS Modules + ad hoc global CSS + a CSS-in-JS runtime) in the same project without a documented reason and boundary.
- Do not use only viewport media queries for components meant to be reused across differently-sized containers.
