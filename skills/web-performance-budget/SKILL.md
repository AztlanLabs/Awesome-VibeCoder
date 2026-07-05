---
name: web-performance-budget
description: 'Defining and enforcing Core Web Vitals performance budgets (LCP, INP, CLS, TTFB, TBT) and asset budgets across the build pipeline, with per-route enforcement in CI.'
---

# Web Performance Budget Skill

A performance budget is a contract: every route, every byte, and every paint is bounded by a stated threshold, and the build fails when a product crosses those bounds. Your role is to define those budgets, wire them into the build pipeline, profile against them, and remediate regressions with surgical, before-after-validated fixes. A site is only fast if a measurable number says it is.

---

## When to Use This Skill

- Establishing or revising the per-route performance budget for an app.
- Profiling a route that reports a metric regression (Lighthouse, RUM, CI alert).
- Designing the CI gate that fails the build on budget breach.
- Triaging third-party scripts that bloat INP / TBT.

## Prerequisites

- A reproducible build command (production mode) and a known list of routes.
- CI environment capable of running Lighthouse-CI or WebPageTest against a built artifact.
- Access to real-user monitoring (RUM) data when tuning thresholds against field experience.
- A baseline commit to measure deltas against.

---

## Core Web Vitals Thresholds (Lab + Field)

| Vital | Good          | Needs improvement | Poor          | Field source              |
|-------|---------------|-------------------|---------------|---------------------------|
| LCP   | ≤ 2.5 s       | 2.5–4.0 s         | > 4.0 s       | `LargestContentfulPaint`  |
| INP   | ≤ 200 ms      | 200–500 ms        | > 500 ms      | `InteractionId` (INP)      |
| CLS   | ≤ 0.10        | 0.10–0.25         | > 0.25        | `layout-shift` entries    |
| TTFB  | ≤ 800 ms      | 800–1800 ms       | > 1800 ms     | Navigation timing          |
| FCP   | ≤ 1.8 s       | 1.8–3.0 s         | > 3.0 s       | `first-contentful-paint`   |
| TBT   | ≤ 200 ms      | 200–600 ms        | > 600 ms      | Lighthouse (lab only)      |

Use field thresholds (LCP/INP/CLS/TTFB) for RUM targets; use lab (TBT/FCP) for CI gating because they are stable.

## Budget Categories

Each category binds a separate concern; never collapse them into a single "bundle is too big" rule.

| Category            | Example target (per route)                                   | Rationale                              |
|---------------------|--------------------------------------------------------------|----------------------------------------|
| JS bundle (initial) | ≤ 170 KiB gzipped                                          | Keeps parse+exec under INP threshold    |
| JS bundle (per async chunk) | ≤ 90 KiB gzipped                                  | Keeps route-split chunks cheap         |
| CSS (initial)       | ≤ 30 KiB gzipped                                          | Above-the-fold must be inline-critical |
| Image bytes (LCP image) | ≤ 120 KiB, format AVIF/WebP                            | First paint speed                      |
| Total images per route | ≤ 600 KiB                                              | Bandwidth on mid-tier mobile           |
| Third-party scripts | ≤ 50 KiB gzipped, ≤ 3 hosts                                   | Caps long-task and blocking impact      |
| Fonts               | ≤ 2 families, ≤ 4 weights, `font-display: swap`            | Avoid FOIT blocking first paint        |
| Request count (initial) | ≤ 30 (HTTP/2 ≤ 25)                                     | Head-of-line + parsing cost            |
| Long tasks (>50ms) | 0 on initial load                                          | Direct driver of INP poor              |

## Measurement Stack

| Tool              | Scope                                      | When                          |
|-------------------|-------------------------------------------|-------------------------------|
| Lighthouse        | Single URL, lab CrUX                       | Local dev, pre-release PR      |
| Lighthouse-CI     | Headless batch over routes in CI           | **CI gate**                    |
| WebPageTest       | Multi-location, custom network throttling  | Deep investigation            |
| `performance` API | Field / runtime capture                    | RUM in production              |
| `PerformanceObserver` | Field component-level metrics           | RUM + targeted remediation      |

### Runtime capture snippet (RUM)

```js
import { onLCP, onINP, onCLS, onFCP, onTTFB } from 'web-vitals';

function emit(metric) {
  navigator.sendBeacon(
    '/rum',
    JSON.stringify({ name: metric.name, value: metric.value, id: metric.id, rating: metric.rating })
  );
}

[onLCP, onINP, onCLS, onFCP, onTTFB].forEach((fn) => fn(emit));
```

### `PerformanceObserver` for long tasks and shifts

```js
let longTaskCount = 0;
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (entry.duration > 50) longTaskCount += 1;
  }
}).observe({ entryTypes: ['longtask'] });

let cls = 0;
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (!entry.hadRecentInput) cls += entry.value;
  }
}).observe({ entryTypes: ['layout-shift'] });
```

