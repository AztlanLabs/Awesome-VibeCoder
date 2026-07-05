---
name: web-design-system
description: 'Building and maintaining production design systems — design tokens (color/spacing/typography/radius/shadow/elevation/motion), token tiers (global/alias/component), theming (light/dark, multi-brand), component APIs, accessibility primitives, Figma <-> code sync, versioning & migration.'
---

# Web Design System Craftsmanship

As an engineering assistant working on a design system, your job is to crystallize design intent into **durable, token-driven primitives** that scale across products, themes, and brands without drifting. A design system is a product: it has versioning, consumers, deprecation paths, and a contract surface. Treat tokens as code — typed, tested, reviewed, and migrated deliberately.

When the user requests token creation, theming support, primitive/component API design, Figma-to-code sync, or system health diagnostics, apply the following framework to every decision.

---

## When to Use This Skill

- Establishing the first set of design tokens for an application or org.
- Extending an existing token set with a new theme (dark mode, density, brand variant).
- Designing the API of a primitive component (Button, Input, Card, Dialog).
- Diagnosing design drift, prop-explosion, or magic-number sprawl.
- Syncing Figma variables / styles to CSS custom properties or a token file.
- Planning a token rename, alias redirect, or breaking version migration.

## Prerequisites

- A build pipeline that emits CSS (custom properties) or a token transformation step (Style Dictionary, Tokens Studio, dtctr).
- A theming host strategy: `data-theme` attribute on `<html>` or a scoped provider.
- WCAG 2.2 AA target agreed with design (AAA where specified).
- A documented component contract spec (slots, variants, states).

---

## Design Token Taxonomy (Tiered Model)

Tokens are layered. Lower tiers are abstract; upper tiers are concrete. Never consume raw global tokens directly inside product code — always go through an alias or component token so the system can be re-pointed without touching every call site.

| Tier      | Scope        | Example                                 | Consumed by             |
|-----------|--------------|-----------------------------------------|-------------------------|
| Global    | Raw primitive | `--color-blue-500`, `--space-8`, `--font-size-7` | Alias tokens only |
| Alias     | Semantic intent | `--color-bg-canvas-primary`, `--space-sm`, `--text-body` | Component tokens, occasionally product UI |
| Component | Component-scoped | `--button-bg`, `--button-padding-x`, `--input-border` | The single owning component |

Rules:
- **Global tokens** are immutable primitives: a palette, a scale. They never reference other tokens.
- **Alias tokens** express intent and are the only layer allowed to reference global tokens. They can be re-pointed per theme (e.g. `--color-bg-canvas-primary` → `--color-gray-0` in light, `--color-gray-950` in dark).
- **Component tokens** are bound to one component and owned by it. Component tokens may reference alias tokens; they never reference global tokens directly.

## Token Naming Convention

Predictable names make tokens greppable and migration-safe. Use the form:

```
--{category}-{property}-{role}-{state?}
```

Examples:
```css
:root {
  --color-bg-canvas-primary: var(--color-gray-0);
  --color-bg-canvas-muted: var(--color-gray-50);
  --color-fg-default: var(--color-gray-950);
  --color-border-subtle: var(--color-gray-200);
  --color-accent-default: var(--color-blue-600);
  --color-accent-default-hover: var(--color-blue-700);

  --space-xs: var(--space-2);   /* 0.5rem */
  --space-sm: var(--space-4);   /* 1rem */
  --space-md: var(--space-6);   /* 1.5rem */
  --space-lg: var(--space-8);   /* 2rem */
  --space-xl: var(--space-12);  /* 3rem */

  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-pill: 9999px;

  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 10px rgba(0, 0, 0, 0.08);

  --motion-duration-fast: 120ms;
  --motion-duration-normal: 200ms;
  --motion-ease-standard: cubic-bezier(0.2, 0, 0, 1);
}
```

Forbidden: `--primary-blue`, `--my-button-bg`, hex inside component CSS, magic numbers like `--gap-13`.

## Spacing Scale

Build on a 4px / 8px rhythm. The base unit is 4px; every step is a multiple of 4 so layouts always snap to the grid.

| Token     | Pixels | rem    | Use                |
|-----------|--------|--------|--------------------|
| `--space-1` | 4    | 0.25   | hairline gaps      |
| `--space-2` | 8    | 0.5    | inline spacing     |
| `--space-3` | 12   | 0.75   | tight grouping     |
| `--space-4` | 16   | 1      | default gap        |
| `--space-6` | 24   | 1.5    | card padding       |
| `--space-8` | 32   | 2      | section padding    |
| `--space-12`| 48   | 3      | layout gaps        |
| `--space-16`| 64   | 4      | page-level rhythm  |

Alias the raw integers to intent (`--space-sm`, `--space-md`). Components consume the alias only.

## Type Scale (Modular + Fluid)

Define a modular scale and a fluid interpolation using `clamp()`. A fluid scale means one token table serves every viewport.

