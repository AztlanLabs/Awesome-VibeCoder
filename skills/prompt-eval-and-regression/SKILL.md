---
name: prompt-eval-and-regression
description: 'Golden outputs, model-graded evals, scorer matrix (deterministic, heuristic, LLM-as-judge, human), CI integration with pass/fail thresholds — the canonical prompt evaluation and regression-testing skill consumed by Prompt File Author and QA Tester.'
---

# Prompt Evaluation & Regression Testing

This skill defines the canonical approach to evaluating prompt quality and detecting regressions across prompt changes. It is consumed by **Prompt File Author** (to author evals alongside prompts) and **QA Tester** (to run eval suites in CI and enforce regression gates).

A prompt is not "done" because it reads well — it is done when it has an **eval suite with golden outputs** and a **CI job that fails on regression**. This skill makes that contract explicit and operational.

---

## When to Use

- Any time a new `.prompt.md` file is created, restructured, or has its system/instructions changed.
- Before merging a prompt change to a shared/team prompt library.
- When a model upgrade, temperature change, or context-window change risks breaking prompt behavior.
- When establishing quality baselines for a prompt-driven pipeline (RAG, code-gen, classification, extraction).

## Prerequisites

- A target `.prompt.md` file under review.
- A versioned set of **input fixtures** (the cases the prompt is run against).
- A versioned set of **golden outputs** (the expected results for at least a deterministic subset of cases).
- A CI runner capable of invoking the eval harness (GitHub Actions, GitLab CI, etc.).

---

## 1. Golden Outputs

Golden outputs are the **reference answers** an eval compares model output against. They are the most valuable artifact in the eval suite — losing them means losing the regression net.

### Structure

Store golden outputs alongside the prompt they evaluate:

```text
.github/prompts/
└── summarize-doc.prompt.md
.github/evals/
└── summarize-doc/
    ├── cases.jsonl            # input fixtures (one case per line)
    ├── golden.jsonl           # expected outputs (one per case, keyed by id)
    ├── scorers.yml            # which scorers to run + thresholds
    └── README.md              # how to add a case, how to update goldens
```

### Rules

- **One case per line** in `cases.jsonl` and `golden.jsonl` (JSON Lines format — diff-friendly, line-level CI annotations).
- **Stable case IDs** — never reuse an ID for a different input; instead add a new case and retire the old one.
- **Goldens are immutable per version** — when behavior changes intentionally, bump the eval suite version (`v2/`, `v3/`) rather than mutating existing goldens.
- **At least one deterministic case** per eval — at least one case must be checkable with exact-string or regex matching (not just LLM-graded).
- **No PII in goldens** — sanitize all fixtures and goldens before committing.
- **Goldens cite source** — each golden output includes a `source_ref` field pointing to the spec/contract it derives from.

### Minimum Required Elements

| Element | Required? | Purpose |
|---|---|---|
| `id` | yes | Stable identifier for the case |
| `input` | yes | The fixture input fed to the prompt |
| `expected` | yes | The golden output (or structured form) |
| `source_ref` | yes | Link to the spec, contract, or human verdict the golden derives from |
| `tags` | no | Category tags (e.g. `regression`, `edge-case`, `security`) |
| `difficulty` | no | `easy` / `medium` / `hard` — used to weight scores |

---

## 2. Model-Graded Evals

Model-graded evals use an LLM (often a different, more capable model than the one being evaluated) to **judge** the output of the system under test. They handle fuzzy qualities (helpfulness, tone, completeness) that deterministic checks cannot.

### The Judge Prompt

A judge prompt is itself a `.prompt.md` file (typically prefixed `judge-`). It must:

- State the **rubric** explicitly (1–5 scale, pass/fail, or dimension-specific).
- Accept the **input** and the **candidate output** as named parameters.
- Return a **machine-parseable result** (JSON with `score`, `reasoning`, `dimensions`).
- **Not** leak the candidate's own self-assessment back as the score (no "rate your own answer" loops).
- Be **versioned** alongside the goldens it grades.

### Rules

