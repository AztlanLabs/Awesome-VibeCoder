---
name: technical-writing-diataxis
description: 'Diátaxis validation (tutorial/how-to/reference/explanation), docstring-driven reference generation, runnable-example enforcement, and plain-language scoring (Hemingway/Flesch) — the canonical documentation-structure skill consumed by Technical Writer.'
---

# Technical Writing — Diátaxis Validation

This skill turns "write good docs" into an enforceable checklist. Documentation is not done because it exists — it is done when every page can be classified into exactly one Diátaxis quadrant, every code sample actually runs, and the prose scores within a plain-language readability target.

Diátaxis is a documentation framework built on a simple observation: **users have four fundamentally different needs** (learning, doing, looking up, understanding), and mixing them on one page serves none of them well.

---

## When to Use

- Authoring, restructuring, or auditing any user-facing documentation (README, docs site, API reference, onboarding guide).
- After an API contract or public surface changes and docs need regeneration (see `workflows/docs-regen.workflow.md`).
- When a documentation PR review needs an objective structure/readability check, not just a subjective "reads fine to me."
- When existing docs mix tutorial, how-to, reference, and explanation content on the same page and users report confusion.

## Prerequisites

- The docs' current structure (existing files/headings) to classify against the four quadrants.
- Access to run any code samples the docs contain, to verify they execute.

---

## 1. The Four Quadrants

| Quadrant | User need | Characteristic | Example |
|---|---|---|---|
| **Tutorial** | "Teach me" | A guided, linear learning experience for a newcomer; optimized for the user succeeding, not for completeness | "Getting Started: build your first X" |
| **How-to Guide** | "Show me how to solve this" | A goal-oriented recipe for someone who already knows the basics | "How to rotate an API key" |
| **Reference** | "Tell me exactly" | Dry, complete, structurally consistent description of the system (every parameter, every option) | API reference, config schema |
| **Explanation** | "Help me understand" | Discursive, background/context/rationale — the "why," not the "how" | "Why we use cursor pagination" |

### Rules

- **Every page MUST be classifiable into exactly one quadrant.** A page that's 40% tutorial and 40% reference serves neither reader well — split it.
- **Tutorials MUST NOT branch or offer options** ("you could also do X instead") — a tutorial is one guaranteed-successful path; alternatives belong in a How-to guide or Explanation.
- **Reference MUST NOT include narrative rationale** ("we chose this because...") — that belongs in Explanation; Reference is for lookup speed, not persuasion.
- **How-to guides MUST assume prior knowledge** — they should not re-teach concepts a Tutorial already covers; link to the Tutorial/Explanation instead of re-explaining.

## 2. Docstring-Driven Reference

Reference documentation should be generated from the source of truth (docstrings, type annotations, OpenAPI/AsyncAPI specs), not hand-maintained in parallel — a hand-maintained reference drifts from the actual API the moment either changes without the other.

### Rules

- **Generate, don't transcribe.** Use the language's docstring/doc-comment tooling (JSDoc/TSDoc, Python docstrings + Sphinx/mkdocstrings, Rustdoc, godoc) or the API spec (`docs/opencode.json`-adjacent OpenAPI/AsyncAPI files — see `skills/api-contract-first/SKILL.md`) as the single source, and regenerate reference pages from it.
- **Every public symbol needs a docstring before it ships** — an undocumented public function/endpoint is a reference-documentation gap by definition, not an acceptable omission.
- **Docstrings state contract, not implementation** — describe parameters, return value, exceptions/error responses, and pre/post-conditions; don't describe internal implementation details that aren't part of the contract.

## 3. Runnable Examples

Every code sample in documentation is a claim that the code works. An untested sample is a claim nobody has verified.

### Rules

- **Every code sample MUST be extracted and run in CI**, not hand-copied into the doc and left unverified — use a doc-testing tool (doctest, `mdtest`-style runners, or a script that extracts fenced code blocks and executes them) so a breaking API change fails the docs build, not just the docs' accuracy.
- **Examples MUST be complete enough to run as shown** — no unexplained `...` elisions of required setup; if brevity matters, link to a full runnable example rather than showing a fragment that silently doesn't work standalone.
- **Pin example dependencies/versions** the same way you'd pin them in a real project — an example that only worked against a since-changed API version is worse than no example.

