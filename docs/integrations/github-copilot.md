# Linking Awesome-VibeCoder into GitHub Copilot

> Goal: use GitHub Copilot (VS Code Copilot Chat + Copilot cloud agent) with this repo's agents, path-specific instructions, skills, prompts, workflows, and MCP servers, and run the SDLC pipeline against the `.sdlc/` shared state.

The repository is **Copilot-shaped by convention**: its `agents/*.agent.md`, `instructions/*.instructions.md`, and `skills/<name>/SKILL.md` sources are designed to be copied on demand into a target project's `.github/agents/`, `.github/instructions/`, `.github/prompts/`, and `.github/skills/`, alongside a Copilot-flavoured [MCP integration guide](../mcp-integration-guide.md). This guide ties those pieces together end-to-end.

---

## What you are linking

| Asset | Repository path | Copilot target |
| --- | --- | --- |
| Repo-wide rules | root README + a generated `.github/copilot-instructions.md` | loaded into every Copilot request in the repo |
| Path-specific instructions | `instructions/*.instructions.md` (have `applyTo` frontmatter) | `.github/instructions/*.instructions.md` |
| Agents / reusable chats | `agents/*.agent.md` | referenced by `AGENTS.md`; bodies used as custom chat mode prompts |
| Reusable prompts | `*.prompt.md` (authored by `agents/PromptFileAuthor.agent.md`) | copy into `.github/prompts/` |
| Skills | `skills/<name>/SKILL.md` | copy the ones you need into `.github/skills/`, or reference on demand |
| Workflows | `workflows/*.workflow.md` | referenced from the orchestrator agent body / a prompt |
| Shared state | `.sdlc/` (created at runtime) | read/written by every agent; nothing to wire |
| MCP | `.github/mcp.json` (Copilot cloud agent) or VS Code `mcp.json` | tool surface for browser/GitHub/Playwright |

---

## Prerequisites

- GitHub Copilot subscription; Copilot enabled in the repository's Settings → Code & automation → Copilot.
- VS Code with the GitHub Copilot + Copilot Chat extensions, **or** the Copilot cloud agent on github.com.
- This repository cloned and opened in VS Code as a workspace (or pushed to your GitHub fork and opened from github.com/copilot).
- A **target project** where the SDLC team will work. You can either run Awesome-VibeCoder's assets from within the Awesome-VibeCoder repo itself (dogfood) or copy the specific `agents/`, `instructions/`, and `skills/` files you need into your target project's `.github/`.

---

## Step 1 — Repository-wide custom instructions

Create `.github/copilot-instructions.md` in the **target project**:

```markdown
# Repo-wide Copilot instructions

This project uses the Awesome-VibeCoder SDLC multi-agent system. When asked to act as a role, load the body of `agents/<role>.agent.md` (e.g. `agents/sdlc-software-architect.agent.md`) as your operating manual and follow it.

Shared state lives in `.sdlc/` at the project root. Always read `.sdlc/activeContext.md`, `.sdlc/progress.md`, and the relevant `.sdlc/contracts/*.md` before acting. Write source code to the project's real source tree — never into `.sdlc/`.

Build/test/lint commands:
- npm install
- npm run build
- npm test
- npm run lint

Treat any agent-file `Definition of Done` as a hard gate: only mark a task complete after a real build + test run with the command and result cited in `.sdlc/progress.md`.
```

Copilot loads this into every request made in the repo.

---

## Step 2 — Path-specific instructions

The repo's instruction files already declare `applyTo` glob frontmatter (e.g. `applyTo: "**/*.tsx, **/*.ts, **/*.jsx, **/*.js, **/*.css"` in `instructions/nextjs.instructions.md`). Make them visible to Copilot by placing them under `.github/instructions/`:

```bash
# In the target project:
mkdir -p .github/instructions
cp ~/src/Awesome-VibeCoder/instructions/nextjs.instructions.md          .github/instructions/
cp ~/src/Awesome-VibeCoder/instructions/tailwind-v4-vite.instructions.md .github/instructions/
cp ~/src/Awesome-VibeCoder/instructions/security-and-owasp.instructions.md .github/instructions/
cp ~/src/Awesome-VibeCoder/instructions/a11y.instructions.md           .github/instructions/
# …add the languages/frameworks this project actually uses
```

> `.github/instructions/` is not pre-populated in this repo — copy the specific instruction files your project needs, as shown above.

Adjust `applyTo` per file to match your project's structure. Copilot attaches the instructions to any request touching a matching file.

Use `excludeAgent` to keep an instruction out of code review or cloud agent:

```markdown
---
applyTo: "**/*.ts"
excludeAgent: "code-review"
---
```

---

## Step 3 — Declare `AGENTS.md` for Copilot cloud agent

Copilot cloud agent reads the nearest `AGENTS.md` in the directory tree. Create a root `AGENTS.md` (or `.github/AGENTS.md`):

```markdown
# Agents guide

This repo's agent personas live in `agents/`. Each `agents/<name>.agent.md` is a self-contained role:
- Frontmatter declares `name`, `description`, and the chat participant's `tools`.
- The body is the role's operating manual (workflow, patterns, indicators of done, boundaries).

When asked to perform an SDLC role, load the matching agent file and follow it. Coordinate via the `.sdlc/` shared state. The orchestrator (`agents/sdlc-orchestrator.agent.md`) decomposes a goal and dispatches roles; the workflows (`workflows/sdlc-sequential.workflow.md`, `workflows/sdlc-parallel.workflow.md`) define phase order.

Reusable prompts: copy into `.github/prompts/`. Reusable skills: `skills/<name>/SKILL.md`, copied on demand into `.github/skills/`.
```

