from __future__ import annotations

import argparse
import json
import os
import re
from collections import defaultdict


VALID_EXTENSIONS = (
    ".py",
    ".js",
    ".ts",
    ".java",
    ".cpp",
    ".c",
    ".cs",
    ".php",
    ".go",
    ".rs",
)

IGNORED_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
}

LANGUAGE_BY_EXTENSION = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
    ".cs": "csharp",
    ".php": "php",
    ".go": "go",
    ".rs": "rust",
}

CONTROL_KEYWORDS = {"if", "while", "for", "switch", "catch"}


class UniversalCodeAnalyzer:
    """Extract a compact, language-agnostic structure map from a source file."""

    library_patterns = (
        r"^\s*import\s+([a-zA-Z0-9_\.]+)",
        r"^\s*from\s+([a-zA-Z0-9_\.]+)\s+import",
        r"^\s*#include\s*[<\"]([^>\"]+)[>\"]",
        r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
        r"^\s*using\s+([a-zA-Z0-9_\.]+)\s*;",
        r"^\s*import\s+.*?\s+from\s+['\"]([^'\"]+)['\"]",
    )

    class_patterns = (
        r"^\s*(public|private|protected|export)?\s*(class|struct|interface)\s+([a-zA-Z0-9_]+)",
        r"^\s*(public|private|protected)?\s*(enum)\s+([a-zA-Z0-9_]+)",
    )

    keyword_function_pattern = re.compile(
        r"^\s*(export|public|private|protected|async)?\s*(def|function|func|fn)\s+([a-zA-Z0-9_]+)\s*\(",
        re.MULTILINE,
    )

    c_style_function_pattern = re.compile(
        r"^\s*(public|private|protected)?\s*(?:static\s+)?([a-zA-Z0-9_<>\[\]]+)\s+([a-zA-Z0-9_]+)\s*\([^)]*\)\s*[{;]",
        re.MULTILINE,
    )

    assignment_function_pattern = re.compile(
        r"^\s*(?:export\s+)?(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>",
        re.MULTILINE,
    )

    file_link_patterns = (
        r"['\"](\./[^'\"]+)['\"]",
        r"['\"](\.\./[^'\"]+)['\"]",
        r"include(?:_once)?\s*[('\"]+([^'\")]+)",
        r"^\s*import\s+.*?\s+from\s+['\"](\.[^'\"]+)['\"]",
        r"^\s*from\s+['\"](\.[^'\"]+)['\"]",
    )

    def __init__(self, file_path: str) -> None:
        self.file_path = os.path.abspath(file_path)
        self.file_extension = os.path.splitext(file_path)[1].lower()
        self.code = ""
        self.read_error = None

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as handle:
                self.code = handle.read()
        except OSError as error:
            self.read_error = str(error)

    def extract_libraries(self) -> list[str]:
        """Extract imported libraries, modules, or dependencies."""
        libraries = set()

        for pattern in self.library_patterns:
            libraries.update(re.findall(pattern, self.code, re.MULTILINE))

        return sorted(item for item in libraries if item)

    def extract_classes_and_objects(self) -> list[dict[str, str]]:
        """Extract class-like definitions across common languages."""
        objects = []
        seen = set()

        for pattern in self.class_patterns:
            matches = re.findall(pattern, self.code, re.MULTILINE)
            for visibility, object_type, name in matches:
                record = {
                    "name": name,
                    "type": object_type,
                    "visibility": visibility or "default",
                }
                key = (record["name"], record["type"], record["visibility"])
                if key not in seen:
                    seen.add(key)
                    objects.append(record)

        return sorted(objects, key=lambda item: (item["name"], item["type"]))

    def extract_functions(self) -> list[dict[str, str]]:
        """Extract function and method definitions with visibility when available."""
        functions = []
        seen = set()

        for modifier, keyword, name in self.keyword_function_pattern.findall(self.code):
            visibility = modifier if modifier in {"public", "private", "protected"} else "default"
            if keyword == "def" and name.startswith("_"):
                visibility = "private"

            record = {
                "name": name,
                "visibility": visibility,
                "kind": keyword,
            }
            key = (record["name"], record["visibility"], record["kind"])
            if key not in seen:
                seen.add(key)
                functions.append(record)

        for visibility, return_type, name in self.c_style_function_pattern.findall(self.code):
            if name in CONTROL_KEYWORDS:
                continue

            record = {
                "name": name,
                "visibility": visibility or "default",
                "return_type": return_type,
                "kind": "c_style",
            }
            key = (record["name"], record["visibility"], record["kind"])
            if key not in seen:
                seen.add(key)
                functions.append(record)

        for name in self.assignment_function_pattern.findall(self.code):
            record = {
                "name": name,
                "visibility": "default",
                "kind": "assignment",
            }
            key = (record["name"], record["visibility"], record["kind"])
            if key not in seen:
                seen.add(key)
                functions.append(record)

        return sorted(functions, key=lambda item: item["name"])

    def extract_file_links(self) -> list[str]:
        """Find local relative path references that point to nearby files or modules."""
        links = set()

        for pattern in self.file_link_patterns:
            for match in re.finditer(pattern, self.code, re.MULTILINE):
                groups = [group for group in match.groups() if group]
                if groups:
                    links.add(groups[-1].replace("\\", "/"))

        return sorted(links)

    def analyze(self) -> dict[str, object]:
        """Compile extracted metadata into a deterministic structure."""
        return {
            "file": self.file_path,
            "extension": self.file_extension,
            "language": LANGUAGE_BY_EXTENSION.get(self.file_extension, "unknown"),
            "libraries_used": self.extract_libraries(),
            "classes_objects": self.extract_classes_and_objects(),
            "functions_methods": self.extract_functions(),
            "linked_files": self.extract_file_links(),
            "read_error": self.read_error,
        }


