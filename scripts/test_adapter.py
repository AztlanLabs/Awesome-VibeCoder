#!/usr/bin/env python3
"""
test_adapter.py — Self-tests for scripts/agent-frontmatter-adapter.py

Covers:
  - slug_from_name
  - detect_bucket (implementation / research / review / orchestrator)
  - detect_mode (primary / all / subagent)
  - default_skills_for (sdlc-shared-memory base, role skill, extras, dedup)
  - three-bucket presets (CLAUDE_TOOLS_*, OPENCODE_PERM_*, CLAUDE_PERMISSIONMODE)
  - --backport-superset round-trip (frontmatter gains mode/model/toolsClaude/permissionMode/skills)
  - end-to-end --stdout against a known repo agent (sdlc-orchestrator.agent.md)

Run:
  python3 scripts/test_adapter.py
or
  python3 -m pytest scripts/test_adapter.py
"""
from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
ADAPTER_PATH = SCRIPTS_DIR / "agent-frontmatter-adapter.py"


def _load_adapter():
    """Load the adapter module by path so tests don't depend on a package install."""
    spec = importlib.util.spec_from_file_location("agent_frontmatter_adapter", ADAPTER_PATH)
    assert spec and spec.loader, "could not build spec for adapter"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


class TestSlugFromName(unittest.TestCase):
    def setUp(self):
        self.mod = _load_adapter()

    def test_sdlc_prefix_preserved(self):
        self.assertEqual(self.mod.slug_from_name("SDLC Orchestrator"), "sdlc-orchestrator")

    def test_spaces_become_dashes(self):
        self.assertEqual(self.mod.slug_from_name("Beast Mode Coder"), "beast-mode-coder")

    def test_special_chars_collapsed(self):
        self.assertEqual(self.mod.slug_from_name("Repo / Path Auditor!"), "repo-path-auditor")

    def test_sdlc_colon_prefix(self):
        self.assertEqual(self.mod.slug_from_name("sdlc: Software Architect"), "sdlc-software-architect")


class TestDetectBucket(unittest.TestCase):
    def setUp(self):
        self.mod = _load_adapter()

    def test_orchestrator_is_research(self):
        self.assertEqual(self.mod.detect_bucket("sdlc-orchestrator", "orchestrate the pipeline"), "research")

    def test_implementation_keywords(self):
        self.assertEqual(self.mod.detect_bucket("sdlc-developer", "implement the feature"), "implementation")
        self.assertEqual(self.mod.detect_bucket("sdlc-backend-engineer", "design the API"), "implementation")

    def test_review_keywords(self):
        self.assertEqual(self.mod.detect_bucket("agent-governance-reviewer", "governance review"), "review")
        self.assertEqual(self.mod.detect_bucket("repository-path-auditor", "audit repo structure"), "review")

    def test_research_fallback_for_design_research(self):
        self.assertEqual(self.mod.detect_bucket("sdlc-software-architect", "design the architecture"), "research")
        self.assertEqual(self.mod.detect_bucket("sdlc-product-manager", "research user needs"), "research")

    def test_default_is_implementation(self):
        self.assertEqual(self.mod.detect_bucket("some-random-agent", "does something unspecified"), "implementation")


class TestDetectMode(unittest.TestCase):
    def setUp(self):
        self.mod = _load_adapter()

    def test_orchestrator_primary(self):
        self.assertEqual(self.mod.detect_mode("sdlc-orchestrator"), "primary")

    def test_autonomous_all(self):
        self.assertEqual(self.mod.detect_mode("beast"), "all")
        self.assertEqual(self.mod.detect_mode("coderbeast"), "all")
        self.assertEqual(self.mod.detect_mode("expertcoder"), "all")
        self.assertEqual(self.mod.detect_mode("gpt-5-beast-mode"), "all")

    def test_default_subagent(self):
        self.assertEqual(self.mod.detect_mode("sdlc-developer"), "subagent")
        self.assertEqual(self.mod.detect_mode("sdlc-qa-tester"), "subagent")


class TestDefaultSkillsFor(unittest.TestCase):
    def setUp(self):
        self.mod = _load_adapter()

    def test_base_skill_always_present(self):
        self.assertIn("sdlc-shared-memory", self.mod.default_skills_for("sdlc-developer", None))

    def test_role_skill_appended_for_sdlc(self):
        skills = self.mod.default_skills_for("sdlc-backend-engineer", None)
        self.assertIn("sdlc-backend-engineer", skills)

    def test_frontend_extras(self):
        skills = self.mod.default_skills_for("sdlc-frontend-engineer", None)
        self.assertIn("web-accessibility-audit", skills)
        self.assertIn("web-performance-budget", skills)

    def test_ux_ui_designer_extra(self):
        skills = self.mod.default_skills_for("sdlc-ux-ui-designer", None)
        self.assertIn("web-design-system", skills)

    def test_responsible_ai_extra(self):
        skills = self.mod.default_skills_for("sdlc-responsible-ai", None)
        self.assertIn("web-accessibility-audit", skills)

    def test_web_engineers_map_to_named_skill(self):
        self.assertIn("web-design-system", self.mod.default_skills_for("web-design-system-engineer", None))
        self.assertIn("web-performance-budget", self.mod.default_skills_for("web-performance-engineer", None))

    def test_extra_skills_added_and_deduped(self):
        skills = self.mod.default_skills_for("sdlc-developer", ["sdlc-shared-memory", "context-map"])
        # dedup: sdlc-shared-memory should appear once
        self.assertEqual(skills.count("sdlc-shared-memory"), 1)
        self.assertIn("context-map", skills)