## 4. Plain-Language Scoring

Documentation prose (Tutorials, How-to guides, Explanations — not Reference, which is intentionally terse/structured) should be measurably readable, not just "clear to the person who already understands the system."

### Rules

- **Target a Flesch Reading Ease score of 60+ (or Flesch-Kincaid grade level ≤ 9)** for tutorial and how-to prose — technical concepts can still be explained in plain sentences; a low score usually means overlong sentences and unnecessary jargon, not irreducible complexity.
- **Run a Hemingway-style readability check** (or an equivalent tool) in the docs review process and flag sentences it marks "hard to read" or "very hard to read" for a rewrite pass, not as optional polish.
- **Prefer active voice and short sentences in Tutorials specifically** — a newcomer following a Tutorial step-by-step is the least tolerant reader of dense, passive-voice prose; save nuance and hedging for Explanation content.
- **Reference content is exempt from the prose-readability target** but must instead be measured for **structural consistency** (every entry has the same fields in the same order) — a Reference's "readability" is scannability, not sentence-level plain language.

## 5. Auditing Existing Docs

When inheriting an undocumented or poorly-structured docs tree:

1. Inventory every existing page and classify it into a quadrant (or "unclassifiable — needs splitting").
2. For each unclassifiable page, split it into the appropriate quadrant-specific pages, moving content rather than duplicating it.
3. Extract and verify every code sample; flag any that no longer run.
4. Run the plain-language check on prose pages (Tutorial/How-to/Explanation) and flag pages below the target score.
5. Cross-link: Tutorials link forward to relevant How-to guides; How-to guides link to Reference for exact parameter details; Explanation is linked from both, not duplicated into both.

---

## Anti-Patterns

- **The "kitchen sink" README** — tutorial, reference, and rationale all crammed into one file with no clear boundary between them.
- **Hand-maintained reference docs alongside a source of truth that's not the reference itself** (docstrings/spec) — guaranteed to drift.
- **Code samples that were never run** — copy-pasted from an earlier version of the API and silently broken.
- **"Wall of text" explanations inside a Tutorial** — a newcomer trying to complete step 3 doesn't need three paragraphs of architectural rationale interrupting the steps; link out to Explanation instead.
- **Treating readability scoring as optional polish** rather than a gate — an unscored, unreviewed prose page is exactly how jargon-heavy, hard-to-follow docs ship.

## Indicators of Done

| Indicator | Target |
|-----------|--------|
| Quadrant classification | Every doc page maps to exactly one Diátaxis quadrant; no page mixes tutorial/how-to/reference/explanation content |
| Reference generation | Reference pages are generated from docstrings/specs, with a documented regeneration command, not hand-transcribed |
| Runnable examples | 100% of code samples are extracted and executed in CI; a broken example fails the build |
| Readability | Tutorial/How-to/Explanation prose scores Flesch Reading Ease ≥ 60 (or grade level ≤ 9) |
| Cross-linking | Tutorials link to relevant How-to/Explanation pages; How-to guides link to Reference for exact details |
| Docstring coverage | Every public symbol/endpoint has a docstring before the reference is regenerated |

## Boundaries

### Do

- Always classify a new or edited doc page into exactly one Diátaxis quadrant before writing.
- Always generate reference content from docstrings/specs rather than hand-authoring it in parallel.
- Always verify code samples execute, ideally via an automated CI check.
- Always run a plain-language readability check on narrative prose pages.
- Always cross-link quadrants rather than duplicating content across them.

### Do Not Do

- Do not mix tutorial and reference content on the same page.
- Do not hand-maintain a reference doc that duplicates information available in docstrings/specs.
- Do not ship a code sample that hasn't been run against the current API version.
- Do not treat a low readability score on tutorial/how-to prose as acceptable because "the author understands it."
