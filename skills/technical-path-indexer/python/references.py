from __future__ import annotations

import re
from pathlib import Path

from .models import FileNode, ReferenceEdge, SkippedFile, UnresolvedItem
from .repository import read_text

IMPORT_PATTERNS = [
    (re.compile(r"import\s+.+?\s+from\s+[\"'`]([^\"'`]+)[\"'`]"), "import"),
    (re.compile(r"export\s+.+?\s+from\s+[\"'`]([^\"'`]+)[\"'`]"), "re-export"),
    (re.compile(r"require\(\s*[\"'`]([^\"'`]+)[\"'`]\s*\)"), "require"),
    (re.compile(r"from\s+([\w./-]+)\s+import\s+"), "python-import"),
    (re.compile(r"^import\s+([\w.]+)"), "python-import"),
    (re.compile(r"using\s+([A-Za-z0-9_.]+);"), "using"),
    (re.compile(r"\[[Ll]oad(From)?\(\s*\"([^\"]+)\"\)\]"), "attribute-path"),
]

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
PATH_LITERAL_RE = re.compile(
    r"(?P<target>(?:\.\.?[\\/]|[\\/])?[A-Za-z0-9_./\\-]+?\.(?:agent\.md|prompt\.md|instructions\.md|md|json|yaml|yml|py|ts|tsx|mjs|cjs|js|jsx|css|scss|less|html|cs|csproj|sln|xml|toml|sql|sh|ps1|go|rs|java|kt|kts|swift|rb))"
)