class TestBucketPresets(unittest.TestCase):
    def setUp(self):
        self.mod = _load_adapter()

    def test_claude_tools_distinct(self):
        self.assertEqual(set(self.mod.CLAUDE_TOOLS_REVIEW) & {"Edit", "Write"}, set())
        self.assertIn("Edit", self.mod.CLAUDE_TOOLS_IMPL)
        self.assertIn("Edit", self.mod.CLAUDE_TOOLS_RESEARCH)

    def test_opencode_permissions(self):
        self.assertEqual(self.mod.OPENCODE_PERM_IMPL["edit"], "allow")
        self.assertEqual(self.mod.OPENCODE_PERM_REVIEW["edit"], "deny")
        # research has scoped edit (dict, not a plain string)
        self.assertIsInstance(self.mod.OPENCODE_PERM_RESEARCH["edit"], dict)
        self.assertEqual(self.mod.OPENCODE_PERM_RESEARCH["edit"]["*"], "deny")

    def test_claude_permission_mode_map(self):
        self.assertEqual(self.mod.CLAUDE_PERMISSIONMODE["implementation"], "acceptEdits")
        self.assertEqual(self.mod.CLAUDE_PERMISSIONMODE["research"], "default")
        self.assertEqual(self.mod.CLAUDE_PERMISSIONMODE["review"], "plan")


class TestBackportSuperset(unittest.TestCase):
    def setUp(self):
        self.mod = _load_adapter()

    def test_superset_adds_expected_keys(self):
        fm = {"name": "SDLC Developer", "description": "implement the feature", "tools": ["vscode", "execute"]}
        out = self.mod.backport_superset(fm, "sdlc-developer", "implementation",
                                         self.mod.default_skills_for("sdlc-developer", None), "subagent")
        for key in ("mode", "model", "toolsClaude", "permissionMode", "skills"):
            self.assertIn(key, out, f"superset frontmatter missing {key}")
        self.assertEqual(out["mode"], "subagent")
        self.assertEqual(out["model"], "inherit")
        self.assertEqual(out["permissionMode"], "acceptEdits")
        self.assertIn("sdlc-shared-memory", out["skills"])

    def test_review_bucket_permissions(self):
        fm = {"name": "Agent Governance Reviewer", "description": "governance review"}
        out = self.mod.backport_superset(fm, "agent-governance-reviewer", "review",
                                         self.mod.default_skills_for("agent-governance-reviewer", None), "subagent")
        self.assertEqual(out["permissionMode"], "plan")
        self.assertEqual(out["toolsClaude"], self.mod.CLAUDE_TOOLS_REVIEW)

    def test_round_trip_preserves_body(self):
        """backport-superset should only rewrite frontmatter; body must pass through unchanged."""
        sample = (
            "---\n"
            "name: SDLC Developer\n"
            "description: implement the feature\n"
            "tools: [vscode, execute, read]\n"
            "---\n\n"
            "# SDLC Developer\n\nThis is the body. It must survive round-trip.\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "sdlc-developer.agent.md"
            src.write_text(sample, encoding="utf-8")
            fm, body = self.mod.parse_frontmatter(sample)
            slug = self.mod.slug_from_name(str(fm.get("name")))
            bucket = self.mod.detect_bucket(slug, str(fm.get("description")))
            mode = self.mod.detect_mode(slug)
            skills = self.mod.default_skills_for(slug, None)
            new_fm = self.mod.backport_superset(fm, slug, bucket, skills, mode)
            order = ["name", "description", "tools", "mode", "model", "toolsClaude", "permissionMode", "skills"]
            head = self.mod.render_frontmatter(new_fm, order)
            new_text = head + body
            # body content preserved
            self.assertIn("# SDLC Developer", new_text)
            self.assertIn("It must survive round-trip.", new_text)
            # frontmatter gained superset keys
            self.assertIn("mode:", new_text)
            self.assertIn("toolsClaude:", new_text)


class TestEndToEndStdout(unittest.TestCase):
    """Run the adapter CLI with --stdout against a real repo agent and assert it succeeds."""

    def test_orchestrator_stdout(self):
        import subprocess
        agent = REPO_ROOT / "agents" / "sdlc-orchestrator.agent.md"
        if not agent.exists():
            self.skipTest("sdlc-orchestrator.agent.md not found")
        result = subprocess.run(
            [sys.executable, str(ADAPTER_PATH), "--src", str(agent), "--claude", ".claude/agents/sdlc-orchestrator.md", "--stdout"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, f"adapter failed: {result.stderr}")
        self.assertIn("===== CLAUDE:", result.stdout)
        self.assertIn("name: sdlc-orchestrator", result.stdout)

    def test_all_agents_stdout(self):
        """Every agents/*.agent.md should adapt without error."""
        import subprocess
        agents_dir = REPO_ROOT / "agents"
        if not agents_dir.is_dir():
            self.skipTest("agents/ directory not found")
        agents = sorted(agents_dir.glob("*.agent.md"))
        self.assertGreater(len(agents), 0, "no agent files found")
        for agent in agents:
            with self.subTest(agent=agent.name):
                result = subprocess.run(
                    [sys.executable, str(ADAPTER_PATH), "--src", str(agent),
                     "--claude", f".claude/agents/{agent.stem}.md", "--stdout"],
                    capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 0, f"{agent.name}: {result.stderr}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
