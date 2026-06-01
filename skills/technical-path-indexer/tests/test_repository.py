from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from python.repository import discover_files


class RepositoryTests(unittest.TestCase):
    def test_marks_mjs_and_cjs_files_as_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "main.mjs").write_text("export const main = true;", encoding="utf-8")
            (root / "util.cjs").write_text("module.exports = {};", encoding="utf-8")

            files = {file_node.path: file_node for file_node in discover_files(root)}

            self.assertTrue(files["main.mjs"].is_text)
            self.assertTrue(files["util.cjs"].is_text)

    def test_ignores_default_noise_and_gitignore_matches(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / ".gitignore").write_text("reports/\n*.tmp\nplugins/*/agents/\n", encoding="utf-8")
            (root / ".github").mkdir()
            (root / ".github" / "ignored.md").write_text("x", encoding="utf-8")
            (root / "reports").mkdir()
            (root / "reports" / "ignored.md").write_text("x", encoding="utf-8")
            (root / "plugins" / "sample" / "agents").mkdir(parents=True)
            (root / "plugins" / "sample" / "agents" / "ignored.agent.md").write_text("x", encoding="utf-8")
            (root / "scratch.tmp").write_text("x", encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / "keep.ts").write_text("export const keep = true;", encoding="utf-8")

            files = {file_node.path for file_node in discover_files(root)}

            self.assertIn("src/keep.ts", files)
            self.assertNotIn(".github/ignored.md", files)
            self.assertNotIn("reports/ignored.md", files)
            self.assertNotIn("plugins/sample/agents/ignored.agent.md", files)
            self.assertNotIn("scratch.tmp", files)


if __name__ == "__main__":
    unittest.main()