def _normalize_path(path: str) -> str:
    normalized = path.replace(os.sep, "/")
    return "." if normalized == "." else normalized.strip("/")


def map_repository(directory_path: str, output_file: str = "repo_map.json") -> dict[str, object]:
    """Scan a directory and create a JSON map of code-bearing files and directories."""
    repository_root = os.path.abspath(directory_path)
    if not os.path.isdir(repository_root):
        raise ValueError(f"Directory does not exist: {directory_path}")

    repo_map: dict[str, object] = {
        "root": repository_root,
        "directories": {},
        "files": {},
    }

    directory_summary: dict[str, dict[str, object]] = defaultdict(
        lambda: {
            "files": [],
            "subdirectories": set(),
            "extensions": set(),
            "languages": set(),
        }
    )

    for root, directories, files in os.walk(repository_root):
        directories[:] = sorted(
            directory for directory in directories if directory not in IGNORED_DIRECTORIES
        )

        relative_root = _normalize_path(os.path.relpath(root, repository_root))
        current_directory = directory_summary[relative_root]
        current_directory["subdirectories"].update(directories)

        for file_name in sorted(files):
            if not file_name.endswith(VALID_EXTENSIONS):
                continue

            full_path = os.path.join(root, file_name)
            relative_path = _normalize_path(os.path.relpath(full_path, repository_root))
            analyzer = UniversalCodeAnalyzer(full_path)
            analyzed_data = analyzer.analyze()

            current_directory["files"].append(relative_path)
            current_directory["extensions"].add(analyzed_data["extension"])
            current_directory["languages"].add(analyzed_data["language"])

            has_useful_data = any(
                [
                    analyzed_data["libraries_used"],
                    analyzed_data["classes_objects"],
                    analyzed_data["functions_methods"],
                    analyzed_data["linked_files"],
                    analyzed_data["read_error"],
                ]
            )

            if has_useful_data:
                repo_map["files"][relative_path] = analyzed_data

    repo_map["directories"] = {
        path: {
            "file_count": len(summary["files"]),
            "files": summary["files"],
            "subdirectories": sorted(summary["subdirectories"]),
            "extensions": sorted(summary["extensions"]),
            "languages": sorted(
                language for language in summary["languages"] if language != "unknown"
            ),
        }
        for path, summary in sorted(directory_summary.items())
        if summary["files"] or summary["subdirectories"]
    }

    with open(output_file, "w", encoding="utf-8") as handle:
        json.dump(repo_map, handle, indent=2)

    return repo_map


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a repository code map for targeted AI-assisted code reading."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Path to the project directory to map.",
    )
    parser.add_argument(
        "--output",
        default="repo_map.json",
        help="Output JSON file name.",
    )

    args = parser.parse_args()
    map_repository(args.directory, args.output)
    print(f"Successfully mapped repository to {args.output}")


if __name__ == "__main__":
    main()