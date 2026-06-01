---
name: ai-workflow-architect
description: 'Ensure clear boundaries between Agents and Skills, enforce semantic naming conventions, clarify objectives, prevent logic loops, eliminate redundancy, and build highly reliable, stateless AI workflows.
This skill is critical for designing and auditing AI Agents and Skills to ensure they are deterministic, maintainable, and free of logic errors.'
---

**Trigger:** Invoke this skill whenever the user asks to design, evaluate, fix, debug, or create an AI Agent or an AI Skill.

## 1. Core Architectural Definitions
Before designing or auditing any workflow, you must strictly separate the two primary entities:
* **The AI Agent (The Execution Engine):** The active, stateful reasoning loop. Agents maintain context, orchestrate tools, make decisions, and invoke skills. *Agents do the thinking.*
* **The AI Skill (The Domain Blueprint):** A passive, stateless, atomic document (usually a Markdown file). It defines the strict rules, constraints, and standard operating procedures for a specific task. *Skills provide the knowledge.*

## 2. Rules for Skill & Agent Design

### A. Naming Conventions & Semantic Clarity (CRITICAL)
Agents rely on semantic matching to load skills. Names and objectives must be ruthlessly clear.
* **Evaluate the Name:** Does the current name immediately describe the *exact* capability (for a skill) or the *exact* role (for an agent)? If not, you must propose a better one.
* **Agent Naming:** Should be Role-based or Persona-based (e.g., `SecurityAuditorAgent`, `DatabaseMigrationAgent`).
* **Skill Naming:** Should be Action-based and highly specific, using kebab-case (e.g., `validate-jwt-tokens.md`, `format-react-components.md`, NOT `auth-stuff.md`).
* **Objective Clarity:** The stated objective must be deterministic. Eradicate vague words like "help," "manage," or "process." Replace them with concrete verbs like "extract," "validate," "transform," or "generate."

### B. Preventing Identity Confusion
* **Skill Triggers Must Be Unique:** The semantic description of a skill must be distinct. Overlapping trigger descriptions cause the Agent to load the wrong skill.
* **No "Agent-Like" Skills:** A skill must never instruct an agent to "figure out the best way" to do something. Skills must provide exact, deterministic steps. 

### C. Safe-Guarding Shared Skills
When a skill is designed to be shared across multiple different Agents, enforce these constraints:
* **Strict Statelessness:** The skill must never assume *which* agent invoked it. It cannot rely on prior conversation history that isn't explicitly passed to it.
* **Input/Output Contracts:** Every shared skill must explicitly state what data it requires to begin (Inputs) and what exact format it must return (Outputs).

### D. Eliminating Logic Errors & Reasoning Fails
* **Eradicate Circular Dependencies:** Skill A must never call Skill B if Skill B has a pathway that calls Skill A.
* **Prevent Redundancy (DRY Principle):** Skills must be atomic. Do not duplicate instructions across files.
* **Mandatory Verification Gates:** Every skill must end with a "Verification Check" so the executing Agent validates its own output against the skill's constraints.

## 3. Standard Operating Procedure (SOP)
When executing this `ai-architect` skill, follow this exact sequence:

**Step 1: The Audit & Semantic Review**
1. Evaluate the proposed or existing name. If it is ambiguous, generate 3 highly specific alternatives.
2. Review the core instructions and objectives. Identify vague language that requires the agent to guess, and rewrite it to be deterministic.
3. Scan for shared-skill dependencies that violate the "Statelessness" rule or create logic loops.

**Step 2: The Blueprinting**
1. Define the optimized Name and the exact Trigger for the target Agent/Skill.
2. Map the required Inputs (what the agent needs before starting) and Outputs (the exact format expected).
3. Establish strict "Do NOT do" constraints to build a boundary around the task.

**Step 3: Implementation & Validation**
1. Write or rewrite the Agent prompt or `SKILL.md` file using imperative, clear language.
2. Inject a definitive Verification Step at the end of the instructions.
3. Present the finalized design to the user, explicitly noting why the name was changed and which instructions were clarified to prevent reasoning failures.