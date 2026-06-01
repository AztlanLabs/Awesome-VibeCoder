from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(slots=True)
class FileNode:
    path: str
    directory: str
    name: str
    stem: str
    extension: str
    suffixes: list[str]
    size: int
    is_text: bool
    is_entrypoint: bool
    is_config: bool
    language: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class DirectoryNode:
    path: str
    file_count: int
    direct_file_count: int
    total_size: int
    entrypoint_count: int
    config_count: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class RouteNode:
    source: str
    route: str
    kind: str
    method: str | None = None
    line: int | None = None
    evidence: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class ReferenceEdge:
    source: str
    target: str
    kind: str
    line: int | None = None
    evidence: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class LinkedFileEdge:
    left: str
    right: str
    rule: str
    evidence: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class ScoreNode:
    path: str
    score: float
    reasons: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class UnresolvedItem:
    source: str
    stage: str
    value: str
    reason: str
    line: int | None = None
    evidence: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class SkippedFile:
    path: str
    stage: str
    reason: str
    detail: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)