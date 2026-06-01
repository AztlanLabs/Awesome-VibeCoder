from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from fnmatch import fnmatch
import os
from pathlib import Path

from .models import DirectoryNode, FileNode

DEFAULT_IGNORED_DIRS = {
    ".cache",
    ".git",
    ".github",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".svn",
    ".tox",
    ".turbo",
    ".vs",
    ".vscode",
    ".idea",
    ".next",
    ".nuxt",
    ".venv",
    "__pycache__",
    "bin",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "obj",
    "out",
    "target",
    "venv",
    "vendor",
    "virtualenv",
    "virtualenvs",
}

DEFAULT_IGNORED_FILE_PATTERNS = {
    ".DS_Store",
    "Thumbs.db",
    "*.log",
    "*.tmp",
    "*.bak",
    "*.swp",
    ".gitattributes",
    ".gitignore",
    ".prettierignore",
    ".eslintignore",
    ".dockerignore",
    ".editorconfig",
}

SPECIAL_COMPOUND_SUFFIXES = {
    ".aspx.cs",
    ".aspx.vb",
    ".designer.cs",
    ".razor.cs",
    ".razor.css",
    ".xaml.cs",
    ".xaml.vb",
    ".axaml.cs",
    ".axaml.vb",
    ".agent.md",
    ".prompt.md",
    ".instructions.md",
}

LANGUAGE_BY_EXTENSION = {
    ".agent.md": "markdown",
    ".aspx": "markup",
    ".axaml": "markup",
    ".bat": "shell",
    ".c": "c",
    ".cjs": "javascript",
    ".cc": "cpp",
    ".cpp": "cpp",
    ".cs": "csharp",
    ".css": "css",
    ".go": "go",
    ".h": "c",
    ".hpp": "cpp",
    ".html": "html",
    ".ini": "config",
    ".java": "java",
    ".js": "javascript",
    ".json": "json",
    ".jsx": "javascript",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".less": "css",
    ".md": "markdown",
    ".mjs": "javascript",
    ".prompt.md": "markdown",
    ".ps1": "powershell",
    ".py": "python",
    ".qmd": "markdown",
    ".razor": "markup",
    ".rb": "ruby",
    ".rs": "rust",
    ".scss": "css",
    ".sh": "shell",
    ".SKILL.md": "markdown",
    ".sql": "sql",
    ".svg": "svg",
    ".swift": "swift",
    ".toml": "config",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".txt": "text",
    ".xml": "xml",
    ".xaml": "markup",
    ".yaml": "yaml",
    ".yml": "yaml",
}

ENTRYPOINT_NAMES = {
    "__main__.py",
    "Cargo.toml",
    "cli.py",
    "Dockerfile",
    "main.go",
    "main.js",
    "main.py",
    "main.ts",
    "manage.py",
    "package.json",
    "pom.xml",
    "Program.cs",
    "pyproject.toml",
    "server.js",
    "server.py",
    "server.ts",
    "vite.config.js",
    "vite.config.ts",
}

CONFIG_EXTENSIONS = {
    ".config",
    ".ini",
    ".json",
    ".props",
    ".settings",
    ".toml",
    ".xml",
    ".yaml",
    ".yml",
}

TEXT_EXTENSIONS = {
    ".agent.md",
    ".aspx",
    ".axaml",
    ".bat",
    ".c",
    ".cjs",
    ".cc",
    ".cpp",
    ".cs",
    ".css",
    ".go",
    ".h",
    ".hpp",
    ".html",
    ".ini",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".kt",
    ".kts",
    ".less",
    ".md",
    ".mjs",
    ".prompt.md",
    ".ps1",
    ".py",
    ".qmd",
    ".razor",
    ".rb",
    ".rs",
    ".scss",
    ".sh",
    ".sql",
    ".svg",
    ".swift",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".xml",
    ".xaml",
    ".yaml",
    ".yml",
}


@dataclass(frozen=True, slots=True)
class IgnorePattern:
    value: str
    anchored: bool
    directory_only: bool
    basename_only: bool


def load_ignore_patterns(root: str | Path) -> list[IgnorePattern]:
    gitignore_path = Path(root) / ".gitignore"
    if not gitignore_path.is_file():
        return []

    patterns: list[IgnorePattern] = []
    for raw_line in gitignore_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("!"):
            continue

        directory_only = line.endswith("/")
        anchored = line.startswith("/")
        normalized = line.strip("/")
        if not normalized:
            continue

        patterns.append(
            IgnorePattern(
                value=normalized,
                anchored=anchored,
                directory_only=directory_only,
                basename_only="/" not in normalized,
            )
        )

    return patterns


def _matches_ignore_pattern(pattern: IgnorePattern, relative_path: str, is_dir: bool) -> bool:
    if pattern.directory_only and not is_dir:
        return False

    if pattern.anchored:
        if fnmatch(relative_path, pattern.value):
            return True
        return pattern.directory_only and (
            relative_path == pattern.value or relative_path.startswith(f"{pattern.value}/")
        )

    path_parts = relative_path.split("/")
    if pattern.basename_only:
        return any(fnmatch(part, pattern.value) for part in path_parts)

    for index in range(len(path_parts)):
        suffix = "/".join(path_parts[index:])
        if fnmatch(suffix, pattern.value):
            return True
        if pattern.directory_only and (suffix == pattern.value or suffix.startswith(f"{pattern.value}/")):
            return True
    return False


