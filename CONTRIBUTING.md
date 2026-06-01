# Contributing to Awesome-VibeCoder

Thank you for choosing to contribute to **Awesome-VibeCoder**! We are excited to build a community-driven repository of AI customization assets that help developers collaborate with agents and optimize their workflows.

As a contributor, you help make this repository more robust, up-to-date, and useful for everyone. Please read through this guide to get started.

---

## 🗺️ How Can I Contribute?

### 1. Adding New Customizations
We welcome additions across all core folders:
*   **Agents (`/agents`)**: Personas or roles that utilize specific styles, tools, or memory profiles.
*   **Instructions (`/instructions`)**: Language-specific styling, framework-specific structures, operations, or testing paradigms.
*   **Skills (`/skills`)**: Task-centric runbooks with templates and execution flows.
*   **Workflows (`/workflows`)**: Orchestration blueprints mapping out sequential or concurrent agent execution phases.
*   **Cookbooks (`/cookbook`)**: Reusable code recipes and implementation patterns (e.g. for the GitHub Copilot SDK).

### 2. Enhancing Existing Assets
You can refine existing instructions, optimize agent prompts, or improve the documentation as AI capabilities and framework guidelines evolve.

### 3. Reporting Issues & Feedback
If you discover a bug in an agent's memory logic, an outdated rule in an instruction file, or have ideas for new roles, please open a GitHub Issue describing:
*   The exact asset involved (e.g., `agents/sdlc-developer.agent.md`).
*   The unexpected behavior or problem.
*   Suggestions for resolving the issue.

---

## 🛠️ Development & Style Guidelines

To keep the repository clean, uniform, and easily parseable by both humans and AI models, please follow these guidelines:

### Agent Profiles (`.agent.md`)
*   **File Structure**: Anchor the agent behavior in a Markdown file ending in `.agent.md`.
*   **Shared Memory**: If the agent is part of the `sdlc-*` family, it **must** integrate with the `Always-On Centralized State Architecture`. Ensure it knows how to read/write context files under the `.sdlc/` directory.
*   **Personas**: Define a clear, focused role with distinct boundaries. Avoid creating monolithic agents that handle too many unrelated domains.

### System Instructions (`.instructions.md`)
*   **Granularity**: Keep instructions focused on single subjects (e.g. one language, one framework, or a specific security practice).
*   **Readability**: Use clear headers, bullet points, and code snippets where appropriate.
*   **Tone**: Keep instruction files declarative and descriptive.

### Skill Folders (`/skills`)
*   **Entry Point**: Every skill must reside in a dedicated subfolder anchored by a `SKILL.md` file.
*   **Dual-Mode Behavior**: Outline the skill's behavior when run in *Interactive Mode* (conversing with a user) vs. *Autonomous Mode* (working independently in a workspace).
*   **Deliverables**: Provide clear folder structures for any templates or output files the skill creates.

---

## 🚀 The Pull Request Workflow

1.  **Fork the Repository**: Create a personal copy of the repository on GitHub.
2.  **Create a Feature Branch**:
    ```bash
    git checkout -b feat/add-kubernetes-agent
    ```
3.  **Implement Your Changes**: Follow the style guidelines above and ensure all links are relative and operational.
4.  **Commit Your Work**: We recommend using Conventional Commits for clarity:
    *   `feat: add rust-development instructions`
    *   `fix: resolve memory format conflict in QA tester agent`
    *   `docs: update readme with quickstart updates`
5.  **Submit a Pull Request (PR)**: Open a PR against the `main` branch of the upstream repository.

### Pull Request Checklist
Before submitting your PR, please verify:
- [ ] No absolute local paths are used inside the repository's markdown links.
- [ ] Markdown links reference valid folders or files in the repository.
- [ ] Any new agent has been added to the corresponding overview tables in the root `README.md` and appropriate `docs/README.*.md` files.
- [ ] The change doesn't break backward compatibility for existing `.sdlc/` workspace state conventions unless documented in the PR description.

---

## 📜 Code of Conduct

We are committed to fostering a welcoming and inclusive community. Please be respectful, constructive, and supportive of fellow contributors in all issues, pull requests, and discussions.
