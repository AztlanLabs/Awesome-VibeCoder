---
name: web-accessibility-audit
description: 'Running WCAG 2.2 AA/AAA accessibility audits on web apps, combining automated tooling with manual checks, and producing a structured remediation report.'
---

# Web Accessibility Audit

Your role in an accessibility audit is to act as a measured, evidence-driven evaluator: combine automated scanners (which catch mechanical regressions) with manual checkpoints (which catch semantic and interaction regressions), then produce a structured remediation report with a per-issue severity, the affected WCAG 2.2 Success Criterion, the failing markup, the recommended markup, and a re-test command.

WCAG is non-negotiable baseline; do not negotiate away a P0 finding. When the user asks you to audit a route, component, product, or PR diff, run the full workflow below and emit the Markdown report.

---

## When to Use This Skill

- Auditing a new route, page, or feature for accessibility before release.
- Triaging a regression reported by a screen-reader user or a scanner alert.
- Reviewing a PR diff for newly introduced accessibility violations.
- Establishing the baseline audit for an existing product.

## Prerequisites

- A running, interactive build of the target page (and the ability to disable animations / CSS reductions).
- Local access to at least one automated engine (axe-core) and one manual screen reader (NVDA or VoiceOver).
- The WCAG 2.2 reference for Success Criteria (SC) numbering (1.x perceivable, 2.x operable, 3.x understandable, 4.x robust).
- An agreed conformance target: **AA** (default) or **AAA** (where specified).

---

## POUR Principles

Every finding maps back to one of the four POUR principles. State the principle in each finding so remediation keeps intent, not just markup, in view.

| Principle   | Meaning                                                  | WCAG chapter |
|-------------|----------------------------------------------------------|--------------|
| Perceivable | Users can perceive the content (it is not invisible to any sense) | 1.x          |
| Operable    | Users can operate every interface element                | 2.x          |
| Understandable | Content and operation are understandable              | 3.x          |
| Robust      | Content works across user agents and assistive tech      | 4.x          |

## Perceivable / Operable / Understandable / Robust Checklist

### Perceivable (1.x)
- [ ] Every image has appropriate `alt` (decorative → `alt=""`, informative → described, actionable → text label).
- [ ] All form controls have a programmatically associated `<label>` (or `aria-label`/`aria-labelledby`).
- [ ] Color contrast ≥ 4.5:1 for body text, ≥ 3:1 for large text and non-text UI.
- [ ] Information is not conveyed by color alone (adds icon, underline, or text).
- [ ] Captions exist for pre-recorded video; transcripts for audio.
- [ ] Content reflows at 320 CSS px without horizontal scroll and without loss of function.
- [ ] Text resizable to 200% without clipping or overlap.

### Operable (2.x)
- [ ] All actions reachable with keyboard alone; no mouse-only interactions.
- [ ] Logical tab order; visible `:focus-visible` styles on every interactive element.
- [ ] No keyboard traps; focus can leave any component with `Esc`/`Tab`.
- [ ] Skip-to-content link present as the first focusable element.
- [ ] Page has a logical heading hierarchy with exactly one `<h1>`.
- [ ] No content flashes more than 3×/second (seizure-safe).
- [ ] Timeouts are announced and extendable (2.2.1).
- [ ] Touch targets ≥ 24×24 CSS px (2.5.8, AA) / 44×44 (AAA recommended).

### Understandable (3.x)
- [ ] Language declared via `<html lang>`.
- [ ] Page language changes flagged with `lang` attribute on the element.
- [ ] Form errors are programmatically associated, descriptive, and offer correction.
- [ ] Inputs use `autocomplete` attributes where appropriate (2.2 in WCAG 2.2).
- [ ] No surprising context changes on focus / input without warning.
- [ ] Instructions are present for inputs that require specific formats.

### Robust (4.x)
- [ ] Valid HTML parses without structural errors (no duplicate IDs, nested interactive elements).
- [ ] All custom components expose correct role, name, and state via ARIA.
- [ ] Status messages use `role="status"` or `aria-live` regions.
- [ ] Components work across at least two screen readers (NVDA + VoiceOver).

## Automated Tooling