def should_ignore_path(relative_path: str, is_dir: bool, ignore_patterns: list[IgnorePattern]) -> bool:
    normalized = Path(relative_path).as_posix().strip("/")
    if not normalized or normalized == ".":
        return False

    path_obj = Path(normalized)
    if any(part in DEFAULT_IGNORED_DIRS for part in path_obj.parts):
        return True

    if not is_dir and any(fnmatch(path_obj.name, pattern) for pattern in DEFAULT_IGNORED_FILE_PATTERNS):
        return True

    return any(_matches_ignore_pattern(pattern, normalized, is_dir) for pattern in ignore_patterns)


def normalize_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def compound_extension(path: Path) -> str:
    suffixes = path.suffixes
    if len(suffixes) >= 2:
        candidate = "".join(suffixes[-2:])
        if candidate in SPECIAL_COMPOUND_SUFFIXES:
            return candidate
    if suffixes:
        return suffixes[-1]
    return ""


def classify_language(path: Path) -> str | None:
    name = path.name
    if name.endswith(".agent.md"):
        return "markdown"
    if name.endswith(".prompt.md"):
        return "markdown"
    extension = compound_extension(path)
    return LANGUAGE_BY_EXTENSION.get(extension) or LANGUAGE_BY_EXTENSION.get(path.suffix)


def is_text_file(path: Path) -> bool:
    extension = compound_extension(path)
    if extension in TEXT_EXTENSIONS or path.suffix in TEXT_EXTENSIONS:
        return True
    if not path.suffix:
        return path.name in {"Dockerfile", "Makefile", "LICENSE", "README"}
    return False


def is_entrypoint_file(path: Path) -> bool:
    if path.name in ENTRYPOINT_NAMES:
        return True
    parts = set(path.parts)
    if path.stem in {"index", "main", "app", "server"} and parts & {"pages", "routes", "api", "app"}:
        return True
    return False


def is_config_file(path: Path) -> bool:
    if path.name in {"Dockerfile", "package.json", "pyproject.toml"}:
        return True
    return compound_extension(path) in CONFIG_EXTENSIONS or path.suffix in CONFIG_EXTENSIONS


def discover_files(root: str | Path) -> list[FileNode]:
    root_path = Path(root).resolve()
    file_nodes: list[FileNode] = []
    ignore_patterns = load_ignore_patterns(root_path)

    for directory, dirs, files in os.walk(root_path, topdown=True):
        directory_path = Path(directory)
        if directory_path != root_path:
            directory_relative = normalize_path(directory_path, root_path)
            if should_ignore_path(directory_relative, is_dir=True, ignore_patterns=ignore_patterns):
                dirs[:] = []
                continue

        filtered_dirs: list[str] = []
        for name in dirs:
            relative_dir = normalize_path(directory_path / name, root_path)
            if should_ignore_path(relative_dir, is_dir=True, ignore_patterns=ignore_patterns):
                continue
            filtered_dirs.append(name)
        dirs[:] = filtered_dirs

        for file_name in files:
            file_path = directory_path / file_name
            relative_path = normalize_path(file_path, root_path)
            if should_ignore_path(relative_path, is_dir=False, ignore_patterns=ignore_patterns):
                continue
            extension = compound_extension(file_path)
            file_nodes.append(
                FileNode(
                    path=relative_path,
                    directory=normalize_path(directory_path, root_path) if directory_path != root_path else ".",
                    name=file_path.name,
                    stem=file_path.stem,
                    extension=extension,
                    suffixes=file_path.suffixes,
                    size=file_path.stat().st_size,
                    is_text=is_text_file(file_path),
                    is_entrypoint=is_entrypoint_file(file_path),
                    is_config=is_config_file(file_path),
                    language=classify_language(file_path),
                )
            )

    return sorted(file_nodes, key=lambda node: node.path)


def build_directory_index(files: list[FileNode]) -> list[DirectoryNode]:
    counters: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for file_node in files:
        current = Path(file_node.directory)
        while True:
            key = current.as_posix() if str(current) != "." else "."
            counters[key]["file_count"] += 1
            counters[key]["total_size"] += file_node.size
            counters[key]["entrypoint_count"] += int(file_node.is_entrypoint)
            counters[key]["config_count"] += int(file_node.is_config)
            if key == file_node.directory:
                counters[key]["direct_file_count"] += 1
            if key == ".":
                break
            current = current.parent

    directories = [
        DirectoryNode(
            path=path,
            file_count=data["file_count"],
            direct_file_count=data["direct_file_count"],
            total_size=data["total_size"],
            entrypoint_count=data["entrypoint_count"],
            config_count=data["config_count"],
        )
        for path, data in counters.items()
    ]
    return sorted(directories, key=lambda node: node.path)


def read_text(root: str | Path, relative_path: str) -> str:
    file_path = Path(root, relative_path)
    return file_path.read_text(encoding="utf-8", errors="ignore")


def filter_files(files: list[FileNode], scope_paths: list[str] | None = None) -> list[FileNode]:
    if not scope_paths:
        return files

    normalized_scopes: list[str] = []
    for scope_path in scope_paths:
        normalized = Path(scope_path).as_posix().strip()
        if normalized in {"", "."}:
            return files
        normalized_scopes.append(normalized.strip("/"))

    filtered: list[FileNode] = []
    for file_node in files:
        for scope_path in normalized_scopes:
            if file_node.path == scope_path or file_node.path.startswith(f"{scope_path}/"):
                filtered.append(file_node)
                break

    return filtered