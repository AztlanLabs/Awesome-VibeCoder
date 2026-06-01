from __future__ import annotations

import re
from pathlib import Path

from .models import FileNode, RouteNode, SkippedFile, UnresolvedItem
from .repository import read_text

ROUTE_PATTERNS = [
    (re.compile(r"\.(get|post|put|patch|delete|options|head|use)\(\s*[\"'`]([^\"'`]+)[\"'`]"), "http"),
    (re.compile(r"@(app|router)\.(get|post|put|patch|delete|route)\(\s*[\"']([^\"']+)[\"']"), "http"),
    (re.compile(r"\bpath\(\s*[\"']([^\"']+)[\"']"), "http"),
    (re.compile(r"\[(HttpGet|HttpPost|HttpPut|HttpPatch|HttpDelete|Route)\(\s*\"([^\"]*)\"\)\]"), "http"),
    (re.compile(r"<Route[^>]+path=\"([^\"]+)\""), "http"),
    (re.compile(r"\bpath\s*:\s*[\"']([^\"']+)[\"']"), "http"),
    (re.compile(r"add_parser\(\s*[\"']([^\"']+)[\"']"), "cli"),
    (re.compile(r"@click\.command\(name\s*=\s*[\"']([^\"']+)[\"']"), "cli"),
]

FILESYSTEM_ROUTE_MARKERS = {"app", "pages", "routes", "api"}
ROUTE_SCAN_EXTENSIONS = {".aspx", ".cs", ".html", ".js", ".jsx", ".mdx", ".py", ".razor", ".svelte", ".ts", ".tsx"}
NEXT_APP_ROUTE_FILES = {"page", "route"}
NEXT_APP_SUPPORT_FILES = {"default", "error", "global-error", "layout", "loading", "not-found", "template"}
NEXT_PAGES_SUPPORT_FILES = {"_app", "_document", "404", "500"}
SVELTEKIT_ROUTE_FILES = {"+page", "+page.server", "+server"}
SVELTEKIT_SUPPORT_FILES = {"+error", "+layout", "+layout.server"}


def _normalize_route_segments(segments: list[str]) -> str:
    normalized: list[str] = []
    for segment in segments:
        if segment in {"", "index"}:
            continue
        if segment.startswith("[[...") and segment.endswith("]]"):
            normalized.append(f"*{segment[5:-2]}?")
        elif segment.startswith("[...") and segment.endswith("]"):
            normalized.append(f"*{segment[4:-1]}")
        elif segment.startswith("[") and segment.endswith("]"):
            normalized.append(f":{segment[1:-1]}")
        else:
            normalized.append(segment)

    return "/" + "/".join(normalized) if normalized else "/"


def _next_app_route(file_node: FileNode) -> tuple[RouteNode | None, SkippedFile | None]:
    path = Path(file_node.path)
    parts = path.parts
    if "app" not in parts:
        return None, None

    app_index = parts.index("app")
    if app_index == len(parts) - 1:
        return None, None

    stem = path.name.split(".", 1)[0]
    if stem in NEXT_APP_SUPPORT_FILES:
        return None, SkippedFile(path=file_node.path, stage="route-scan", reason="framework-support-file", detail="nextjs-app")
    if stem not in NEXT_APP_ROUTE_FILES:
        return None, None

    route_segments = list(parts[app_index + 1 : -1])
    route = _normalize_route_segments(route_segments)
    return (
        RouteNode(
            source=file_node.path,
            route=route,
            kind="filesystem-nextjs-app",
            evidence="nextjs app router convention",
        ),
        None,
    )


def _next_pages_route(file_node: FileNode) -> tuple[RouteNode | None, SkippedFile | None]:
    path = Path(file_node.path)
    parts = path.parts
    if "pages" not in parts:
        return None, None

    pages_index = parts.index("pages")
    if pages_index == len(parts) - 1:
        return None, None

    stem = path.stem
    if stem in NEXT_PAGES_SUPPORT_FILES:
        return None, SkippedFile(path=file_node.path, stage="route-scan", reason="framework-support-file", detail="nextjs-pages")

    route_segments = list(parts[pages_index + 1 : -1])
    if stem != "index":
        route_segments.append(stem)

    route = _normalize_route_segments(route_segments)
    return (
        RouteNode(
            source=file_node.path,
            route=route,
            kind="filesystem-nextjs-pages",
            evidence="nextjs pages router convention",
        ),
        None,
    )


