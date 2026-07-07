#!/usr/bin/env python3
"""
lint-docs.py — Extended documentation/structure linter for Awesome-VibeCoder.

Complements scripts/validate-assets.py (frontmatter + placeholder checks) with:
  (a) canonical 7-section body check for agents/sdlc-*.agent.md (WARN — legacy
      standalone agents are intentionally free-form, see AGENTS.md).
  (b) skill "When to Use" / "Indicators of Done" heading check for skills/*/SKILL.md
      (WARN — pre-SDLC-convention skills are intentionally free-form).
  (c) broken internal markdown link check across docs/, root *.md, AGENTS.md,
      CONTRIBUTING.md (ERROR) — a lightweight, no-external-dependency stand-in
      for a full lychee run (lychee also checks external URLs; run it
      separately in CI/locally for that: `lychee --offline docs/ *.md`).
  (d) no absolute `file:///` paths in docs/ (ERROR).
  (e) no hardcoded machine-specific paths (`/home/<user>/`, `/Users/<user>/`,
      `C:\\Users\\<user>\\`) anywhere in the repo's markdown/py sources (ERROR)
      — this is exactly the class of bug TASK-0.1 fixed in validate-assets.py.

Errors fail the build (exit 1); warnings are informational only (exit 0).
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

WORKSPACE_DIR = Path(__file__).resolve().parent.parent

errors: list[str] = []
warnings: list[str] = []

# ---------------------------------------------------------------------------
# (a) Canonical 7-section agent bodies (sdlc-*.agent.md only)
# ---------------------------------------------------------------------------

# Universal across every sdlc-*.agent.md, including the orchestrator's own template.
AGENT_UNIVERSAL_SECTIONS = [
    "Mandatory Skill Loading",
    "Patterns, Rules & Structures",
    "Indicators of Done",
    "Boundaries",
]
# Present in every sdlc-*.agent.md except the orchestrator (a documented, special "Set up" bucket).
AGENT_STANDARD_SECTIONS = AGENT_UNIVERSAL_SECTIONS + [
    "Centralized State Architecture",
    "Core Workflow",
]


def check_agent_sections() -> None:
    agents_dir = WORKSPACE_DIR / "agents"
    if not agents_dir.exists():
        return
    for f in sorted(agents_dir.glob("sdlc-*.agent.md")):
        body = f.read_text(encoding="utf-8")
        headings = re.findall(r"^##\s+(.+?)\s*$", body, re.MULTILINE)
        required = (
            AGENT_UNIVERSAL_SECTIONS
            if f.name == "sdlc-orchestrator.agent.md"
            else AGENT_STANDARD_SECTIONS
        )
        for section in required:
            if not any(section in h for h in headings):
                warnings.append(
                    f"[agent-sections] {f.relative_to(WORKSPACE_DIR)}: missing canonical section containing '{section}'"
                )


# ---------------------------------------------------------------------------
# (b) Skill "When to Use" / "Indicators of Done" headings
# ---------------------------------------------------------------------------

SKILL_EXPECTED_HEADING_SUBSTRINGS = ["When to Use", "Indicators of Done"]


def check_skill_headings() -> None:
    skills_dir = WORKSPACE_DIR / "skills"
    if not skills_dir.exists():
        return
    for f in sorted(skills_dir.glob("*/SKILL.md")):
        body = f.read_text(encoding="utf-8")
        headings = re.findall(r"^##\s+(.+?)\s*$", body, re.MULTILINE)
        for expected in SKILL_EXPECTED_HEADING_SUBSTRINGS:
            if not any(expected in h for h in headings):
                warnings.append(
                    f"[skill-sections] {f.relative_to(WORKSPACE_DIR)}: missing heading containing '{expected}'"
                )


# ---------------------------------------------------------------------------
# (c) Broken internal markdown links
# ---------------------------------------------------------------------------

MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
LINT_ROOTS = ["docs", "AGENTS.md", "CONTRIBUTING.md", "README.md", "CHANGELOG.md"]


def _iter_markdown_files():
    for root_name in LINT_ROOTS:
        root = WORKSPACE_DIR / root_name
        if root.is_file() and root.suffix == ".md":
            yield root
        elif root.is_dir():
            yield from sorted(root.rglob("*.md"))


def check_internal_links() -> None:
    for md_file in _iter_markdown_files():
        text = md_file.read_text(encoding="utf-8")
        for match in MD_LINK_RE.finditer(text):
            target = match.group(1).strip()
            # Skip external URLs, mailto, anchors-only, and templated placeholders.
            if re.match(r"^[a-z][a-z0-9+.\-]*://", target, re.IGNORECASE):
                continue
            if target.startswith("mailto:") or target.startswith("#"):
                continue
            if "<" in target or "{" in target:
                continue
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue
            resolved = (md_file.parent / path_part).resolve()
            try:
                resolved.relative_to(WORKSPACE_DIR)
            except ValueError:
                continue  # link escapes the repo root; not ours to validate
            if not resolved.exists():
                errors.append(
                    f"[broken-link] {md_file.relative_to(WORKSPACE_DIR)}: link target does not exist: {target}"
                )


# ---------------------------------------------------------------------------
# (d) No absolute file:/// paths in docs/
# ---------------------------------------------------------------------------


def check_no_file_scheme() -> None:
    docs_dir = WORKSPACE_DIR / "docs"
    if not docs_dir.exists():
        return
    for f in sorted(docs_dir.rglob("*.md")):
        rel = str(f.relative_to(WORKSPACE_DIR))
        if rel in MACHINE_PATH_EXCLUDE_FILES:
            continue  # dated planning snapshots that quote this check's own spec, not a violation
        text = f.read_text(encoding="utf-8")
        if "file:///" in text:
            errors.append(f"[file-scheme] {rel}: contains an absolute file:/// path")


# ---------------------------------------------------------------------------
# (e) No hardcoded machine-specific paths
# ---------------------------------------------------------------------------

MACHINE_PATH_PATTERNS = [
    re.compile(r"/home/[A-Za-z0-9_.\-]+/"),
    re.compile(r"/Users/[A-Za-z0-9_.\-]+/"),
    re.compile(r"[A-Za-z]:\\\\Users\\\\[A-Za-z0-9_.\-]+\\\\"),
    re.compile(r"C:\\Users\\[A-Za-z0-9_.\-]+\\"),
]
MACHINE_PATH_SCAN_GLOBS = ["**/*.md", "**/*.py", "**/*.json", "**/*.yml", "**/*.yaml"]
# `deprecate/` is frozen legacy content (out of scope, like validate-assets.py's own
# scan); `docs/roadmap.md`/`docs/implementation-plan.md` are dated planning snapshots
# that *quote* the original TASK-0.1 bug for historical record, not a live instance of
# it; `instructions/` is pedagogical content that legitimately shows illustrative
# Windows-style example paths (a generic project folder, not a real machine/user path).
MACHINE_PATH_EXCLUDE_DIRS = {"node_modules", ".git", "__pycache__", "cookbook", "deprecate", "instructions"}
MACHINE_PATH_EXCLUDE_FILES = {"docs/roadmap.md", "docs/implementation-plan.md"}


def check_no_machine_paths() -> None:
    seen: set[Path] = set()
    for pattern in MACHINE_PATH_SCAN_GLOBS:
        for f in WORKSPACE_DIR.glob(pattern):
            if f in seen:
                continue
            if any(part in MACHINE_PATH_EXCLUDE_DIRS for part in f.parts):
                continue
            if str(f.relative_to(WORKSPACE_DIR)) in MACHINE_PATH_EXCLUDE_FILES:
                continue
            seen.add(f)
            try:
                text = f.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for pat in MACHINE_PATH_PATTERNS:
                m = pat.search(text)
                if m:
                    errors.append(
                        f"[hardcoded-path] {f.relative_to(WORKSPACE_DIR)}: contains a hardcoded machine path ({m.group(0)!r})"
                    )
                    break


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

check_agent_sections()
check_skill_headings()
check_internal_links()
check_no_file_scheme()
check_no_machine_paths()

print("--- Docs Lint Results ---")
print(f"Total Errors found: {len(errors)}")
print(f"Total Warnings found: {len(warnings)}")

if warnings:
    print("\nWARNINGS (informational — do not fail the build):")
    for w in warnings:
        print(f"  [WARN] {w}")

if errors:
    print("\nERRORS:")
    for e in errors:
        print(f"  [ERROR] {e}")
    sys.exit(1)
else:
    print("\nAll hard-gated doc checks passed! ✅")
    sys.exit(0)
