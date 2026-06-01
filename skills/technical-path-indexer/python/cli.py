from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def _load_build_index():
    package_dir = Path(__file__).resolve().parent
    init_path = package_dir / "__init__.py"
    spec = importlib.util.spec_from_file_location(
        "technical_path_indexer_python",
        init_path,
        submodule_search_locations=[str(package_dir)],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load technical path indexer package.")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.build_index


if __package__ in {None, ""}:
    build_index = _load_build_index()
else:
    from .pipeline import build_index


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Emit a repository technical path index as JSON.")
    parser.add_argument("root", nargs="?", default=".", help="Repository root to index")
    parser.add_argument("--output", "-o", help="Optional file path for JSON output")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    parser.add_argument("--compact", action="store_true", help="Emit a smaller JSON payload by omitting reference evidence fields")
    parser.add_argument("--scope", action="append", default=[], help="Optional scoped path to index. Repeat to add more than one path.")
    parser.add_argument("--batch-size", type=int, help="Optional file count per emitted batch.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    index = build_index(args.root, scope_paths=args.scope or None, batch_size=args.batch_size, compact=args.compact)
    indent = 2 if args.pretty else None
    payload = json.dumps(index, indent=indent, sort_keys=bool(args.pretty))

    if args.output:
        Path(args.output).write_text(payload + ("\n" if args.pretty else ""), encoding="utf-8")
    else:
        print(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())