## Per-Route Budget Enforcement

Wire thresholds into the bundler so a breach fails the build (not merely warns).

### Thresholds config (`perf-budgets.ts`)

```ts
export interface RouteBudget {
  route: string;
  lcp: number;        // ms
  inp: number;        // ms
  cls: number;        // unitless
  tbt: number;        // ms
  jsGzipKiB: number;  // initial bundle
  imageKiB: number;   // per-route image total
}

export const budgets: RouteBudget[] = [
  { route: '/',            lcp: 2500, inp: 200, cls: 0.1, tbt: 200, jsGzipKiB: 170, imageKiB: 120 },
  { route: '/p/:id',       lcp: 2500, inp: 200, cls: 0.1, tbt: 250, jsGzipKiB: 200, imageKiB: 600 },
  { route: '/search',      lcp: 2200, inp: 200, cls: 0.05, tbt: 150, jsGzipKiB: 150, imageKiB: 80 },
];
```

### Vite plugin pattern (assert bundle sizes at build time)

```ts
import { Plugin } from 'vite';
import { budgets } from './perf-budgets';

export function perfBudgetPlugin(): Plugin {
  return {
    name: 'perf-budget-gate',
    apply: 'build',
    closeBundle: () => {
      const report = budgets.map((b) => {
        const bundleKiB = measureRouteBundle(b.route);
        return { route: b.route, jsGzipKiB: bundleKiB, budget: b.jsGzipKiB };
      });
      const breaches = report.filter((r) => r.jsGzipKiB > r.budget);
      if (breaches.length) {
        for (const b of breaches) {
          console.error(`[budget] ${b.route}: ${b.jsGzipKiB}KiB > ${b.budget}KiB`);
        }
        throw new Error('Performance budget exceeded');
      }
    },
  };
}
```

### Webpack equivalent (using `performance` hints + `webpack-bundle-analyzer`)

```js
module.exports = {
  performance: {
    maxAssetSize: 200 * 1024,
    maxEntrypointSize: 170 * 1024,
    hints: 'error', // fails build on breach
  },
  plugins: [new BundleAnalyzerPlugin({ analyzerMode: 'json', openAnalyzer: false })],
};
```

### Lighthouse-CI gate (asserts vitals, not just bundle size)

```js
// lighthouserc.js
module.exports = {
  ci: {
    collect: { url: ['http://localhost:3000/', 'http://localhost:3000/search'], numberOfRuns: 3 },
    assert: {
      assertions: {
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'interaction-to-next-paint': ['error', { maxNumericValue: 200 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'total-blocking-time': ['error', { maxNumericValue: 200 }],
        'first-contentful-paint': ['warn', { maxNumericValue: 1800 }],
      },
    },
  },
};
```

## Third-Party Impact

Every third-party script adds parse time, network round-trips, and a new origin that can schedule main-thread work. The table below lists the typical aggressive Guests and how to encapsulate them.

| Third-party        | Common impact                       | Mitigation                                 |
|--------------------|-------------------------------------|--------------------------------------------|
| Analytics (GA)     | INP regression, blocking `<script>` | Async/defer, partytown, sample on slow     |
| Tag managers       | Long tasks at startup               | Async load, partition triggers             |
| Chat widgets       | Long task + fixed DOM               | Lazy-mount on idle, `requestIdleCallback`  |
| Video embeds (YT)  | Heavy main-thread parse             | Facade: clickable poster, load on click   |
| Maps               | Heavy JS + image requests            | Static preview until interaction           |
| A/B testing        | Inline synchronous script blocking   | Async, server-side variant assignment       |

Rule: a third-party that loads in the initial waterfall must move behind `requestIdleCallback`, an interaction trigger, or a sandboxed web worker (`partytown`).

## Runtime Indicators

| Indicator            | How to read                                                     | Action                            |
|---------------------|------------------------------------------------------------------|-----------------------------------|
| LCP element         | `PerformanceObserver` `largest-contentful-paint` + `element`     | Optimize that node first          |
| Long task count      | Sum of `longtask` entries > 50ms                                 | Code-split or defer the offender  |
| Layout shift score   | Sum of `layout-shift` entries (excluding input)                  | Reserve dimensions, lazy-load with size |
| JS coverage          | DevTools `Coverage` tab: unused % of initial bundle              | Tree-shake or move to lazy chunk   |
| CLS top contributors | `layout-shift` `sources` array                                  | Stabilize those specific elements  |
| INP phases           | `inputDelay` + `processingTime` + `presentationDelay`           | Targets the dominant phase         |

## CI Integration Rule

A budget breach must **fail** the build. Warnings decay silently into regressions; red builds force a fix-or-raise-the-budget (with documented justification) decision.