| Tool        | Scope                                         | Output shape          | When to use                       |
|-------------|----------------------------------------------|-----------------------|-----------------------------------|
| **axe-core** | DOM-level rules, ~50 SCs                     | JSON violations list  | Programmatic tests, CI gate        |
| **Lighthouse** | Audits a URL with axe-core + perf/SEO      | Score + issues        | Pre-release, baseline scoring      |
| **Pa11y**   | CLI wrapper around HTML CodeSniffer          | CLI exit code + JSON | CI gate, URL batch                 |
| **WAVE**    | Browser extension + API, visual overlay      | Sidebar icons         | Manual exploration, contrast/structure overview |
| **NVDA**    | Windows screen reader                        | Spoken feedback       | Manual pass of every interactive surface |
| **VoiceOver** | macOS screen reader                        | Spoken feedback       | Manual pass on Mac                |
| **Keyboard only** | No mouse, Tab/Shift+Tab/Arrows/Space/Enter | Manual traversal      | Always run before scanner          |

Automated catches ~30–40% of issues; it never validates semantics, keyboard flow, or screen-reader announcement quality, so it cannot be the only gate.

## Per-Component Audit Workflow

For every audited component, run these five passes and record evidence:

1. **DOM snapshot** — render the component, save the HTML, and assert structural invariants (no nested `<button>`, no orphan `<label>`, no duplicate IDs).
2. **Keyboard-only pass** — Tab through every interactive element (and arrow within compound widgets). Verify focus is visible, order matches reading order, and `Esc` returns to a safe state.
3. **Screen-reader pass** — with NVDA or VoiceOver enabled, articulate every interactive element's name, role, and state; trigger every action and listen for live-region announcements.
4. **Contrast pass** — record the foreground and background color of every informational text and non-text UI element; compute the ratio and assert against target level.
5. **Focus management pass** — for paths that open/close overlays (dialog, menu, popover): verify focus moves into the overlay on open, returns to the trigger on close, and the overlay's focus trap is correct.

Record each pass result (`PASS`, `FAIL`, `N/A`) per component in the report.

## Indicators

| Indicator                          | Measurement                                  | Sort by         |
|------------------------------------|----------------------------------------------|-----------------|
| Issue severity                     | P0 (blocker), P1 (serious), P2 (minor)       | Fix P0 first    |
| Contrast ratio failures            | Ratio < target ratio                         | Lowest first    |
| Missing labels %                   | `(#inputs without label) / (#inputs)`         | > 0 = P1 sweep  |
| Keyboard-reachable %               | `(#keyboard-operable) / (#interactive)`       | Must be 100%    |
| ARIA correctness                   | Manual SR pass announcements matched name/role/state | Any mismatch = P1 |
| Duplicate IDs                      | Count                                        | Any = P0        |
| Heading order gaps                 | Skipped levels (e.g. h1 → h3)                | Any = P1        |

## Common Patterns (with Correct Markup)

### Modal Focus Trap

```html
<div role="dialog" aria-modal="true" aria-labelledby="dlg-title">
  <h2 id="dlg-title">Settings</h2>
  <button type="button" aria-label="Close" data-close>×</button>
  <!-- Tab cycle: first focusable gets focus on open; Tab on last wraps to first; Shift+Tab on first wraps to last; Esc closes -->
</div>
```

On open: store the previously focused element, move focus to the dialog's first focusable. On close: restore focus to that element. Intercept `Tab`/`Shift+Tab` to keep focus inside.

### Menu ARIA

```html
<ul role="menubar" aria-label="Main">
  <li role="none">
    <button role="menuitem" aria-haspopup="true" aria-expanded="false" aria-controls="submenu">File</button>
    <ul id="submenu" role="menu">
      <li role="none"><button role="menuitem">Open</button></li>
      <li role="none"><button role="menuitem">Save</button></li>
    </ul>
  </li>
</ul>
```

Arrow keys navigate within `role="menu"`. `Escape` closes a submenu and returns focus to the parent menuitem.

### Form Labels & Errors

```html
<label for="email">Email</label>
<input id="email" name="email" type="email" required autocomplete="email"
       aria-describedby="email-hint email-err" aria-invalid="false">
<small id="email-hint">We never share your email.</small>
<span id="email-err" role="alert" hidden></span>
```

On validation failure: set `aria-invalid="true"`, fill `#email-err`, show it. The `role="alert"` announces automatically.

### Skip Link

```html
<a href="#main" class="skip-link">Skip to content</a>
<main id="main" tabindex="-1">…</main>
```

`tabindex="-1"` makes `<main>` programmatically focusable so the link target receives focus, not just scroll.

### Live Region