def _sveltekit_route(file_node: FileNode) -> tuple[RouteNode | None, SkippedFile | None]:
    path = Path(file_node.path)
    parts = path.parts
    marker = ("src", "routes")
    marker_index = None
    for index in range(len(parts) - 1):
        if tuple(parts[index : index + 2]) == marker:
            marker_index = index + 1
            break

    if marker_index is None:
        return None, None

    stem = path.name
    for suffix in path.suffixes:
        stem = stem.removesuffix(suffix)
    if stem in SVELTEKIT_SUPPORT_FILES:
        return None, SkippedFile(path=file_node.path, stage="route-scan", reason="framework-support-file", detail="sveltekit")
    if stem not in SVELTEKIT_ROUTE_FILES:
        return None, None

    route_segments = list(parts[marker_index + 1 : -1])
    route = _normalize_route_segments(route_segments)
    return (
        RouteNode(
            source=file_node.path,
            route=route,
            kind="filesystem-sveltekit",
            evidence="sveltekit filesystem route convention",
        ),
        None,
    )


def _detect_framework_route(file_node: FileNode) -> tuple[RouteNode | None, list[SkippedFile]]:
    skipped: list[SkippedFile] = []
    for detector in (_next_app_route, _next_pages_route, _sveltekit_route):
        route, skipped_file = detector(file_node)
        if skipped_file is not None:
            skipped.append(skipped_file)
        if route is not None:
            return route, skipped
    return None, skipped


def extract_routes(root: str | Path, files: list[FileNode]) -> tuple[list[RouteNode], list[UnresolvedItem], list[SkippedFile]]:
    route_nodes: list[RouteNode] = []
    unresolved: list[UnresolvedItem] = []
    skipped_files: list[SkippedFile] = []
    seen: set[tuple[str, str, str, int | None]] = set()

    for file_node in files:
        framework_route, framework_skips = _detect_framework_route(file_node)
        skipped_files.extend(framework_skips)

        if framework_route:
            key = (framework_route.source, framework_route.route, framework_route.kind, framework_route.line)
            if key not in seen:
                seen.add(key)
                route_nodes.append(framework_route)
        elif framework_skips:
            continue

        if not file_node.is_text:
            skipped_files.append(SkippedFile(path=file_node.path, stage="route-scan", reason="non-text-file"))
            continue
        if file_node.extension not in ROUTE_SCAN_EXTENSIONS:
            skipped_files.append(
                SkippedFile(path=file_node.path, stage="route-scan", reason="unsupported-text-format", detail=file_node.extension or "<none>")
            )
            continue

        content = read_text(root, file_node.path)
        for line_number, line in enumerate(content.splitlines(), start=1):
            for pattern, kind in ROUTE_PATTERNS:
                match = pattern.search(line)
                if not match:
                    continue

                method = None
                route = None
                if pattern.pattern.startswith(r"\."):
                    method = match.group(1).upper()
                    route = match.group(2)
                elif "@(" in pattern.pattern:
                    method = match.group(2).upper()
                    route = match.group(3)
                elif "Http" in pattern.pattern:
                    method = match.group(1).replace("Http", "").upper()
                    route = match.group(2) or "/"
                else:
                    route = match.group(1)

                key = (file_node.path, route, kind, line_number)
                if key in seen:
                    continue

                seen.add(key)
                route_nodes.append(
                    RouteNode(
                        source=file_node.path,
                        route=route,
                        kind=kind,
                        method=method,
                        line=line_number,
                        evidence=line.strip(),
                    )
                )

    return (
        sorted(route_nodes, key=lambda node: (node.source, node.route, node.kind, node.line or 0)),
        unresolved,
        sorted(skipped_files, key=lambda item: (item.path, item.stage, item.reason, item.detail or "")),
    )