IMPORT_EXTENSION_CANDIDATES = {
    ".cjs": [".cjs", ".js", ".jsx", ".ts", ".tsx", ".json"],
    ".js": [".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".json"],
    ".jsx": [".jsx", ".js", ".tsx", ".ts", ".json"],
    ".mjs": [".mjs", ".js", ".jsx", ".ts", ".tsx", ".json"],
    ".ts": [".ts", ".tsx", ".js", ".jsx", ".json"],
    ".tsx": [".tsx", ".ts", ".jsx", ".js", ".json"],
    ".py": [".py"],
}


def _is_external_reference(candidate: str) -> bool:
    return candidate.startswith(("http://", "https://", "mailto:", "//"))


def _normalize_candidate(raw_value: str) -> str:
    return raw_value.replace("\\", "/").split("#", 1)[0].split("?", 1)[0].strip()


def _to_repo_relative(root: Path, candidate_path: Path) -> str | None:
    resolved = candidate_path.resolve()
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError:
        return None


def _try_existing(root: Path, source: Path, candidate: str, available_paths: set[str]) -> Path | None:
    if not candidate or _is_external_reference(candidate):
        return None

    raw_candidate = Path(candidate)
    paths_to_try: list[Path] = []
    if raw_candidate.is_absolute():
        paths_to_try.append(root / candidate.lstrip("/\\"))
    else:
        paths_to_try.append((source.parent / raw_candidate).resolve())
        paths_to_try.append((root / raw_candidate).resolve())

    for path in paths_to_try:
        relative_path = _to_repo_relative(root, path)
        if relative_path and relative_path in available_paths:
            return path
    return None


def _resolve_import_target(root: Path, source: Path, raw_value: str, available_paths: set[str]) -> Path | None:
    cleaned = _normalize_candidate(raw_value)
    if _is_external_reference(cleaned):
        return None

    direct = _try_existing(root, source, cleaned, available_paths)
    if direct is not None:
        return direct

    source_extension = source.suffix
    candidates = IMPORT_EXTENSION_CANDIDATES.get(source_extension, [".ts", ".tsx", ".js", ".jsx", ".json", ".py"])

    if cleaned.startswith(".") or "/" in cleaned:
        base_path = source.parent / cleaned
        for extension in candidates:
            for candidate in [base_path.with_suffix(extension), base_path / f"index{extension}"]:
                relative_path = _to_repo_relative(root, candidate)
                if relative_path and relative_path in available_paths:
                    return candidate.resolve()

    if source_extension == ".py" and "/" not in cleaned:
        module_path = root / Path(*cleaned.split("."))
        for candidate in [module_path.with_suffix(".py"), module_path / "__init__.py"]:
            relative_path = _to_repo_relative(root, candidate)
            if relative_path and relative_path in available_paths:
                return candidate.resolve()

    return None


def _should_report_unresolved(raw_value: str, relation: str) -> bool:
    cleaned = _normalize_candidate(raw_value)
    if _is_external_reference(cleaned):
        return False

    if relation in {"import", "re-export", "require"}:
        return cleaned.startswith((".", "/"))
    if relation == "python-import":
        return cleaned.startswith(".") or "/" in cleaned
    return False


def _append_unresolved(
    unresolved: list[UnresolvedItem],
    unresolved_seen: set[tuple[str, str, str, str]],
    *,
    source: str,
    value: str,
    reason: str,
    line: int,
    evidence: str,
) -> None:
    key = (source, "reference-scan", value, reason)
    if key in unresolved_seen:
        return
    unresolved_seen.add(key)
    unresolved.append(
        UnresolvedItem(
            source=source,
            stage="reference-scan",
            value=value,
            reason=reason,
            line=line,
            evidence=evidence,
        )
    )


def extract_references(root: str | Path, files: list[FileNode]) -> tuple[list[ReferenceEdge], list[UnresolvedItem], list[SkippedFile]]:
    root_path = Path(root).resolve()
    edges: list[ReferenceEdge] = []
    unresolved: list[UnresolvedItem] = []
    skipped_files: list[SkippedFile] = []
    seen: set[tuple[str, str, str, int | None]] = set()
    unresolved_seen: set[tuple[str, str, str, str]] = set()
    available_paths = {file_node.path for file_node in files}

    for file_node in files:
        if not file_node.is_text:
            skipped_files.append(SkippedFile(path=file_node.path, stage="reference-scan", reason="non-text-file"))
            continue

        source_path = root_path / file_node.path
        content = read_text(root_path, file_node.path)

        for line_number, line in enumerate(content.splitlines(), start=1):
            for pattern, relation in IMPORT_PATTERNS:
                match = pattern.search(line)
                if not match:
                    continue

                raw_target = match.group(match.lastindex or 1)
                resolved = _resolve_import_target(root_path, source_path, raw_target, available_paths)
                if resolved is None:
                    if _should_report_unresolved(raw_target, relation):
                        _append_unresolved(
                            unresolved,
                            unresolved_seen,
                            source=file_node.path,
                            value=_normalize_candidate(raw_target),
                            reason="local reference could not be resolved",
                            line=line_number,
                            evidence=line.strip(),
                        )
                    continue

                target = resolved.relative_to(root_path).as_posix()
                key = (file_node.path, target, relation, line_number)
                if key in seen:
                    continue
                seen.add(key)
                edges.append(
                    ReferenceEdge(
                        source=file_node.path,
                        target=target,
                        kind=relation,
                        line=line_number,
                        evidence=line.strip(),
                    )
                )

            for match in MARKDOWN_LINK_RE.finditer(line):
                raw_target = match.group(1)
                resolved = _resolve_import_target(root_path, source_path, raw_target, available_paths)
                if resolved is None:
                    if _should_report_unresolved(raw_target, "markdown-link"):
                        _append_unresolved(
                            unresolved,
                            unresolved_seen,
                            source=file_node.path,
                            value=_normalize_candidate(raw_target),
                            reason="linked repository path could not be resolved",
                            line=line_number,
                            evidence=line.strip(),
                        )
                    continue

                target = resolved.relative_to(root_path).as_posix()
                key = (file_node.path, target, "markdown-link", line_number)
                if key in seen:
                    continue
                seen.add(key)
                edges.append(
                    ReferenceEdge(
                        source=file_node.path,
                        target=target,
                        kind="markdown-link",
                        line=line_number,
                        evidence=line.strip(),
                    )
                )

            for match in PATH_LITERAL_RE.finditer(line):
                raw_target = match.group("target")
                resolved = _resolve_import_target(root_path, source_path, raw_target, available_paths)
                if resolved is None:
                    continue

                target = resolved.relative_to(root_path).as_posix()
                key = (file_node.path, target, "path-literal", line_number)
                if key in seen:
                    continue
                seen.add(key)
                edges.append(
                    ReferenceEdge(
                        source=file_node.path,
                        target=target,
                        kind="path-literal",
                        line=line_number,
                        evidence=line.strip(),
                    )
                )

    return (
        sorted(edges, key=lambda edge: (edge.source, edge.target, edge.kind, edge.line or 0)),
        unresolved,
        sorted(skipped_files, key=lambda item: (item.path, item.stage, item.reason, item.detail or "")),
    )