```css
:root {
  --font-size-1: clamp(0.75rem, 0.72rem + 0.15vw, 0.8rem);
  --font-size-2: clamp(0.875rem, 0.85rem + 0.2vw, 0.95rem);
  --font-size-3: clamp(1rem, 0.97rem + 0.3vw, 1.125rem);
  --font-size-5: clamp(1.5rem, 1.4rem + 0.8vw, 2rem);
  --font-size-7: clamp(2rem, 1.7rem + 2.2vw, 3rem);

  --line-height-tight: 1.15;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.7;

  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-bold: 700;
}
```

Type tokens (alias layer) carry role + size + weight together:

```css
--text-display: var(--font-size-7) var(--font-weight-bold) / var(--line-height-tight);
--text-body: var(--font-size-2) var(--font-weight-regular) / var(--line-height-normal);
--text-caption: var(--font-size-1) var(--font-weight-medium) / var(--line-height-normal);
```

## Color Tokens & WCAG Contrast

Color tokens are paired foreground-on-background and **must** meet contrast targets before merge.

| Use case                                  | Min ratio | Target level |
|-------------------------------------------|----------|--------------|
| Body text on background                   | 4.5:1    | AA           |
| Body text on background (AAA tier)        | 7:1      | AAA          |
| Large text (≥24px or ≥18.66px bold)      | 3:1      | AA large     |
| UI component boundaries & graphics        | 3:1      | AA non-text  |
| Disabled state text/icon                  | N/A      | exempt       |

Contrast indicators enforced in CI:
- `Good` — ratio ≥ target level.
- `Warning` — meets AA but not AAA when AAA is requested.
- `Fail` — ratio below target; the token PR cannot merge.

Pair tokens as foreground-on-background roles rather than standalone hues so contrast is auditable per pair:

```css
:root {
  --color-bg-canvas-primary: var(--color-gray-0);   /* light */
  --color-fg-default: var(--color-gray-950);        /* ratio 19.3:1 ✓ */
  --color-bg-canvas-muted: var(--color-gray-50);
  --color-fg-muted: var(--color-gray-600);          /* ratio 7.1:1 ✓ AAA */
}
```

## Shadow / Elevation Tokens

Elevation maps depth to a discrete scale; components pick a tier, never a custom shadow.

```css
--elevation-0: none;
--elevation-1: var(--shadow-sm);
--elevation-2: var(--shadow-md);
--elevation-3: 0 8px 24px rgba(0,0,0,0.10);
--elevation-overlay: 0 12px 32px rgba(0,0,0,0.16);
```

Pair elevation with border tokens (`--color-border-subtle`) so resting and raised surfaces share a language.

## Motion Tokens

Motion also has tiers; durations and easings are tokens, not local constants.

```css
--motion-duration-instant: 80ms;
--motion-duration-fast: 120ms;
--motion-duration-normal: 200ms;
--motion-duration-slow: 320ms;

--motion-ease-standard: cubic-bezier(0.2, 0, 0, 1);
--motion-ease-emphasized: cubic-bezier(0.3, 0, 0, 1.2);
--motion-ease-exit: cubic-bezier(0.4, 0, 1, 1);
```

Always gate motion behind `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  :root {
    --motion-duration-fast: 0ms;
    --motion-duration-normal: 0ms;
    --motion-duration-slow: 0ms;
  }
}
```

## Theming via `data-theme` + Custom Properties

Theming is a flat key swap. Define a default palette on `:root` and override per `data-theme`. Multi-brand becomes a `data-brand` axis orthogonal to `data-theme`.

```css
:root,
[data-theme="light"] {
  --color-bg-canvas-primary: var(--color-gray-0);
  --color-fg-default: var(--color-gray-950);
}

[data-theme="dark"] {
  --color-bg-canvas-primary: var(--color-gray-950);
  --color-fg-default: var(--color-gray-100);
}

[data-brand="alt"][data-theme="light"] {
  --color-accent-default: var(--color-teal-600);
}
[data-brand="alt"][data-theme="dark"] {
  --color-accent-default: var(--color-teal-400);
}
```

```html
<html data-theme="dark" data-brand="default">
```

Density (`data-density="compact"`) and direction (`dir`) ride the same attribute axis.

## Component API Rules

1. **Composition over configuration.** Prefer slots (`<Card.Header>`, `children`) to a single giant props object. One component, one job; compose for variety.
2. **Variants via `data-` attributes, not utility props.** `<Button data-variant="primary">` over `<Button variant="primary">` styling branches because `data-*` is styleable from CSS without JS.
3. **Minimum surface, maximum escape hatch.** Keep required props to zero; expose `className` slots and a `style` passthrough for product-level escape cases.
4. **States belong to the component, not the consumer.** `:hover`, `:focus-visible`, `:disabled`, `aria-*` are wired internally; consumers pass data, not styling hooks.
5. **Document the slot contract.** Each component lists its slots, accepted children, and the tokens it consumes.

## Indicator & Signals (System Health)