- **Use a stronger model as judge** when possible (e.g., judge GPT-4 outputs with GPT-4 Turbo or a different family).
- **Rubric must be specific** — "is the answer helpful?" is too vague; "does the answer cite the contract section by its exact heading?" is testable.
- **Blind the judge** — strip model identity, temperature, and prompt-version metadata from the candidate before judging.
- **Report the judge's reasoning** — never just the final score; store the reasoning for spot-audits.
- **Calibrate periodically** — sample 20 judge verdicts per month and have a human audit them; track inter-rater agreement.

---

## 3. Scorer Matrix

A scorer is a function that takes a candidate output and a reference (golden or rubric) and returns a score. A mature eval suite uses a **matrix of scorers** so that no single failure mode goes undetected.

### Scorer Types

| Scorer Type | What It Checks | Example | Strength | Weakness |
|---|---|---|---|---|
| **Deterministic** | Exact string match, regex, JSON-schema validity | "Output must contain `id`, `title`, `status`" | Fast, cheap, unambiguous | Brittle to formatting changes |
| **Heuristic** | Length, keyword presence, custom rules | "Output must mention 'Sunset header' when the deprecation section is present" | Fast, catches obvious misses | Cannot judge quality |
| **LLM-as-judge** | Helpfulness, tone, completeness via rubric | "Does the answer follow the contract-first pattern?" | Handles fuzzy qualities | Expensive, can be gamed |
| **Human** | Expert review on a sample | Security architect signs off on a threat-model output | Highest authority | Slow, expensive, not scalable |

### Rules

- **Every eval suite MUST include at least one deterministic scorer** — this is the regression backstop.
- **Use LLM-as-judge sparingly** — cap at 30% of scorers; deterministic + heuristic scorers are cheaper and more stable.
- **Human review is the final court** — at least 5% of cases should be human-audited each release.
- **Scorers are versioned** with the goldens they run against.
- **Score aggregation is explicit** — declare the aggregation rule (mean? min? pass-rate?) in `scorers.yml`.

### Scorer Configuration (`scorers.yml`)

```yaml
version: 1
suite: summarize-doc
aggregation: mean
thresholds:
  overall: 0.85
  per_scorer:
    deterministic: 1.0      # deterministic must always pass
    heuristic: 0.90
    llm_judge: 0.75
  regression:
    max_score_drop: 0.05    # fail if overall drops >5% from baseline
scorers:
  - name: schema-valid
    type: deterministic
    rule: json-schema-validate(output, schemas/summarize-doc.schema.json)
  - name: cites-source
    type: heuristic
    rule: contains_any(output, ["$ref", "see section"])
  - name: helpfulness
    type: llm_judge
    judge_prompt: judge-helpfulness.prompt.md
    rubric_dimensions: [completeness, accuracy, tone]
```

---

## 4. CI Integration

An eval suite that doesn't run in CI is a **diary, not a test**. The eval harness must be wired into the CI pipeline and **fail the build on regression**.

### CI Job Requirements

- **Runs on every PR** that touches a `.prompt.md` or its `evals/` directory.
- **Posts a summary comment** on the PR with per-case pass/fail and overall score.
- **Fails the build** when any threshold in `scorers.yml` is violated.
- **Uploads artifacts** — the full eval report (`eval-report.json`), per-case logs, and judge reasoning.
- **Caches model responses** for deterministic cases (when the model + temperature + seed are pinned).

### CI Workflow Sketch (`.github/workflows/prompt-evals.yml`)

```yaml
name: Prompt Evals
on:
  pull_request:
    paths:
      - '.github/prompts/**'
      - '.github/evals/**'
jobs:
  evals:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22 }
      - run: npm ci
      - name: Run prompt evals
        run: npm run eval -- --suite=.
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      - name: Upload eval report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: eval-report
          path: eval-report.json
      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const report = require('./eval-report.json');
            // ...post per-case summary as PR comment
```

### Rules

- **Pin model + temperature + seed** for deterministic cases — any un-pinned parameter is a flaky test.
- **Use a separate judge model API key** — never let the system under test grade itself.
- **Surface failures in the PR diff** — annotate changed lines that caused score drops.
- **Track baseline scores** — store the latest main-branch score; fail if any case drops >`max_score_drop`.
- **Never silently skip a case** — if a case is too expensive to run, mark it `deferred` with a reason, don't omit it.

---

## 5. Eval Suite Versioning

