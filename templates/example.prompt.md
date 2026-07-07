---
description: "<concise description of what this prompt accomplishes>"
agent: "<agent|ask|edit>"
tools: ["<tool-1>", "<tool-2>"]
---

# <Title>

<Persona / role definition — who the model is acting as for this task>

## Constraints

- <Non-negotiable rule 1>
- <Non-negotiable rule 2>

## Workflow

1. <Step-by-step instruction for the model>
2. <Step-by-step instruction for the model>

## Context / Inputs

- `${selection}` — <what this variable contains and how it's used>
- `${file}` — <what this variable contains and how it's used>
- `${input:name}` — <what this variable contains and how it's used>

<!--
Everything above this PROMPT: marker is model-facing instruction.
Everything after it is the user-facing prompt body — what to accomplish,
inputs, expected output, and definition of done. See
agents/PromptFileAuthor.agent.md for the full authoring convention, and run
it (or the prompt-builder / prompt-maintainer / prompt-markdown-sanitizer /
prompt-eval-and-regression skills directly) to create or refine prompts
following this template.
-->

PROMPT: <The actual prompt — what to accomplish, expected output, and a concrete definition of done>