| Signal                        | Healthy     | Watch         | Act                 |
|-------------------------------|-------------|---------------|---------------------|
| Adoption rate (components using DS primitives) | ≥ 80%     | 60–80% | Reduce barrier, add primitives |
| Drift % (custom values overriding tokens in app code) | ≤ 5% | 5–15% | Audit + redirect aliases |
| Coverage (token-consuming sites for a category) | ≥ 90% | < 90% | Add missing alias tokens |
| Token duplication (same value, different name) | 0 | > 0 | Consolidate + deprecate duplicate |
| Breaking-change frequency     | < 1 / quarter | 1 / quarter | Owner review |

## Figma <-> Code Sync

- Source of truth is one token artifact (`tokens.json` or Tokens Studio export). Both Figma and code regenerate from it; never hand-edit either side.
- Codegen step (Style Dictionary / custom transformer) emits `:root` CSS, TS theme constants, and tailwind/figma-plugin equivalents from the same artifact.
- A rename in the source artifact triggers a codemod (jscodeshift / ts-morph) that updates call sites and writes a migration note in the changelog.

## Versioning & Migration

- Semantic version the token package. Token renames/repointing with no behavior change = minor; token removal or rename of an alias consumed by product code = major.
- Maintain an `aliases` redirect map for one minor cycle so old token names keep working with a deprecation warning.
- Every major ships a codemod and a `CHANGELOG.md` migration table: `Old → New → Codemod command`.

## Anti-Patterns

- **Magic numbers** in component CSS (`padding: 13px`, `top: 47px`). Replace with `--space-*` / alias tokens.
- **Hardcoded hex** inside components (`background: #1a73e8`). Use a token; if none exists, add an alias token, then consume it.
- **Prop-explosion** (`variant`, `tone`, `size`, `shape`, `weight`, `intent` all on one component). Split into composition or move to `data-variant` + tokens.
- **Defining alias tokens inside product code.** Alias tokens live in the system package; product calls alias tokens.
- **Cross-tier references.** Component tokens referencing global tokens directly breaks theming redirection.

## Workflows

### Workflow 1: Add a New Alias Token

1. Open or create the alias token section in `tokens.color.json` (etc.).
2. Add `--color-<role>-<state>` with a global-token reference; never a literal.
3. Regenerate CSS theme bundle (`npm run tokens:build`) and verify the new custom property appears in `:root`.
4. Run the contrast CI gate (`npm run tokens:contrast`) and confirm the pair meets target.
5. Add a usage example to the component docs and update the changelog as `minor`.

### Workflow 2: Introduce a Dark Theme

1. Inventory existing alias tokens — list every `--color-*` pair.
2. For each pair, pick a dark global-token target and verify contrast on the dark background.
3. Append a `[data-theme="dark"]` block overriding every alias; never delete the light block.
4. Add a theme switcher test using `data-theme` and snapshot visual regression in both themes.
5. Update the system health dashboard token coverage metric.

### Workflow 3: Migrate a Renamed Token

1. Add the new token name with the new alias target.
2. Add an alias redirect (`--old-name: var(--new-name)`) valid for one minor cycle.
3. Generate a codemod that replaces `--old-name` → `--new-name` across the monorepo.
4. Run codemod, regenerate, run tests against the consumer packages.
5. Bump major if removal, minor if addition-only; write the migration note.

## Do's / Don'ts

**Do**
- ✅ Always consume alias/component tokens, never global tokens, in product CSS.
- ✅ Pair foreground and background tokens so contrast is testable per pair.
- ✅ Treat a token rename as a coded migration, not a find-replace.
- ✅ Keep `:root` light-theme the default; other themes are overrides.
- ✅ Gate motion behind `prefers-reduced-motion`.
- ✅ Add one component token per property slot; one component, one owner.

**Don't**
- ❌ Hardcode hex, px values, or `cubic-bezier(...)` literals inside components.
- ❌ Consume global tokens (`--color-blue-500`) directly in component CSS.
- ❌ Add a `<Button variant="...">` for every appearance — use `data-variant` + tokens.
- ❌ Ship a token without a contrast CI result.
- ❌ Delete a token without a deprecation cycle and codemod.

## Validation Checklist

- [ ] Every new token sits in the correct tier and references only the tier below.
- [ ] Pair tokens (fg/bg) include a recorded contrast ratio meeting AA/AAA target.
- [ ] No literal hex, px, or `cubic-bezier(...)` inside component CSS.
- [ ] `data-theme` (and `data-brand` if multi-brand) overrides honored for every alias token.
- [ ] Component samples render identically across `light` and `dark` themes (visual regression green).
- [ ] Motion tokens gated by `prefers-reduced-motion`.
- [ ] Token coverage ≥ 90% for the touched category.
- [ ] No new duplicated token names (CI guard green).
- [ ] Changelog entry present with tier, level (minor/major), and migration command.
- [ ] Figma export/import passes `tokens:diff` with no uncommitted manual edits.

## Summary

A web design system is a versioned contract: tiers of tokens, paired-color contrast guarantees, theme-able via attributes, component APIs that compose. When you touch it, you move tokens deliberately — add an alias, verify contrast, regenerate, record the migration — and never sprinkle magic values. Health is measurable: adoption, drift, and coverage. Keep those numbers in the green and the system scales.