```yaml
# .github/workflows/perf.yml
- name: Lighthouse CI
  run: npm run lhci
- name: Bundle budget gate
  run: npm run build -- --perf-budget
```

When a budget is intentionally raised, PR description must include: previous threshold, new threshold, root cause, and the metric delta that justified the change.

## Workflow

1. **Record baseline** — commit hash, route list, Lighthouse-CI numbers, bundle size table.
2. **Define thresholds** — start from the recommended Good thresholds; tighten toward RUM p75 of last 28 days.
3. **Wire the gate** — add the Vite/Webpack plugin and `lighthouserc.js`; fail on breach.
4. **Profile the regression** — pick the failing route, capture Lighthouse trace + `PerformanceObserver` field numbers, identify the LCP element, long tasks, and CLS sources.
5. **Apply targeted fixes** — one fix at a time, re-measure between each:
   - LCP image → AVIF/WebP, `fetchpriority="high"`, `rel=preload`, size attributes.
   - INP → defer non-critical tasks with `requestIdleCallback`, code-split heavy handlers.
   - CLS → set explicit `width`/`height`, `aspect-ratio`, reserve placeholder for ads.
   - JS coverage → tree-shake, lazy-mount below-the-fold widgets, replace moment with native `Intl`.
   - Fonts → `font-display: swap`, subset, `preload` the most critical family only.
   - Third-party → partytown / idle trigger / facade.
6. **Re-measure** — re-run CI gate + a manual Lighthouse pass; record before/after numbers in the PR.
7. **Pin** — update `perf-budgets.ts` (only if justified), commit the trace + summary, append a one-liner to `.sdlc/memory.md`.

## Reporting Template

```markdown
# Performance Report — <route>
Date: YYYY-MM-DD   Build: <commit>
Budget source: perf-budgets.ts (<route>)

## Baseline → After
| Metric  | Budget | Before | After | Status |
|---------|--------|--------|-------|--------|
| LCP     | 2500   | 3100   | 2300  | PASS   |
| INP     | 200    | 280    | 180   | PASS   |
| CLS     | 0.10   | 0.18   | 0.04  | PASS   |
| TBT     | 200    | 420    | 150   | PASS   |
| JS gzip | 170    | 240    | 158   | PASS   |
| Image   | 120    | 220    | 95    | PASS   |

## Root causes addressed
1. LCP image re-encoded AVIF, `fetchpriority="high"`, `rel=preload`.
2. Search handler code-split, deferred to `requestIdleCallback`.
3. Ads slot reserved with `aspect-ratio` to eliminate CLS.

## CI gate result
`npm run lh-ci` exit 0; `npm run build -- --perf-budget` exit 0.
```

## Do's / Don'ts

**Do**
- ✅ Define per-route budgets, not a single global one.
- ✅ Fail the build on breach; warnings rot.
- ✅ Cite before + after numbers in every remediation PR.
- ✅ Use lab (TBT) for CI stability and field (INP) for RUM truth.
- ✅ Lazy-mount third-party behind `requestIdleCallback` or an interaction.
- ✅ Reserve dimensions for any asynchronous layout (images, ads, embeds).

**Don't**
- ❌ Move the budget target up to make CI green without a documented root-cause.
- ❌ Inline every script "for speed"; the long-task tax destroys INP.
- ❌ Use `prefetch`/`preload` liberally — every hint competes for the initial network.
- ❌ Treat "fast on my machine" as evidence — only the CI gate and RUM count.
- ❌ Ship `font-display: block` for non-critical families.
- ❌ Set `will-change: transform` permanently on every moving element.

## Validation Checklist

- [ ] `perf-budgets.ts` lists every route with a threshold per metric.
- [ ] CI runs Lighthouse-CI against built artifacts on every PR.
- [ ] CI runs the bundler budget plugin (`--perf-budget` / `performance: { hints: 'error' }`).
- [ ] A breach fails the build (exit non-zero).
- [ ] Field/RUM capture wired (`web-vitals` + `sendBeacon`).
- [ ] LCP element identified and optimized per route.
- [ ] Long-task count = 0 on initial load for primary routes.
- [ ] All initial images have explicit `width`/`height` or `aspect-ratio`.
- [ ] Third-party scripts gated behind idle or interaction triggers.
- [ ] Fonts: ≤ 2 families, `font-display: swap`, critical one `preload`ed.
- [ ] Report committed with before/after numbers and root-cause list.
- [ ] Budget raise (if any) documented with previous threshold + justification.

## Summary

A performance budget is a measurable, enforced contract: per-route thresholds for each Core Web Vital and asset class, gated in CI, regressed with surgical fixes, and reported with before/after numbers. Define the budgets from RUM p75, gate them red in the pipeline, profile the offending LCP elements and long tasks, fix one variable at a time, and never move a threshold without a written root cause.