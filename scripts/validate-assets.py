import os
import re
import yaml
import sys

workspace_dir = "/home/crowne/Documents/Documents/VS Code/Awesome-VibeCoder"

errors = []
warnings = []

def parse_frontmatter(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Match frontmatter block at start of file
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if not match:
        return None, content
    
    fm_str = match.group(1)
    body = match.group(2)
    try:
        data = yaml.safe_load(fm_str)
        return data, body
    except Exception as e:
        errors.append(f"Invalid YAML frontmatter in {file_path}: {e}")
        return None, body

def check_legacy_placeholders(file_path, body):
    # Strip fenced code blocks
    cleaned_body = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    # Strip inline code blocks
    cleaned_body = re.sub(r"`.*?`", "", cleaned_body)
    if "{{" in cleaned_body or "}}" in cleaned_body:
        errors.append(f"Legacy double curly brace placeholder found in {file_path}")

def validate_agent(file_path):
    fm, body = parse_frontmatter(file_path)
    if fm is None:
        if not any(e.startswith(f"Invalid YAML frontmatter in {file_path}") for e in errors):
            errors.append(f"Missing frontmatter block in {file_path}")
        return
    
    # Verify required description field
    if "description" not in fm or not fm["description"]:
        errors.append(f"Agent profile {file_path} is missing required 'description' field.")
    
    # Check length threshold
    if len(body) > 30000:
        warnings.append(f"Agent prompt in {file_path} exceeds 30,000 characters (length: {len(body)})")
        
    check_legacy_placeholders(file_path, body)

def validate_skill(file_path):
    fm, body = parse_frontmatter(file_path)
    check_legacy_placeholders(file_path, body)

def validate_instructions(file_path):
    fm, body = parse_frontmatter(file_path)
    check_legacy_placeholders(file_path, body)

# 1. Validate Agents
agents_dir = os.path.join(workspace_dir, "agents")
if os.path.exists(agents_dir):
    for f in os.listdir(agents_dir):
        if f.endswith(".agent.md"):
            validate_agent(os.path.join(agents_dir, f))

# 2. Validate Skills
skills_dir = os.path.join(workspace_dir, "skills")
if os.path.exists(skills_dir):
    for root, dirs, files in os.walk(skills_dir):
        for f in files:
            if f == "SKILL.md":
                validate_skill(os.path.join(root, f))

# 3. Validate Instructions
inst_dir = os.path.join(workspace_dir, "instructions")
if os.path.exists(inst_dir):
    for f in os.listdir(inst_dir):
        if f.endswith(".instructions.md") or f.endswith(".instructions"):
            validate_instructions(os.path.join(inst_dir, f))

# 4. Check Mirror Parity
github_skills_dir = os.path.join(workspace_dir, ".github", "skills")
if os.path.exists(github_skills_dir):
    for skill_name in os.listdir(github_skills_dir):
        github_skill_path = os.path.join(github_skills_dir, skill_name, "SKILL.md")
        if os.path.exists(github_skill_path):
            root_skill_path = os.path.join(skills_dir, skill_name, "SKILL.md")
            if not os.path.exists(root_skill_path):
                errors.append(f"Mirrored skill {github_skill_path} does not exist at root skills directory {root_skill_path}")
            else:
                with open(github_skill_path, "r", encoding="utf-8") as f1, open(root_skill_path, "r", encoding="utf-8") as f2:
                    c1 = f1.read()
                    c2 = f2.read()
                if c1 != c2:
                    errors.append(f"Parity mismatch between mirrored {github_skill_path} and root {root_skill_path}")

print(f"--- Prompt & Agent Validation Results ---")
print(f"Total Errors found: {len(errors)}")
print(f"Total Warnings found: {len(warnings)}")

if warnings:
    print("\nWARNINGS:")
    for w in warnings:
        print(f"  [WARN] {w}")

if errors:
    print("\nERRORS:")
    for e in errors:
        print(f"  [ERROR] {e}")
    sys.exit(1)
else:
    print("\nAll active assets passed validation successfully! ✅")
    sys.exit(0)
