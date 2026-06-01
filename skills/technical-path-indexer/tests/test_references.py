from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from python.references import extract_references
from python.repository import discover_files


class ReferenceTests(unittest.TestCase):
    def test_reports_unresolved_local_references_without_flagging_package_imports(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir(parents=True)
            (root / "src" / "util.ts").write_text("export const util = true;", encoding="utf-8")
            (root / "src" / "main.ts").write_text(
                "\n".join(
                    [
                        'import { util } from "./util";',
                        'import { missing } from "./missing";',
                        'import React from "react";',
                    ]
                ),
                encoding="utf-8",
            )

            files = discover_files(root)
            references, unresolved, skipped = extract_references(root, files)

            self.assertFalse(skipped)
            resolved_targets = {(edge.source, edge.target) for edge in references}
            self.assertIn(("src/main.ts", "src/util.ts"), resolved_targets)

            unresolved_values = {item.value for item in unresolved}
            self.assertIn("./missing", unresolved_values)
            self.assertNotIn("react", unresolved_values)

    def test_skips_external_markdown_links_and_path_literal_noise(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "docs").mkdir(parents=True)
            (root / "docs" / "guide.md").write_text(
                "\n".join(
                    [
                        "[badge](//img.shields.io/test)",
                        "See ./missing.agent.md for more details.",
                        "See ./missing.agent.md for more details.",
                    ]
                ),
                encoding="utf-8",
            )

            files = discover_files(root)
            references, unresolved, skipped = extract_references(root, files)

            self.assertFalse(references)
            self.assertFalse(skipped)
            self.assertFalse(unresolved)

    def test_suppresses_unresolved_markdown_links_but_keeps_code_imports(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "docs").mkdir(parents=True)
            (root / "src").mkdir(parents=True)
            (root / "docs" / "guide.md").write_text("[missing](./missing.md)", encoding="utf-8")
            (root / "src" / "main.ts").write_text('import helper from "./missing";', encoding="utf-8")

            files = discover_files(root)
            references, unresolved, skipped = extract_references(root, files)

            self.assertFalse(references)
            self.assertFalse(skipped)
            self.assertEqual(["./missing"], [item.value for item in unresolved])


if __name__ == "__main__":
    unittest.main()