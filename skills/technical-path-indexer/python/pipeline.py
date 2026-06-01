from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .linked_files import detect_linked_files
from .models import FileNode, SkippedFile
from .references import extract_references
from .repository import build_directory_index, discover_files, filter_files
from .routes import extract_routes


def _normalize_scope(scope_paths: list[str] | None) -> list[str]:
    if not scope_paths:
        return []
    return [Path(scope_path).as_posix().strip().strip("/") for scope_path in scope_paths if scope_path.strip()]


def _build_batches(file_paths: list[str], batch_size: int | None = None) -> list[dict[str, object]]:
    groups: dict[str, list[str]] = {}
    for file_path in sorted(file_paths):
        parts = Path(file_path).parts
        group_name = parts[0] if len(parts) > 1 else "."
        groups.setdefault(group_name, []).append(file_path)

    batches: list[dict[str, object]] = []
    batch_index = 1
    for group_name in sorted(groups):
        group_files = groups[group_name]
        if batch_size and batch_size > 0:
            for offset in range(0, len(group_files), batch_size):
                chunk = group_files[offset : offset + batch_size]
                batches.append(
                    {
                        "index": batch_index,
                        "path": group_name,
                        "file_count": len(chunk),
                    }
                )
                batch_index += 1
        else:
            batches.append(
                {
                    "index": batch_index,
                    "path": group_name,
                    "file_count": len(group_files),
                }
            )
            batch_index += 1


    return batches


def _serialize_files(files: list[FileNode]) -> list[dict[str, object]]:
    return [
        {
            "file": file_node.path,
            "language": file_node.language,
            "size": file_node.size,
        }
        for file_node in files
    ]


def _serialize_skipped_files(skipped_files: list[SkippedFile]) -> list[str]:
    ignored_reasons = {"framework-support-file", "unsupported-text-format"}
    return sorted({item.path for item in skipped_files if item.reason not in ignored_reasons})


def build_index(
    root: str | Path,
    scope_paths: list[str] | None = None,
    batch_size: int | None = None,
    compact: bool = False,
) -> dict[str, object]:
    root_path = Path(root).resolve()
    normalized_scope = _normalize_scope(scope_paths)
    files = filter_files(discover_files(root_path), normalized_scope)
    directories = build_directory_index(files)
    routes, _route_unresolved, route_skipped = extract_routes(root_path, files)
    references, _reference_unresolved, reference_skipped = extract_references(root_path, files)
    linked_files = detect_linked_files(files)
    skipped_files = route_skipped + reference_skipped
    batches = _build_batches([file_node.path for file_node in files], batch_size)
    serialized_files = _serialize_files(files)
    serialized_skipped_files = _serialize_skipped_files(skipped_files)

    return {
        "root": str(root_path),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "mode": "scoped-scan" if normalized_scope else "full-scan",
            "paths": normalized_scope,
            "batch_size": batch_size,
            "compact": compact,
        },
        "batches": batches,
        "files": serialized_files,
        "directories": [directory.to_dict() for directory in directories],
        "routes": [route.to_dict() for route in routes],
        "linked_files": [edge.to_dict() for edge in linked_files],
        "skipped_files": serialized_skipped_files,
        "summary": {
            "file_count": len(files),
            "directory_count": len(directories),
            "route_count": len(routes),
            "linked_file_count": len(linked_files),
            "batch_count": len(batches),
            "skipped_file_count": len(serialized_skipped_files),
        },
    }