Eval suites evolve alongside the prompts they test. Versioning prevents the "moving target" problem where goldens get updated to match buggy outputs.

### Rules

- **Bump suite version** on any change to `cases.jsonl`, `golden.jsonl`, or `scorers.yml`.
- **Keep at least 2 prior versions** in the repo for diff and rollback.
- **Never mutate a released version's goldens** — add a new version instead.
- **Document the bump** in the suite's `README.md` with what changed and why.

### Versioning Convention

```text
.github/evals/
└── summarize-doc/
    ├── v1/
    │   ├── cases.jsonl
    │   ├── golden.jsonl
    │   └── scorers.yml
    ├── v2/                    # current
    │   ├── cases.jsonl
    │   ├── golden.jsonl
    │   └── scorers.yml
    └── README.md
```

---

## 6. When to Add a Case

Add a new eval case when:

- A **bug** is found in production — encode the failing input + correct output as a regression case.
- A **new requirement** is added to the prompt — add a case that exercises the new requirement.
- An **edge case** is discovered during manual review — encode it before the prompt drifts away from handling it.
- A **model upgrade** changes behavior — capture both old and new behavior as separate cases to track the delta.

### Rules

- **One bug → one case** — don't bundle multiple bugs into a single fixture.
- **The case must reproduce the bug** — if the eval passes after the fix, the case is correctly constructed.
- **Tag the case** with `regression` so it stays in the suite even when other cases are pruned.

---

## 7. Anti-Patterns

- **No goldens, no eval** — a prompt without goldens is folklore.
- **"It looks right" is not a score** — subjective review without a rubric is not a scorer.
- **LLM-as-judge for everything** — expensive, noisy, and gameable; reserve for qualities only a model can judge.
- **Mutating goldens to match current output** — that's overfitting to the test, not testing the prompt.
- **Skipping the deterministic backstop** — if you only have LLM-graded cases, a formatting change can break the prompt silently.
- **Eval suite not in CI** — a test that doesn't run is not a test.
- **One scorer, one perspective** — a single scorer misses entire failure modes; use the matrix.
- **PII in fixtures or goldens** — never commit real user data; use synthetic or anonymized inputs.
- **Un-pinned model parameters** — temperature, seed, and model-version must be fixed for deterministic cases.

---

## Indicators of Done

| Indicator | Target |
|-----------|--------|
| Golden outputs | Every prompt in the library has a versioned `golden.jsonl` with at least one deterministic case |
| Scorer matrix | Every eval suite has ≥1 deterministic, ≥1 heuristic, and (if fuzzy qualities matter) ≥1 LLM-as-judge scorer |
| CI integration | A CI job runs the eval suite on every PR that touches a `.prompt.md` and fails the build on threshold violation |
| Threshold declaration | `scorers.yml` declares both per-scorer and overall pass thresholds; no implicit "looks fine" |
| Regression baseline | The latest main-branch score is stored as the baseline; PRs failing `max_score_drop` are blocked |
| Versioning | Eval suites are versioned; prior versions are retained for rollback and diff |
| Bug → case loop | Every production prompt bug produces a regression case in the next release |
| Judge calibration | At least 5% of LLM-judge verdicts are human-audited per release |

## Boundaries

### Do

- Always create goldens alongside a new prompt — no exceptions.
- Always include at least one deterministic scorer per eval suite.
- Always wire the eval suite into CI before merging a prompt to a shared library.
- Always pin model, temperature, and seed for deterministic cases.
- Always version eval suites on changes to `cases.jsonl`, `golden.jsonl`, or `scorers.yml`.
- Always tag a case as `regression` when it encodes a real production bug.
- Always store the judge's reasoning alongside the score for spot-audits.
- Always sanitize fixtures and goldens — no PII, no secrets.

### Do Not Do

- Do not grade a model's output with the same model (use a separate judge).
- Do not mutate released goldens to match current output — bump the version.
- Do not ship a prompt without an eval suite.
- Do not use only LLM-as-judge scorers — deterministic + heuristic are the regression backstop.
- Do not skip the CI integration "because it works locally."
- Do not commit fixtures or goldens containing PII or secrets.
- Do not silently skip a case — mark it `deferred` with a reason or fix it.
- Do not treat subjective review as a scorer — write a rubric first.