> Alternatively (or additionally) you can use a root `CLAUDE.md` / `GEMINI.md` — Copilot cloud agent accepts any of these. `AGENTS.md` is the cross-tool convention.

---

## Step 4 — Custom chat modes / prompts

Copy the `*.prompt.md` files you need into the target project's `.github/prompts/` (if you are not already in the Awesome-VibeCoder repo). For per-role chat modes in VS Code, create `.github/chatmodes/<role>.chatmode.md` (VS Code Copilot chat modes support the `name`, `description`, `tools`, `instructions` fields). The chat mode body can pasteload a repo agent file:

```markdown
---
name: SDLC Backend Engineer
description: Implement APIs and service layers following the .sdlc/ contracts.
tools: ['vscode', 'execute', 'read', 'edit', 'search', 'web']
---

Load `agents/sdlc-backend-engineer.agent.md` and follow it. Always consume `.sdlc/contracts/db-schema.md` and `.sdlc/contracts/api-contracts.md` unchanged; write code to the project source tree; record build/test command+result in `.sdlc/progress.md`.
```

The repo's agents already declare the Copilot-style `tools` array (`vscode, execute, read, agent, edit, search, web, browser, todo`), so they drop straight into chat-mode / custom-participant frontmatter with minimal massaging.

---

## Step 5 — Link skills

The repo's skills are addressed by relative path in agent file bodies ("Always load `skills/sdlc-shared-memory/SKILL.md`"). For GitHub Copilot's discoverability:

- In the target project, either copy the skills you need into `.github/skills/`, or add an instruction line in `AGENTS.md` / `copilot-instructions.md` that names each skill and its trigger conditions, so Copilot loads it on demand.

Because Copilot Chat/Copilot cloud agent's instruction budget is shared, prefer the on-demand pattern over embedding all 47 skills at once.

---

## Step 6 — Workflows

Reference the workflow files from `AGENTS.md` (already done in Step 3) and from a reusable prompt. To run a workflow:

```text
@workspace load workflows/sdlc-sequential.workflow.md and execute it phase by phase against .sdlc/.
```

Or with the cloud agent, after opening the repo on github.com/copilot:

```text
Run the SDLC sequential workflow defined in workflows/sdlc-sequential.workflow.md against this repository.
```

---

## Step 7 — MCP servers

For Copilot cloud agent, declare servers in `.github/mcp.json`:

```json
{
  "mcpServers": {
    "playwright": {
      "type": "local",
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest", "--caps=vision"]
    },
    "github": {
      "type": "local",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "${env:COPILOT_MCP_GITHUB_TOKEN}" }
    }
  }
}
```

> **Secret prefix**: Copilot cloud agent only exposes repository secrets prefixed `COPILOT_MCP_`. Reference them as `${{ secrets.COPILOT_MCP_* }}` and the host filters out anything else. See the [MCP integration guide](../mcp-integration-guide.md) for the full secret/namespacing rules.

For VS Code Copilot Chat, add `.vscode/mcp.json` with the same shape (VS Code's MCP support). Agent tools namespaced as `<server>/<tool>`.

---

## Step 8 — Run a canonical SDLC session

1. Confirm `.github/copilot-instructions.md`, `.github/instructions/`, `AGENTS.md`, and `.github/mcp.json` exist in the target project.
2. In VS Code Copilot Chat, pick the chat mode for `SDLC: Software Architect` (or use `@workspace`).
3. Task it to produce the architecture and ADRs:

   ```text
   Act as the SDLC Software Architect: scaffold .sdlc/ if missing, read .sdlc/projectbrief.md (create it from this goal: "<your goal>"), produce .sdlc/architecture.md + .sdlc/systemPatterns.md + ADRs in .sdlc/decisions/.
   ```

4. Verify `.sdlc/architecture.md` and at least one `ADR-*.md` exist.
5. Continue with the next role, e.g.:

   ```text
   Act as the SDLC Backend Engineer: read .sdlc/architecture.md and .sdlc/contracts/db-schema.md, write API contracts to .sdlc/contracts/api-contracts.md, then implement endpoints in src/api/; run `npm test` and cite the result in .sdlc/progress.md.
   ```

6. Toggle code-review custom instructions on or off in repo Settings → Copilot → Code review ("Use custom instructions when reviewing pull requests").

---

## Verification checklist

- [ ] `.github/copilot-instructions.md` exists.
- [ ] `.github/instructions/*.instructions.md` each declare a valid `applyTo` glob.
- [ ] `AGENTS.md` exists at the repo root.
- [ ] The chat modes / `@workspace` can read `agents/sdlc-*.agent.md`.
- [ ] `.github/mcp.json` servers connect (no secret-prefix warnings).
- [ ] Running an architect task creates `.sdlc/architecture.md` + ADRs.
- [ ] `.sdlc/progress.md` accumulates real command+result lines after each role.

---

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| Instructions not applied | `applyTo` glob mismatch or repo disabled | Settings → Copilot → Code review → enable custom instructions; verify `applyTo` syntax |
| Secret not exposed | non-`COPILOT_MCP_` prefix | prefix the secret name; reference as `${{ secrets.COPILOT_MCP_* }}` |
| Agent tools error | tool name not in the agent's `tools` list | add it to frontmatter `tools:` array |
| MCP server `tools: ['*']` flagged | repo policy restricts tools | list specific tool names instead of `'*'` |
| Too much context | 107 instructions + 47 skills loaded at once | use on-demand reference from `AGENTS.md`, not bulk paste |

---

## See also

- [Awesome-VibeCoder root README](../../README.md)
- [SDLC system overview](../README.sdlc-system.md)
- [MCP integration guide (Copilot-flavoured)](../mcp-integration-guide.md)
- GitHub Copilot docs: <https://docs.github.com/copilot> · custom instructions: <https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot>