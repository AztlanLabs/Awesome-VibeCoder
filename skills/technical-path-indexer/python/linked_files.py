from __future__ import annotations

from pathlib import Path

from .models import FileNode, LinkedFileEdge

SCRIPT_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx"}
STYLE_EXTENSIONS = {".css", ".scss", ".less"}
MARKUP_EXTENSIONS = {".html", ".aspx", ".razor", ".xaml", ".axaml"}


def _add_link(
    links: list[LinkedFileEdge],
    seen: set[tuple[str, str, str]],
    left: str,
    right: str,
    rule: str,
    evidence: str,
) -> None:
    ordered = tuple(sorted((left, right)))
    key = (ordered[0], ordered[1], rule)
    if key in seen or left == right:
        return
    seen.add(key)
    links.append(LinkedFileEdge(left=ordered[0], right=ordered[1], rule=rule, evidence=evidence))


def detect_linked_files(files: list[FileNode]) -> list[LinkedFileEdge]:
    lookup = {file_node.path for file_node in files}
    links: list[LinkedFileEdge] = []
    seen: set[tuple[str, str, str]] = set()

    for file_node in files:
        path = Path(file_node.path)
        path_str = path.as_posix()
        stem_base = path.with_suffix("")

        if file_node.extension == ".aspx":
            for suffix in [".cs", ".vb"]:
                candidate = f"{path_str}{suffix}"
                if candidate in lookup:
                    _add_link(links, seen, path_str, candidate, "aspx-codebehind", "explicit aspx/code-behind rule")
            designer = f"{stem_base.as_posix()}.designer.cs"
            if designer in lookup:
                _add_link(links, seen, path_str, designer, "aspx-designer", "explicit aspx/designer rule")

        if file_node.extension in {".xaml", ".axaml"}:
            for suffix in [".cs", ".vb"]:
                candidate = f"{path_str}{suffix}"
                if candidate in lookup:
                    _add_link(links, seen, path_str, candidate, "markup-codebehind", "explicit xaml or axaml code-behind rule")

        if file_node.extension == ".razor":
            for suffix in [".cs", ".css"]:
                candidate = f"{path_str}{suffix}"
                if candidate in lookup:
                    _add_link(links, seen, path_str, candidate, "razor-companion", "explicit razor companion rule")

        if file_node.extension in SCRIPT_EXTENSIONS:
            for extension in STYLE_EXTENSIONS | MARKUP_EXTENSIONS:
                candidate = stem_base.with_suffix(extension).as_posix()
                if candidate in lookup:
                    _add_link(links, seen, path_str, candidate, "same-stem-script-companion", "same-stem script companion rule")

            for prefix in ["test", "spec", "stories"]:
                candidate = path.with_name(f"{stem_base.name}.{prefix}{file_node.extension}").as_posix()
                if candidate in lookup:
                    _add_link(links, seen, path_str, candidate, "script-test-companion", "same-stem test, spec, or story rule")

        if file_node.name == "package.json":
            for sibling in ["package-lock.json", "pnpm-lock.yaml", "yarn.lock"]:
                candidate = path.with_name(sibling).as_posix()
                if candidate in lookup:
                    _add_link(links, seen, path_str, candidate, "package-lock-companion", "package manifest to lockfile rule")

        if file_node.name == "Dockerfile":
            for sibling in ["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"]:
                candidate = path.with_name(sibling).as_posix()
                if candidate in lookup:
                    _add_link(links, seen, path_str, candidate, "docker-compose-companion", "Docker runtime configuration rule")

        if file_node.name in {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}:
            dockerfile = path.with_name("Dockerfile").as_posix()
            if dockerfile in lookup:
                _add_link(links, seen, path_str, dockerfile, "docker-compose-companion", "Docker runtime configuration rule")

    return sorted(links, key=lambda edge: (edge.left, edge.right, edge.rule))