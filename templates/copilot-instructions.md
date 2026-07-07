# Repo-wide Copilot instructions

<!--
Copy this file to .github/copilot-instructions.md in your target project.
Copilot loads it into every request made in the repo. See
docs/integrations/github-copilot.md for the full walkthrough.
-->

This project uses the Awesome-VibeCoder SDLC multi-agent system. When asked to act as a role, load the body of `agents/<role>.agent.md` (e.g. `agents/sdlc-software-architect.agent.md`) as your operating manual and follow it.

Shared state lives in `.sdlc/` at the project root. Always read `.sdlc/activeContext.md`, `.sdlc/progress.md`, and the relevant `.sdlc/contracts/*.md` before acting. Write source code to the project's real source tree — never into `.sdlc/`.

Build/test/lint commands:
- <install command, e.g. `npm install`>
- <build command, e.g. `npm run build`>
- <test command, e.g. `npm test`>
- <lint command, e.g. `npm run lint`>

Treat any agent-file `Definition of Done` as a hard gate: only mark a task complete after a real build + test run with the command and result cited in `.sdlc/progress.md`.

Reusable prompts live in `.github/prompts/`. Reusable skills are addressed by relative path (`skills/<name>/SKILL.md`) or copied into `.github/skills/` for discoverability — see [`docs/integrations/github-copilot.md`](../docs/integrations/github-copilot.md).