```html
<div role="status" aria-live="polite" id="sr-status"></div>
```

Use `role="status"` (polite) for non-critical updates; `role="alert"` (assertive) for errors requiring immediate attention. Avoid `aria-live="assertive"` for general messages — it interrupts the user.

## Reporting Template (Markdown)

Produce one report per audit. Persist it under `.sdlc/audits/a11y-<route>-<date>.md` when working inside an SDLC workspace; otherwise emit inline.

```markdown
# Accessibility Audit — <route or component>
Date: YYYY-MM-DD   Auditor: <name>
Target: WCAG 2.2 AA   Build: <commit>

## Summary
- Total findings: X (P0: A, P1: B, P2: C)
- Automated coverage: axe-core Lighthouse score / 100
- Manual coverage: keyboard □ PASS, SR □ PASS, contrast □ PASS, focus mgmt □ PASS

## Findings

### F-001 — <short title>  [P0]
- Component: <path:line>
- WCAG SC: 2.4.3 Focus Order (Operable)
- Failing markup: `<div onclick="open()">…</div>`
- Recommended markup: `<button type="button" aria-haspopup="dialog">…</button>`
- Re-test: `npx axe-core <url> --tags=wcag2a`

### F-002 — …

## Indicators
| Indicator             | Value  | Target | Status |
|-----------------------|--------|--------|--------|
| Missing label inputs  | 3 / 18 | 0      | FAIL   |
| Contrast failures     | 2      | 0      | FAIL   |
| Keyboard-reachable    | 100%   | 100%   | PASS   |

## Sign-off
- [ ] All P0 closed
- [ ] All P1 scheduled for next sprint
- [ ] Re-audit date: YYYY-MM-DD
```

## Do's / Don'ts

**Do**
- ✅ Always run a keyboard-only pass first; it exposes structural issues the scanner won't.
- ✅ Cite the WCAG 2.2 SC number on every finding.
- ✅ Record before/after markup on each finding so non-auditors can implement.
- ✅ Re-run the scanner after fixes; attach the command in the report.
- ✅ Use the most restrictive live-region politeness that still meets UX.

**Don't**
- ❌ Treat automated-green as accessible-green.
- ❌ Add ARIA to "fix" semantics when the right HTML element exists (`<button>` over `<div role="button">`).
- ❌ Use `aria-hidden="true"` on a focusable element or its ancestor.
- ❌ Hide focus outlines globally without a replacement `:focus-visible` style.
- ❌ Use color alone to convey state (error, success, required).
- ❌ Auto-play audio longer than 3 seconds without a controls.

## Validation Checklist (mapped to WCAG SCs)

| Check                                            | SC                                        |
|--------------------------------------------------|-------------------------------------------|
| All images have appropriate `alt`                | 1.1.1 Non-text Content                    |
| Form controls have associated labels             | 1.3.1, 3.3.2, 4.1.2                       |
| Body text contrast ≥ 4.5:1 (AAA 7:1)             | 1.4.3, 1.4.6                              |
| Large text and UI ≥ 3:1                          | 1.4.11                                    |
| Page reflows at 320px and zooms to 200%          | 1.4.10, 1.4.4                             |
| Keyboard-only operation, no traps                | 2.1.1, 2.1.2                              |
| Visible focus on every interactive element       | 2.4.7, 1.4.11                             |
| Skip link present                                | 2.4.1                                     |
| One `<h1>`, logical hierarchy                    | 1.3.1, 2.4.6                              |
| Touch targets ≥ 24×24 CSS px                     | 2.5.8                                     |
| `<html lang>` set                                | 3.1.1                                     |
| Form errors programmatically associated          | 3.3.1, 3.3.3, 4.1.3                       |
| Status messages use `aria-live` / `role=status`  | 4.1.3                                     |
| Valid HTML, no duplicate IDs                     | 4.1.1, 4.1.2                              |
| Custom widgets expose role/name/state             | 4.1.2                                     |
| No flashing > 3×/sec                             | 2.3.1                                     |

## Summary

Accessibility audits blend automated scanners (which catch structure) with manual keyboard, screen-reader, and contrast passes (which catch semantics). Every finding carries a WCAG 2.2 SC, a severity, before/after markup, and a re-test command. P0s block release; P1s schedule into the next sprint; P2s fix when feasible. The report lives next to the code so the audit is replayable, and the checklist mirrors the SCs so nothing measurable is forgotten.