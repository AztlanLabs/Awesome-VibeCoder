from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from .models import DirectoryNode, FileNode, LinkedFileEdge, ReferenceEdge, RouteNode, ScoreNode


def _directory_for(path: str) -> str:
    return path.rsplit("/", 1)[0] if "/" in path else "."


def _ancestor_directories(path: str, known_directories: set[str]) -> list[str]:
    current = Path(_directory_for(path))
    ancestors: list[str] = []

    while True:
        key = current.as_posix() if str(current) != "." else "."
        if key in known_directories:
            ancestors.append(key)
        if key == ".":
            break
        current = current.parent

    return ancestors


def compute_file_scores(
    files: list[FileNode],
    routes: list[RouteNode],
    references: list[ReferenceEdge],
    linked_files: list[LinkedFileEdge],
) -> list[ScoreNode]:
    inbound = Counter(edge.target for edge in references)
    outbound = Counter(edge.source for edge in references)
    route_count = Counter(route.source for route in routes)
    companion_count: Counter[str] = Counter()

    for edge in linked_files:
        companion_count[edge.left] += 1
        companion_count[edge.right] += 1

    scores: list[ScoreNode] = []
    for file_node in files:
        reasons: dict[str, float] = {}
        if file_node.is_entrypoint:
            reasons["entrypoint"] = 8.0
        if file_node.is_config:
            reasons["config"] = 2.0
        if route_count[file_node.path]:
            reasons["routes"] = min(route_count[file_node.path] * 4.0, 16.0)
        if inbound[file_node.path]:
            reasons["inbound_references"] = min(inbound[file_node.path] * 1.5, 12.0)
        if outbound[file_node.path]:
            reasons["outbound_references"] = min(outbound[file_node.path] * 0.75, 8.0)
        if companion_count[file_node.path]:
            reasons["companion_links"] = companion_count[file_node.path] * 1.5
        if file_node.directory.count("/") <= 1:
            reasons["top_level_visibility"] = 1.0

        scores.append(
            ScoreNode(
                path=file_node.path,
                score=round(sum(reasons.values()), 2),
                reasons=reasons,
            )
        )

    return sorted(scores, key=lambda node: (-node.score, node.path))


def compute_path_scores(
    directories: list[DirectoryNode],
    routes: list[RouteNode],
    references: list[ReferenceEdge],
    linked_files: list[LinkedFileEdge],
) -> list[ScoreNode]:
    aggregate: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    known_directories = {directory.path for directory in directories}
    route_count: Counter[str] = Counter()
    inbound_references: Counter[str] = Counter()
    outbound_references: Counter[str] = Counter()
    linkage_centrality: Counter[str] = Counter()

    for route in routes:
        for directory in _ancestor_directories(route.source, known_directories):
            route_count[directory] += 1

    for edge in references:
        for directory in _ancestor_directories(edge.target, known_directories):
            inbound_references[directory] += 1
        for directory in _ancestor_directories(edge.source, known_directories):
            outbound_references[directory] += 1

    for edge in linked_files:
        for directory in _ancestor_directories(edge.left, known_directories):
            linkage_centrality[directory] += 1
        for directory in _ancestor_directories(edge.right, known_directories):
            linkage_centrality[directory] += 1

    for directory in directories:
        aggregate[directory.path]["file_volume"] = min(directory.file_count * 0.25, 10.0)
        aggregate[directory.path]["entrypoints"] = directory.entrypoint_count * 3.0
        aggregate[directory.path]["configs"] = directory.config_count * 1.0
        if route_count[directory.path]:
            aggregate[directory.path]["route_ownership"] = min(route_count[directory.path] * 2.5, 15.0)
        if inbound_references[directory.path]:
            aggregate[directory.path]["inbound_references"] = min(inbound_references[directory.path] * 1.25, 10.0)
        if outbound_references[directory.path]:
            aggregate[directory.path]["outbound_references"] = min(outbound_references[directory.path] * 0.75, 8.0)
        if linkage_centrality[directory.path]:
            aggregate[directory.path]["linked_files"] = min(linkage_centrality[directory.path] * 1.5, 12.0)

    results = [
        ScoreNode(path=path, score=round(sum(reasons.values()), 2), reasons=dict(reasons))
        for path, reasons in aggregate.items()
    ]
    return sorted(results, key=lambda node: (-node.score, node.path))