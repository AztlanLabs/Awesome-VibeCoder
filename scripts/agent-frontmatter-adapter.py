#!/usr/bin/env python3
"""
agent-frontmatter-adapter.py — Convert a repo agents/<name>.agent.md to the
frontmatter shape required by another host (Claude Code, opencode, Cursor),
or backport a portable 'superset' frontmatter into the source file.

Idempotent. Only rewrites the frontmatter; the agent's markdown BODY is
passed through unchanged to every target.

Source conventions:
  - Repo agents declare (name, description, tools:[vscode, execute, read, ...]).
  - Repo skills declare (name, description) and are already cross-host portable.

Targets:
  --claude   <path>   .claude/agents/<name>.md   (YAML frontmatter + body)
  --opencode <path>   .opencode/agent/<name>.md  (YAML frontmatter + body)
  --cursor   <path>   .cursor/rules/<name>.mdc   (YAML frontmatter + body)

Options:
  --src <path>             (required) repo agent source
  --bucket implementation|research|review   tool/permission preset (auto from description if omitted)
  --skills a,b,c           extra skills to preload (Claude target; auto-defaults to sdlc-shared-memory + matching role skill)
  --mcp playwright         inline mcpServers entry (Claude target)
  --globs "**/*.tsx"       glob(s) for Cursor target (else alwaysApply: true)
  --mode primary|subagent|all  override auto mode (auto: orchestrator=primary, autonomous coders=all, else subagent)
  --backport-superset      rewrite the SOURCE file's frontmatter with the superset (Rule 1); off by default
  --stdout                 print each target's content instead of writing
  --list-buckets           print the bucket presets and exit

See: docs/integrations/compatibility.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n(.*)$", re.S)

CLAUDE_TOOLS_IMPL = ["Read", "Edit", "Write", "Bash", "Grep", "Glob", "WebFetch", "WebSearch", "Skill", "Agent"]
CLAUDE_TOOLS_RESEARCH = ["Read", "Edit", "Bash", "Grep", "Glob", "WebFetch", "Skill", "Agent"]
CLAUDE_TOOLS_REVIEW = ["Read", "Grep", "Glob", "WebFetch", "WebSearch", "Skill", "Agent"]

OPENCODE_PERM_IMPL = {"edit": "allow", "bash": "ask", "task": "allow"}
OPENCODE_PERM_RESEARCH = {
    "edit": {"*": "deny", ".sdlc/**": "allow", "docs/**": "allow", ".github/**": "allow"},
    "bash": "ask",
    "task": "allow",
}
OPENCODE_PERM_REVIEW = {"edit": "deny", "bash": "ask", "task": "allow"}

CLAUDE_PERMISSIONMODE = {
    "implementation": "acceptEdits",
    "research": "default",
    "review": "plan",
}

AUTONOMOUS_KEYWORDS = ("beast", "coderbeast", "expertcoder", "gpt-5-beast", "planning-agent", "promptfileauthor", "expert-react", "modernization", "refine-issue", "context-researcher", "repository-path", "governance", "electron-angular", "scientific-paper", "search-ai", "simple-app", "idea-generator")
IMPL_KEYWORDS = ("developer", "backend", "frontend", "fullstack", "db-developer", "cybersecurity-developer", "qa-tester", "devops", "technical-writer", "web-design-system", "web-performance", "beast", "coderbeast", "expertcoder", "gpt-5-beast", "expert-react", "promptfileauthor")
REVIEW_KEYWORDS = ("governance-reviewer", "electron-angular", "scientific-paper", "search-ai-optimization", "simple-app-idea", "repository-path-auditor")


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise SystemExit("error: source has no YAML frontmatter delimited by '---'")
    raw_fm, body = m.group(1), m.group(2)
    fm: dict[str, Any] = {}
    for line in raw_fm.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
            val = val[1:-1]
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1]
            val = [x.strip().strip("'\"") for x in inner.split(",") if x.strip()]
        fm[key] = val
    return fm, body


def slug_from_name(name: str) -> str:
    s = name.lower()
    s = re.sub(r"^sdlc:\s*", "sdlc-", s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def detect_bucket(slug: str, description: str) -> str:
    text = f"{slug} {description}".lower()
    if slug == "sdlc-orchestrator":
        return "research"
    if any(k in slug.lower() for k in REVIEW_KEYWORDS):
        return "review"
    if any(k in slug.lower() for k in IMPL_KEYWORDS):
        return "implementation"
    if "implement" in text or "code" in text or "develop" in text:
        return "implementation"
    if "design" in text or "research" in text or "plan" in text or "review" in text or "audit" in text:
        return "research"
    return "implementation"


def detect_mode(slug: str) -> str:
    if slug == "sdlc-orchestrator":
        return "primary"
    if any(k in slug for k in AUTONOMOUS_KEYWORDS):
        return "all"
    return "subagent"


def default_skills_for(slug: str, extra: list[str] | None) -> list[str]:
    skills = ["sdlc-shared-memory"]
    role_skill = slug if slug.startswith("sdlc-") else None
    if slug in {"web-design-system-engineer", "web-performance-engineer"}:
        role_skill = {"web-design-system-engineer": "web-design-system", "web-performance-engineer": "web-performance-budget"}[slug]
    if role_skill:
        skills.append(role_skill)
    if slug == "sdlc-frontend-engineer":
        skills += ["web-accessibility-audit", "web-performance-budget"]
    if slug == "sdlc-ux-ui-designer":
        skills += ["web-design-system"]
    if slug == "sdlc-responsible-ai":
        skills += ["web-accessibility-audit"]
    if extra:
        for s in extra:
            if s not in skills:
                skills.append(s)
    return skills


def yaml_value(v: Any) -> str:
    if isinstance(v, list):
        return "[" + ", ".join(yaml_value(x) for x in v) + "]"
    if isinstance(v, dict):
        items = []
        for k, vv in v.items():
            if isinstance(vv, dict):
                inner = ", ".join(f"{kk}: {yaml_value(vv[kk])}" for kk in vv)
                items.append(f"{k}: {{{inner}}}")
            else:
                items.append(f"{k}: {yaml_value(vv)}")
        return "{" + ", ".join(items) + "}"
    if isinstance(v, str) and (":" in v or "{" in v or "[" in v or "'" in v):
        return '"' + v.replace('"', '\\"') + '"'
    return str(v)


def render_frontmatter(fm: dict[str, Any], order: list[str]) -> str:
    lines = ["---"]
    for key in order:
        if key in fm:
            lines.append(f"{key}: {yaml_value(fm[key])}")
    for key, val in fm.items():
        if key in order:
            continue
        lines.append(f"{key}: {yaml_value(val)}")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def make_claude(fm: dict[str, Any], body: str, slug: str, bucket: str, skills: list[str], mcp: str | None, mode: str) -> str:
    out: dict[str, Any] = {
        "name": slug,
        "description": fm.get("description", ""),
        "model": fm.get("model", "inherit"),
    }
    if bucket == "implementation":
        out["tools"] = CLAUDE_TOOLS_IMPL
        out["permissionMode"] = "acceptEdits"
    elif bucket == "research":
        out["tools"] = CLAUDE_TOOLS_RESEARCH
        out["permissionMode"] = "default"
    else:
        out["tools"] = CLAUDE_TOOLS_REVIEW
        out["permissionMode"] = "plan"
    out["skills"] = skills
    if mcp == "playwright":
        out["mcpServers"] = [{"playwright": {"type": "stdio", "command": "npx",
                                             "args": ["-y", "@playwright/mcp@latest"]}}]
    out["# body"] = "repo agent file follows"
    order = ["name", "description", "model", "tools", "permissionMode", "skills", "mcpServers", "# body"]
    fm_clean = {k: v for k, v in out.items() if k != "# body"}
    head = render_frontmatter(fm_clean, order)
    pointer = f"\nRead `agents/{slug}.agent.md` and follow it exactly as your operating manual. The repo file overrides any contradiction in this default prompt.\n"
    return head + body if body.startswith("\n") else head + "\n" + pointer.strip() + "\n\n" + body.lstrip("\n")


def make_opencode(fm: dict[str, Any], body: str, slug: str, bucket: str, mode: str) -> str:
    if bucket == "implementation":
        perm = OPENCODE_PERM_IMPL
    elif bucket == "research":
        perm = OPENCODE_PERM_RESEARCH
    else:
        perm = OPENCODE_PERM_REVIEW
    out: dict[str, Any] = {
        "mode": mode,
        "description": fm.get("description", ""),
        "permission": perm,
    }
    order = ["mode", "description", "permission"]
    head = render_frontmatter(out, order)
    return head + body


def make_cursor(fm: dict[str, Any], body: str, slug: str, globs: list[str] | None) -> str:
    out: dict[str, Any] = {
        "description": fm.get("description", ""),
    }
    if globs:
        out["globs"] = globs
        out["alwaysApply"] = False
    else:
        out["alwaysApply"] = True
    order = ["description", "globs", "alwaysApply"]
    head = render_frontmatter(out, order)
    pointer = (f"\nRead `agents/{slug}.agent.md` and follow it as your operating manual; load the matching skills on demand.\n\n")
    return head + body if body.startswith("\n") else head + pointer + body.lstrip("\n")


def backport_superset(fm: dict[str, Any], slug: str, bucket: str, skills: list[str], mode: str) -> dict[str, Any]:
    out = dict(fm)
    out["mode"] = mode
    out["model"] = "inherit"
    if bucket == "implementation":
        out["toolsClaude"] = CLAUDE_TOOLS_IMPL
        cl_perm = "acceptEdits"
    elif bucket == "research":
        out["toolsClaude"] = CLAUDE_TOOLS_RESEARCH
        cl_perm = "default"
    else:
        out["toolsClaude"] = CLAUDE_TOOLS_REVIEW
        cl_perm = "plan"
    out["permissionMode"] = cl_perm
    out["skills"] = skills
    return out


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Adapt a repo .agent.md to another host's frontmatter.")
    p.add_argument("--src", help="repo agent source path (required unless --list-buckets)")
    p.add_argument("--claude", help="emit Claude .claude/agents/*.md at this path")
    p.add_argument("--opencode", help="emit opencode .opencode/agent/*.md at this path")
    p.add_argument("--cursor", help="emit Cursor .cursor/rules/*.mdc at this path")
    p.add_argument("--bucket", choices=["implementation", "research", "review"], help="tool/permission preset (auto-detected if omitted)")
    p.add_argument("--skills", help="comma-separated extra skills to preload (Claude target)")
    p.add_argument("--mcp", help="inline mcpServers entry for Claude (e.g. playwright)")
    p.add_argument("--globs", help="comma-separated globs for Cursor target (else alwaysApply: true)")
    p.add_argument("--mode", choices=["primary", "subagent", "all"], help="override auto mode")
    p.add_argument("--backport-superset", action="store_true", help="rewrite the SOURCE file's frontmatter in-place with the superset")
    p.add_argument("--stdout", action="store_true", help="print target contents instead of writing")
    p.add_argument("--list-buckets", action="store_true", help="print preset tables and exit")
    args = p.parse_args(argv)

    if args.list_buckets:
        print(json.dumps({
            "implementation": {"claude_tools": CLAUDE_TOOLS_IMPL, "claude_permissionMode": "acceptEdits",
                                "opencode_permission": OPENCODE_PERM_IMPL},
            "research": {"claude_tools": CLAUDE_TOOLS_RESEARCH, "claude_permissionMode": "default",
                         "opencode_permission": OPENCODE_PERM_RESEARCH},
            "review": {"claude_tools": CLAUDE_TOOLS_REVIEW, "claude_permissionMode": "plan",
                      "opencode_permission": OPENCODE_PERM_REVIEW},
        }, indent=2))
        return 0

    src = Path(args.src) if args.src else None
    if src is None:
        print("error: --src is required", file=sys.stderr)
        return 2
    if not src.exists():
        print(f"error: source not found: {src}", file=sys.stderr)
        return 2
    text = src.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    name = str(fm.get("name", src.stem))
    slug = slug_from_name(name)
    description = str(fm.get("description", ""))
    bucket = args.bucket or detect_bucket(slug, description)
    mode = args.mode or detect_mode(slug)
    extra_skills = [s.strip() for s in args.skills.split(",")] if args.skills else []
    skills = default_skills_for(slug, extra_skills)
    globs = [g.strip() for g in args.globs.split(",")] if args.globs else None

    if args.backport_superset:
        new_fm = backport_superset(fm, slug, bucket, skills, mode)
        order = ["name", "description", "tools", "mode", "model", "toolsClaude", "permissionMode", "skills"]
        head = render_frontmatter(new_fm, order)
        new_text = head + body
        if args.stdout:
            print(new_text)
        else:
            src.write_text(new_text, encoding="utf-8")
            print(f"backported superset into {src}")
        return 0

    produced = False
    if args.claude:
        out = make_claude(fm, body, slug, bucket, skills, args.mcp, mode)
        if args.stdout:
            print(f"===== CLAUDE: {args.claude} ====="); print(out)
        else:
            Path(args.claude).parent.mkdir(parents=True, exist_ok=True)
            Path(args.claude).write_text(out, encoding="utf-8")
            print(f"wrote {args.claude}")
        produced = True
    if args.opencode:
        out = make_opencode(fm, body, slug, bucket, mode)
        if args.stdout:
            print(f"===== OPENCODE: {args.opencode} ====="); print(out)
        else:
            Path(args.opencode).parent.mkdir(parents=True, exist_ok=True)
            Path(args.opencode).write_text(out, encoding="utf-8")
            print(f"wrote {args.opencode}")
        produced = True
    if args.cursor:
        out = make_cursor(fm, body, slug, globs)
        if args.stdout:
            print(f"===== CURSOR: {args.cursor} ====="); print(out)
        else:
            Path(args.cursor).parent.mkdir(parents=True, exist_ok=True)
            Path(args.cursor).write_text(out, encoding="utf-8")
            print(f"wrote {args.cursor}")
        produced = True

    if not produced:
        print("warning: no --claude/--opencode/--cursor/--backport-superset target given; nothing to do.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))